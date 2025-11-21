from typing import Optional, List
from pgvector.sqlalchemy import Vector
from sqlmodel import Column, Field, SQLModel, Relationship

class Category(SQLModel, table=True):
    """Utility problem category."""
    __tablename__ = "categories"

    id: str = Field(primary_key=True)
    name: str = Field(index=True)
    description: str
    
    # Relationship back-populates (Optional, but recommended for easy access)
    examples: List["Example"] = Relationship(back_populates="category")

class Example(SQLModel, table=True):
    """Problem example for few-shot classification (used for RAG)."""
    __tablename__ = "examples"

    id: Optional[int] = Field(default=None, primary_key=True)
    category_id: str = Field(foreign_key="categories.id", index=True)
    text: str
    is_urgent: bool = Field(default=False, index=True)
    
    # pgvector embedding
    embedding: list[float] = Field(sa_column=Column(Vector(1536)))
    
    category: Category = Relationship(back_populates="examples")

    class Config:
        arbitrary_types_allowed = True
