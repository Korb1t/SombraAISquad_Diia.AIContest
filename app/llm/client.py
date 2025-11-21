from openai import OpenAI
import google.generativeai as genai
from app.core.config import settings


def _create_openai_client() -> OpenAI:
    """
    Create and configure OpenAI-compatible client for CodeMie
    """
    return OpenAI(
        api_key=settings.CODEMIE_API_KEY,
        base_url=settings.CODEMIE_API_BASE,
    )


def _create_genai_client():
    """
    Configure and return genai client for CodeMie endpoint
    """
    genai.configure( 
        api_key=settings.CODEMIE_API_KEY,
        transport="rest",
        client_options={
            "api_endpoint": settings.CODEMIE_API_BASE
        }
    )
    return genai


class SimpleLLM:
    """Wrapper for OpenAI client that works with CodeMie"""
    
    def __init__(self):
        self.client = _create_openai_client()
        self.model = settings.CODEMIE_LLM_MODEL
    
    def invoke(self, prompt: str):
        """Invoke LLM with prompt and return Response object with .content attribute"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )
        
        class Response:
            def __init__(self, text):
                self.content = text
        
        return Response(response.choices[0].message.content)
    
    async def generate_text(self, prompt: str, temperature: float = 0.7) -> str:
        """
        Generate text based on prompt (async version).
        
        Args:
            prompt: Input prompt for text generation
            temperature: Sampling temperature (0.0 to 1.0)
            
        Returns:
            Generated text
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature
        )
        
        content = response.choices[0].message.content
        if content is None:
            raise ValueError("LLM returned empty response")
        
        return content


class SimpleEmbeddings:
    """Wrapper for embeddings via CodeMie"""
    
    def __init__(self):
        self.client = _create_openai_client()
        self.model = settings.CODEMIE_EMBEDDING_MODEL
    
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
        self.model = self.client.GenerativeModel(settings.CODEMIE_TRANSCRIPTION_MODEL)


def get_gemini_client() -> GeminiClient:
    """Get Gemini client"""
    return GeminiClient()