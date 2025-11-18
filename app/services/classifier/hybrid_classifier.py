import logging
from sqlmodel import Session
from typing import Tuple

from app.services.classifier.base_classifier import BaseClassifier
from app.services.classifier.knn_classifier import KNNClassifier
from app.services.classifier.llm_classifier import LLMClassifier

logger = logging.getLogger(__name__)


class HybridClassifier(BaseClassifier):
    """
    Tries the fast k-NN approach first.
    If confidence is below threshold, falls back to the heavy LLM approach.
    """
    
    def __init__(self, session: Session, threshold: float):
        super().__init__(session)
        self.threshold = threshold

        self.knn_strategy = KNNClassifier(session)
        self.llm_strategy = LLMClassifier(session)

    def classify(self, problem_text: str) -> Tuple[str, float, str]:
        """
        Orchestrates the classification flow.
        """
        cat_id, confidence, reasoning = self.knn_strategy.classify(problem_text)

        if confidence >= self.threshold:
            return cat_id, confidence, f"[Hybrid-Fast] {reasoning}"

        logger.info(
            f"Hybrid Fallback: KNN confidence {confidence} < {self.threshold}. "
            "Перехід до класифікації LLM.."
        )
        
        llm_cat, llm_conf, llm_reason = self.llm_strategy.classify(problem_text)

        final_reasoning = (
            f"[Hybrid-Deep] {llm_reason} "
            f"(Викликано після невдалої спроби KNN: confidence було лише {confidence:.2f})"
        )
        
        return llm_cat, llm_conf, final_reasoning
