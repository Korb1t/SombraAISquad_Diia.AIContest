from openai import OpenAI
import google.generativeai as genai
from app.core.config import settings


def _create_openai_client() -> OpenAI:
    """
    Create and configure OpenAI client
    """
    return OpenAI(
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_API_BASE,
    )


def _create_genai_client():
    """
    Configure and return genai client for CodeMie endpoint
    """
    genai.configure( 
        api_key=settings.GEMINI_API_KEY,
        transport="rest",
        client_options={
            "api_endpoint": settings.OPENAI_API_BASE
        }
    )
    return genai


class SimpleLLM:
    """Wrapper for OpenAI client that works with CodeMie"""
    
    def __init__(self):
        self.client = _create_openai_client()
        self.model = settings.MODEL_NAME
    
    def invoke(self, prompt: str) -> str:
        """Invoke LLM with prompt"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )
        
        class Response:
            def __init__(self, text):
                self.content = text
        
        return Response(response.choices[0].message.content)


class SimpleEmbeddings:
    """Wrapper for embeddings via CodeMie"""
    
    def __init__(self):
        self.client = _create_openai_client()
        self.model = settings.EMBEDDING_MODEL
    
    def embed_query(self, text: str) -> list[float]:
        """Generate embedding for text"""
        response = self.client.embeddings.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding

def get_llm():
    """Get LLM client"""
    return SimpleLLM()


def get_embeddings():
    """Get embeddings client"""
    return SimpleEmbeddings()


class GeminiClient:
    """Wrapper for Gemini API via CodeMie"""
    
    def __init__(self):
        self.client = _create_genai_client()
        self.model = self.client.GenerativeModel(settings.GEMINI_MODEL)


def get_gemini_client() -> GeminiClient:
    """Get Gemini client"""
    return GeminiClient()