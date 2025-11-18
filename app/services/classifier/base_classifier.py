from abc import ABC, abstractmethod
from typing import Tuple

from sqlmodel import Session
from app.db_models import Category


class BaseClassifier(ABC):
    """Abstract base class for all classification strategies"""
    
    def __init__(self, session: Session):
        self.session = session

    @abstractmethod
    def classify(self, problem_text: str) -> Tuple[str, float, str]:
        """Must return (category_id, confidence, reasoning)"""
        pass

    def get_category_info(self, category_id: str) -> Category | None:
        return self.session.get(Category, category_id)

    def classify_with_category(self, problem_text: str) -> dict:
        """Shared logic for formatting the final response"""
        category_id, confidence, reasoning = self.classify(problem_text)
        
        if category_id == "other":
             return {
                "category_id": "other",
                "category_name": "Uncategorized",
                "category_description": "Could not determine specific category",
                "confidence": confidence,
                "reasoning": reasoning
            }

        category = self.get_category_info(category_id)
        if not category:
            # Fallback for data inconsistency
            return {
                "category_id": category_id,
                "category_name": "Unknown", 
                "category_description": "Category ID exists in model but not DB",
                "confidence": confidence,
                "reasoning": reasoning
            }
        
        return {
            "category_id": category.id,
            "category_name": category.name,
            "category_description": category.description,
            "confidence": confidence,
            "reasoning": reasoning
        }
