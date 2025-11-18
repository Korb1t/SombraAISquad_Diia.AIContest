"""
Database initialization script
"""
import json
import os
from pathlib import Path
from sqlmodel import Session, SQLModel, create_engine, text
from dotenv import load_dotenv

# IMPORTANT: Load .env BEFORE everything else
load_dotenv()

from app.core.config import settings
from app.llm.client import get_embeddings
from app.db_models import Category, Example


def init_pgvector_extension(engine):
    """Create pgvector extension in PostgreSQL"""
    with Session(engine) as session:
        session.exec(text("CREATE EXTENSION IF NOT EXISTS vector"))
        session.commit()
    print("pgvector extension created")


def create_tables(engine):
    """Create all tables"""
    SQLModel.metadata.create_all(engine)
    print("Tables created")


def load_categories_and_examples(session: Session, categories_file: str = "app/data/categories.json"):
    """Load categories and examples from JSON file"""
    
    categories_path = Path(categories_file)
    if not categories_path.exists():
        raise FileNotFoundError(f"File {categories_file} not found")
    
    with open(categories_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    print("Checking API key...")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in .env file!")
    print(f"API key: {api_key[:10]}...")
    
    embeddings = get_embeddings()
    
    total_examples = 0
    for cat_data in data["categories"]:
        category = Category(
            id=cat_data["id"],
            name=cat_data["name"],
            description=cat_data["description"]
        )
        session.add(category)
        print(f"Category: {category.name}")
        
        for example_text in cat_data["examples"]:
            print(f"   Generating embedding...")
            embedding = embeddings.embed_query(example_text)
            
            example = Example(
                category_id=category.id,
                text=example_text,
                embedding=embedding
            )
            session.add(example)
            total_examples += 1
        
        print(f"   Added {len(cat_data['examples'])} examples")
    
    session.commit()
    print(f"\nLoaded {len(data['categories'])} categories and {total_examples} examples")


def main():
    """Main initialization function"""
    print("Starting database initialization...\n")
    
    engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
    
    init_pgvector_extension(engine)
    create_tables(engine)
    
    with Session(engine) as session:
        load_categories_and_examples(session)
    
    print("\nInitialization completed successfully!")


if __name__ == "__main__":
    main()