from typing import Tuple
import json

from sqlmodel import Session, select
from app.db_models import Category, Example
from app.llm.client import get_llm, get_embeddings
from app.llm.prompts import CLASSIFIER_PROMPT_TEMPLATE
from app.services.classifier.base_classifier import BaseClassifier
from app.llm.prompts import URGENCY_CHECK_PROMPT
from app.db_models import Category, Example


class LLMClassifier(BaseClassifier):
    """Intelligent, generative classifier using Few-Shot Prompting"""

    def __init__(self, session: Session):
        super().__init__(session)
        self.llm = None # Lazy load

    def _get_llm(self):
        if self.llm is None:
            self.llm = get_llm()
        return self.llm
    
    def _get_similar_examples(self, problem_text: str, top_k: int = 5) -> list[Example]:
        """Find most similar examples through vector search"""

        # Generate embedding for user's problem
        embeddings = get_embeddings()
        query_embedding = embeddings.embed_query(problem_text)

        # Vector search for nearest examples
        statement = (
            select(Example)
            .order_by(Example.embedding.cosine_distance(query_embedding))
            .limit(top_k)
        )
 
        results = self.session.exec(statement).all()
        return results

    def _build_few_shot_prompt(self, problem_text: str, similar_examples: list[Example]) -> str:
        """Build prompt with few-shot examples"""

        # Get all categories
        categories = self.session.exec(select(Category)).all()
        categories_list = "\n".join([f"- {cat.id}: {cat.name} - {cat.description}" for cat in categories])

        # Format examples
        examples_text = ""
        for i, example in enumerate(similar_examples, 1):
            examples_text += f"\nExample {i}:\n"
            examples_text += f"Text: \"{example.text}\"\n"
            examples_text += f"Category: {example.category_id}\n"

        # Use prompt template from prompts.py
        prompt = CLASSIFIER_PROMPT_TEMPLATE.format(
            categories_list=categories_list,
            examples_text=examples_text,
            problem_text=problem_text
        )

        return prompt
    
    def classify(self, problem_text: str) -> Tuple[str, float, str, bool]:

    def classify(self, problem_text: str) -> Tuple[str, float, str]:
        """
        Classify user's problem and check urgency in single LLM call
        
        Returns:
            Tuple[category_id, confidence, reasoning, is_urgent]
        """
        # Step 1: Find similar examples through RAG
        similar_examples = self._get_similar_examples(problem_text, top_k=5)
        
        if not similar_examples:
            return "other", 0.5, "No similar examples found in database", False
        
        # Step 2: Build few-shot prompt
        prompt = self._build_few_shot_prompt(problem_text, similar_examples)
        
        # Step 3: Get classification from LLM (includes urgency check now)
        llm = self._get_llm()
        response = llm.invoke(prompt)
        
        # Step 4: Parse response
        try:
            # Remove possible markdown blocks
            content = response.content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            
            result = json.loads(content)
            category_id = result.get("category_id", "other")
            confidence = float(result.get("confidence", 0.5))
            reasoning = result.get("reasoning", "")
            is_urgent = bool(result.get("is_urgent", False))
            

            # Check that category exists
            category = self.session.get(Category, category_id)
            if not category:
                return "other", 0.5, f"Category {category_id} not found", False
            
            return category_id, confidence, reasoning, is_urgent
            return category_id, confidence, f"[LLM] {reasoning}"
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            return "other", 0.5, f"LLM response parsing error: {str(e)}", False
    
    def get_category_info(self, category_id: str) -> Category | None:
        """Get category information"""
        return self.session.get(Category, category_id)
    
    def classify_with_category(self, problem_text: str) -> dict:
        """
        Classify problem and return full response with category info and urgency check
        
        Performs two-step analysis:
        1. Urgency detection via LLM
        2. Category classification via RAG + few-shot learning
        """
        # Classify category and check urgency in one call
        category_id, confidence, reasoning, is_urgent = self.classify(problem_text)
        category = self.get_category_info(category_id)
        
        if not category:
            raise ValueError(f"Category {category_id} not found in database")
        
        return {
            "category_id": category.id,
            "category_name": category.name,
            "category_description": category.description,
            "confidence": confidence,
            "reasoning": reasoning,
            "is_urgent": is_urgent
        }
