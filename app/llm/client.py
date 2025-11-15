import os
from openai import OpenAI


def _create_openai_client() -> OpenAI:
    """Create and configure OpenAI client"""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(f"OPENAI_API_KEY not found! Available vars: {list(os.environ.keys())[:10]}")
    
    return OpenAI(
        api_key=api_key,
        base_url=os.environ.get("OPENAI_API_BASE", "https://codemie.lab.epam.com/llms"),
    )


class SimpleLLM:
    """Wrapper for OpenAI client that works with CodeMie"""
    
    def __init__(self):
        self.client = _create_openai_client()
        self.model = os.environ.get("MODEL_NAME", "gpt-5-mini-2025-08-07")
    
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
        self.model = os.environ.get("EMBEDDING_MODEL", "codemie-text-embedding-ada-002")
    
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