from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings


def get_llm():
    return ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.0,
    )


def get_embeddings():
    return OpenAIEmbeddings(model="text-embedding-3-small")
