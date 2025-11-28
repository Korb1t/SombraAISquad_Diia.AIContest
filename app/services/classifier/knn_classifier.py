from typing import Tuple
from collections import Counter
import math
from sqlmodel import Session, select

from app.core.config import settings
from app.db_models import Example
from app.llm.client import get_embeddings
from app.services.classifier.base_classifier import BaseClassifier

class KNNClassifier(BaseClassifier):
    """
    Math-based classifier using Vector Voting.
    Performs simultaneous multi-label classification for category and urgency.
    """

    def __init__(self, session: Session):
        super().__init__(session)
        self.embeddings = get_embeddings()

    MAX_COSINE_DISTANCE = 2.0
    EPSILON = 1e-9

    def _get_nearest_neighbors(self, query_embedding, k: int) -> list[Example]:
        """
        Finds the K nearest neighbors based on cosine distance.
        """
        statement = (
            select(Example)
            .order_by(Example.embedding.cosine_distance(query_embedding))
            .limit(k)
        )

        return self.session.exec(statement).all()

    def _cosine_distance(self, vec_a: list[float], vec_b: list[float]) -> float:
        """
        Compute cosine distance between two vectors (1 - cosine similarity).
        Falls back to max distance when a zero vector is encountered.
        """
        norm_a = math.sqrt(sum(x * x for x in vec_a))
        norm_b = math.sqrt(sum(x * x for x in vec_b))
        if norm_a < self.EPSILON or norm_b < self.EPSILON:
            return self.MAX_COSINE_DISTANCE

        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        similarity = dot_product / (norm_a * norm_b)
        # Clamp similarity to avoid floating point artifacts outside [-1, 1].
        similarity = max(-1.0, min(1.0, similarity))
        return 1 - similarity

    def _prepare_neighbor_distances(
        self, query_embedding: list[float], neighbors: list[Example]
    ) -> list[tuple[Example, float]]:
        """
        Attach cosine distances to each neighbor so we can reason about confidence.
        """
        return [
            (neighbor, self._cosine_distance(query_embedding, neighbor.embedding))
            for neighbor in neighbors
        ]

    def _distance_confidence(
        self, winner_distances: list[float], competitor_distances: list[float]
    ) -> tuple[float, float | None, float | None]:
        """
        Estimate how separated the winning label is from the closest competitor.
        Returns (confidence_component, closest_winner, closest_competitor).
        """
        if not winner_distances:
            return 0.0, None, None

        closest_winner = min(winner_distances)

        if not competitor_distances:
            # No competitor → rely on absolute distance (smaller distance => higher confidence).
            absolute_component = max(
                0.0, 1 - (closest_winner / self.MAX_COSINE_DISTANCE)
            )
            return absolute_component, closest_winner, None

        closest_competitor = min(competitor_distances)
        if closest_competitor < self.EPSILON:
            return 0.0, closest_winner, closest_competitor

        relative_gap = max(0.0, closest_competitor - closest_winner)
        distance_component = min(
            1.0, relative_gap / (closest_competitor + self.EPSILON)
        )
        return distance_component, closest_winner, closest_competitor

    def _blend_confidence(self, vote_component: float, distance_component: float) -> float:
        """
        Blend classic majority voting confidence with the distance-based separation metric.
        """
        blended = 0.5 * vote_component + 0.5 * distance_component
        return max(0.0, min(1.0, blended))

    def classify(self, problem_text: str) -> Tuple[str, float, str, bool]:
        """
        Classify the problem by category and determine its urgency (is_urgent).
        
        Returns:
            Tuple[category_id, confidence, reasoning, is_urgent, is_relevant]
        """
        k_neighbors = settings.TOP_K 
        query_embedding = self.embeddings.embed_query(problem_text)

        # 1. FIND NEIGHBORS FOR CATEGORY (Use ALL data)
        # Category uses all available data
        neighbors_category = self._get_nearest_neighbors(query_embedding, k_neighbors)
        
        if not neighbors_category:
            return "other", 0.0, "No historical examples found for category classification.", False

        # --- A. VOTING FOR CATEGORY (Multi-Class) ---
        votes_cat = [ex.category_id for ex in neighbors_category]
        vote_counts_cat = Counter(votes_cat)
        winner_cat, count_cat = vote_counts_cat.most_common(1)[0]
        neighbor_distances_cat = self._prepare_neighbor_distances(
            query_embedding, neighbors_category
        )
        winner_distance_values = [
            dist for example, dist in neighbor_distances_cat if example.category_id == winner_cat
        ]
        competitor_distance_values = [
            dist for example, dist in neighbor_distances_cat if example.category_id != winner_cat
        ]
        distance_component_cat, closest_winner_cat, closest_competitor_cat = self._distance_confidence(
            winner_distance_values, competitor_distance_values
        )
        vote_component_cat = count_cat / len(neighbors_category)
        confidence_cat = self._blend_confidence(vote_component_cat, distance_component_cat)

        # 2. FIND NEIGHBORS FOR URGENCY
        neighbors_urgency = self._get_nearest_neighbors(
            query_embedding, 
            k_neighbors
        )
        
        # If no neighbors found even in tagged zone, we cannot determine urgency.
        if not neighbors_urgency:
             is_urgent_result = False
             
             reasoning = (
                 f"[KNN] Category: '{winner_cat}' ({count_cat}/{len(neighbors_category)} votes). "
             )
             return winner_cat, round(confidence_cat, 2), reasoning, is_urgent_result


        # --- B. VOTING FOR URGENCY (Binary) ---
        
        # 1. Count votes for True
        neighbor_distances_urgency = self._prepare_neighbor_distances(
            query_embedding, neighbors_urgency
        )
        urgent_votes = sum(1 for ex in neighbors_urgency if ex.is_urgent)
        
        # 2. Determine urgency: Majority voting
        is_urgent_result = urgent_votes > (len(neighbors_urgency) / 2) 
        
        # 3. Confidence for urgency (number of True votes / Total)
        urgent_winner_distances = [
            dist
            for example, dist in neighbor_distances_urgency
            if bool(example.is_urgent) == is_urgent_result
        ]
        urgent_competitor_distances = [
            dist
            for example, dist in neighbor_distances_urgency
            if bool(example.is_urgent) != is_urgent_result
        ]
        distance_component_urgency, closest_winner_urgency, closest_competitor_urgency = self._distance_confidence(
            urgent_winner_distances, urgent_competitor_distances
        )
        vote_component_urgency = (
            urgent_votes / len(neighbors_urgency)
            if is_urgent_result
            else (len(neighbors_urgency) - urgent_votes) / len(neighbors_urgency)
        )
        confidence_urgent = self._blend_confidence(
            vote_component_urgency, distance_component_urgency
        )
        
        # --- C. FORMING RESPONSE ---
        
        category = self.get_category_info(winner_cat)
        cat_name = category.name if category else winner_cat
        
        def _format_distance_details(closest_winner: float | None, closest_competitor: float | None) -> str:
            if closest_winner is None:
                return "dist: n/a"
            if closest_competitor is None:
                return f"closest dist: {closest_winner:.3f}"
            gap = max(0.0, closest_competitor - closest_winner)
            return f"closest dist: {closest_winner:.3f}, gap: {gap:.3f}"

        reasoning = (
            f"[KNN] Category: '{cat_name}' ({count_cat}/{len(neighbors_category)} votes, "
            f"{_format_distance_details(closest_winner_cat, closest_competitor_cat)}). "
            f"Urgency: {'True' if is_urgent_result else 'False'} ({urgent_votes}/{len(neighbors_urgency)} votes, "
            f"{_format_distance_details(closest_winner_urgency, closest_competitor_urgency)}). "
            f"Confidence in Category: {round(confidence_cat, 2)}. "
            f"Confidence in Urgency: {round(confidence_urgent, 2)}"
        )

        return winner_cat, round(confidence_cat, 2), reasoning, is_urgent_result
