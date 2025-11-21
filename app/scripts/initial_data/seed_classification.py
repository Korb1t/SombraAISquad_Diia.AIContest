import json
from pathlib import Path
from sqlmodel import Session, select
from app.db_models import Category, Example
from app.llm.client import get_embeddings

def load_categories_and_examples(session: Session, categories_file: str, force: bool = False):
    """Load categories and examples from JSON file."""
    categories_path = Path(categories_file)
    if not categories_path.exists():
        print(f"Category file {categories_file} not found. Skipping.")
        return

    with open(categories_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    embeddings_model = None 

    added_cats, updated_cats = 0, 0
    added_ex, skipped_ex = 0, 0

    for cat_data in data["categories"]:
        # 1. Upsert Category
        category = session.get(Category, cat_data["id"])
        if not category:
            category = Category(
                id=cat_data["id"],
                name=cat_data["name"],
                description=cat_data["description"],
            )
            session.add(category)
            added_cats += 1
        elif force:
            category.name = cat_data["name"]
            category.description = cat_data["description"]
            session.add(category)
            updated_cats += 1

        # 2. Upsert Examples
        for example_text in cat_data["examples"]:
            # Check existence by text + category
            stmt = (
                select(Example)
                .where(Example.category_id == cat_data["id"])
                .where(Example.text == example_text)
            )
            existing_example = session.exec(stmt).first()

            if existing_example and not force:
                skipped_ex += 1
                continue

            # Initialize embeddings client only when needed
            if not embeddings_model:
                print("   [i] Initializing Embedding Model...")
                embeddings_model = get_embeddings()

            print(f"   Generating embedding for: {example_text[:30]}...")
            embedding = embeddings_model.embed_query(example_text)

            if existing_example:
                existing_example.embedding = embedding
                session.add(existing_example)
            else:
                example = Example(
                    category_id=cat_data["id"],
                    text=example_text,
                    embedding=embedding,
                )
                session.add(example)
                added_ex += 1

    session.commit()
    print(
        f"Categories: {added_cats} added, {updated_cats} updated. "
        f"Examples: {added_ex} added, {skipped_ex} skipped."
    )
