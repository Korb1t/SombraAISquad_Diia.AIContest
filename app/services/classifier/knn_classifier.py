from typing import Tuple
from collections import Counter
from sqlmodel import Session, select

from app.core.config import settings
from app.db_models import Example
from app.llm.client import get_embeddings
from app.services.classifier.base_classifier import BaseClassifier

# TODO: Remove is_relevant as field and add as new category
class KNNClassifier(BaseClassifier):
    """
    Math-based classifier using Vector Voting.
    Performs simultaneous multi-label classification for category and urgency.
    """

    # TEMP VARIABLE WHILE DB IS BEING TAGGED FOR URGENCY
    MAX_URGENCY_TAGGED_ID = 2370  # Only IDs < 2370 are reliably tagged for urgency

    # TODO: Implement is_relevant classification
    is_relevant = True

    def __init__(self, session: Session):
        super().__init__(session)
        self.embeddings = get_embeddings()

    def _get_nearest_neighbors(self, query_embedding, k: int, filter_max_id: int = None) -> list[Example]:
        """
        Finds the K nearest neighbors based on cosine distance.
        """
        statement = (
            select(Example)
            .order_by(Example.embedding.cosine_distance(query_embedding))
            .limit(k)
        )

        if filter_max_id is not None:
            statement = statement.where(Example.id <= filter_max_id)
             
        return self.session.exec(statement).all()

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
            return "other", 0.0, "No historical examples found for category classification.", False, self.is_relevant

        # --- A. VOTING FOR CATEGORY (Multi-Class) ---
        votes_cat = [ex.category_id for ex in neighbors_category]
        vote_counts_cat = Counter(votes_cat)
        winner_cat, count_cat = vote_counts_cat.most_common(1)[0]
        confidence_cat = count_cat / len(neighbors_category)

        # 2. FIND NEIGHBORS FOR URGENCY (Use only 2000 tagged)
        neighbors_urgency = self._get_nearest_neighbors(
            query_embedding, 
            k_neighbors, 
            filter_max_id=self.MAX_URGENCY_TAGGED_ID
        )
        
        # If no neighbors found even in tagged zone, we cannot determine urgency.
        if not neighbors_urgency:
             is_urgent_result = False
             
             reasoning = (
                 f"[KNN] Category: '{winner_cat}' ({count_cat}/{len(neighbors_category)} votes). "
                 f"Urgency: Cannot be determined (No tagged neighbors found below ID {self.MAX_URGENCY_TAGGED_ID})."
             )
             return winner_cat, round(confidence_cat, 2), reasoning, is_urgent_result, self.is_relevant


        # --- B. VOTING FOR URGENCY (Binary) ---
        
        # 1. Count votes for True
        urgent_votes = sum(1 for ex in neighbors_urgency if ex.is_urgent)
        
        # 2. Determine urgency: Majority voting
        is_urgent_result = urgent_votes > (len(neighbors_urgency) / 2) 
        
        # 3. Confidence for urgency (number of True votes / Total)
        confidence_urgent = urgent_votes / len(neighbors_urgency) 
        
        # --- C. FORMING RESPONSE ---
        
        category = self.get_category_info(winner_cat)
        cat_name = category.name if category else winner_cat
        
        reasoning = (
            f"[KNN] Category: '{cat_name}' ({count_cat}/{len(neighbors_category)} votes). "
            f"Urgency: {'True' if is_urgent_result else 'False'} ({urgent_votes}/{len(neighbors_urgency)} urgent votes from tagged set). "
            f"Confidence in Category: {round(confidence_cat, 2)}. "
            f"Confidence in Urgency: {round(confidence_urgent, 2)}"
        )

        return winner_cat, round(confidence_cat, 2), reasoning, is_urgent_result, self.is_relevant
