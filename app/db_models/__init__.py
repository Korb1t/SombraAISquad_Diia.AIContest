from typing import Optional
from sqlmodel import Field, SQLModel, Column
from pgvector.sqlalchemy import Vector


class Category(SQLModel, table=True):
    """Utility problem category"""
    __tablename__ = "categories"
    
    id: str = Field(primary_key=True)
    name: str = Field(index=True)
    description: str


class Example(SQLModel, table=True):
    """Problem example for few-shot classification"""
    __tablename__ = "examples"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    category_id: str = Field(foreign_key="categories.id", index=True)
    text: str
    is_urgent: bool = Field(default=False, description="Is this an urgent/emergency problem?")

    embedding: list[float] = Field(sa_column=Column(Vector(1536)))  # for OpenAI text-embedding-3-small
    
    class Config:
        arbitrary_types_allowed = True