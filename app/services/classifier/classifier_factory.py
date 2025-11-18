from sqlmodel import Session

from app.services.classifier.base_classifier import BaseClassifier
from app.services.classifier.knn_classifier import KNNClassifier
from app.services.classifier.llm_classifier import LLMClassifier
from app.services.classifier.hybrid_classifier import HybridClassifier
from app.core.config import settings


def get_classifier(session: Session) -> BaseClassifier:
    """
    Factory that returns the configured classifier strategy.
    Reads from env vars: CLASSIFIER_TYPE and CLASSIFIER_THRESHOLD
    """
    mode = settings.CLASSIFIER_TYPE.lower()
    if mode == "llm":
        return LLMClassifier(session)
    elif mode == "knn":
        return KNNClassifier(session)
    elif mode == "hybrid":
        return HybridClassifier(session, threshold=settings.CLASSIFIER_THRESHOLD)
    return KNNClassifier(session)