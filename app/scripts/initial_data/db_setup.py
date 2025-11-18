from sqlmodel import Session, SQLModel, text

def init_pgvector_extension(engine):
    """Create pgvector extension in PostgreSQL."""
    try:
        with Session(engine) as session:
            session.exec(text("CREATE EXTENSION IF NOT EXISTS vector"))
            session.commit()
        print("pgvector extension ensured")
    except Exception as e:
        print(f"Could not create pgvector extension. Ensure you have superuser privileges. Error: {e}")

def create_tables(engine):
    """Create all tables."""
    SQLModel.metadata.create_all(engine)
    print("Tables ensured")
