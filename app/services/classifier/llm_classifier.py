from typing import Tuple
import json

from sqlmodel import Session, select
from app.llm.client import get_llm, get_embeddings
from app.llm.prompts import CLASSIFIER_SAFE_TEMPLATE
from app.services.classifier.base_classifier import BaseClassifier
from app.db_models import Category, Example
from app.utils.security import sanitize_prompt_input


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
        """Build secure prompt with few-shot examples"""

        # Get all categories
        categories = self.session.exec(select(Category)).all()
        categories_list = "\n".join([f"- {cat.id}: {cat.name} - {cat.description}" for cat in categories])

        # Format examples
        examples_text = ""
        for i, example in enumerate(similar_examples, 1):
            examples_text += f"\nExample {i}:\n"
            examples_text += f"Text: \"{example.text}\"\n"
            examples_text += f"Category: {example.category_id}\n"

        # Use safe prompt template from file
        prompt = CLASSIFIER_SAFE_TEMPLATE.format(
            categories_list=categories_list,
            examples_text=examples_text,
            problem_text=problem_text
        )

        return prompt
    
    def classify(self, problem_text: str) -> Tuple[str, float, str, bool, bool]:
        """
        Classify user's problem, check relevance and urgency in single LLM call
        
        Returns:
            Tuple[category_id, confidence, reasoning, is_urgent, is_relevant]
        """
        # Step 0: Sanitize input to prevent prompt injection
        sanitized_text = sanitize_prompt_input(problem_text, max_length=2000)
        
        # Step 1: Find similar examples through RAG
        similar_examples = self._get_similar_examples(sanitized_text, top_k=5)
        
        if not similar_examples:
            return "other", 0.5, "No similar examples found in database", False, True
        
        # Step 2: Build few-shot prompt
        prompt = self._build_few_shot_prompt(sanitized_text, similar_examples)
        
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
            is_relevant = bool(result.get("is_relevant", True))
            category_id = result.get("category_id", "other")
            confidence = float(result.get("confidence", 0.5))
            reasoning = result.get("reasoning", "")
            is_urgent = bool(result.get("is_urgent", False))
            

            # Check that category exists
            category = self.session.get(Category, category_id)
            if not category:
                return "other", 0.5, f"Category {category_id} not found", False, is_relevant
            
            return category_id, confidence, reasoning, is_urgent, is_relevant
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            return "other", 0.5, f"LLM response parsing error: {str(e)}", False, True
    
    def get_category_info(self, category_id: str) -> Category | None:
        """Get category information"""
        return self.session.get(Category, category_id)
    
    def classify_with_category(self, problem_text: str) -> dict:
        """
        Classify problem and return full response with category info, relevance and urgency check
        
        Performs analysis:
        1. Relevance check - is this a utility problem?
        2. Urgency detection via LLM
        3. Category classification via RAG + few-shot learning
        """
        # Classify category, check relevance and urgency in one call
        category_id, confidence, reasoning, is_urgent, is_relevant = self.classify(problem_text)
        category = self.get_category_info(category_id)
        
        if not category:
            raise ValueError(f"Category {category_id} not found in database")
        
        return {
            "category_id": category.id,
            "category_name": category.name,
            "category_description": category.description,
            "confidence": confidence,
            "reasoning": reasoning,
            "is_urgent": is_urgent,
            "is_relevant": is_relevant
        }
