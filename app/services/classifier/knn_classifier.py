
from typing import Tuple
from collections import Counter
from sqlmodel import Session, select

from app.core.config import settings
from app.db_models import Example
from app.llm.client import get_embeddings
from app.services.classifier.base_classifier import BaseClassifier


class KNNClassifier(BaseClassifier):
    """Math-based classifier using Vector Voting"""
    
    def __init__(self, session: Session):
        super().__init__(session)
        self.embeddings = get_embeddings()

    def classify(self, problem_text: str) -> Tuple[str, float, str, bool, bool]:
        query_embedding = self.embeddings.embed_query(problem_text)

        statement = (
            select(Example)
            .order_by(Example.embedding.cosine_distance(query_embedding))
            .limit(settings.TOP_K)
        )
        neighbors = self.session.exec(statement).all()
        
        if not neighbors:
            return "other", 0.0, "No historical examples found.", False, True

        votes = [ex.category_id for ex in neighbors]
        vote_counts = Counter(votes)
        winner, count = vote_counts.most_common(1)[0]

        confidence = count / len(neighbors)
        category = self.get_category_info(winner)
        cat_name = category.name if category else winner
        
        reasoning = (
            f"[KNN] k-NN Voting: {count}/{len(neighbors)} схожих випадків раніше "
            f"були класифіковані як '{cat_name}'."
        )

        # Todo: ML urgency detection should be added later
        # KNN cannot determine relevance, assumes relevant if historical data exists
        is_urgent = False
        is_relevant = True

        return winner, round(confidence, 2), reasoning, is_urgent, is_relevant

