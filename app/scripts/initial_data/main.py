import argparse
import sys
from dotenv import load_dotenv
from sqlmodel import Session, create_engine

# Ensure app is in python path for imports to work if running from root
sys.path.insert(0, ".")

from app.core.config import settings
from app.scripts.initial_data.db_setup import init_pgvector_extension, create_tables
from app.scripts.initial_data.seed_classification import load_categories_and_examples
from app.scripts.initial_data.seed_services import load_services_and_areas

load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="Initialize local database.")
    parser.add_argument("--categories-file", default="app/data/categories.json")
    parser.add_argument("--force", action="store_true", help="Force update existing records")
    args = parser.parse_args()

    print("Starting database initialization...")

    # 1. Connect
    engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
    
    # 2. Structure
    init_pgvector_extension(engine)
    create_tables(engine)

    # 3. Data
    with Session(engine) as session:
        load_categories_and_examples(session, args.categories_file, args.force)
        load_services_and_areas(session)

    print("\nInitialization completed successfully!")

if __name__ == "__main__":
    main()
