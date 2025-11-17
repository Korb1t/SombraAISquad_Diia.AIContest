# Database Migrations with Alembic

This project uses Alembic for database schema migrations.

## Setup

1. Install dependencies (alembic is already in pyproject.toml):
```bash
pip install -e .
```

## Common Commands

### Create a new migration (auto-generate from models)
```bash
alembic revision --autogenerate -m "description of changes"
```

### Apply migrations (upgrade to latest)
```bash
alembic upgrade head
```

### Rollback last migration
```bash
alembic downgrade -1
```

### Show current migration version
```bash
alembic current
```

### Show migration history
```bash
alembic history
```

## Initial Setup (First Time)

1. Create initial migration:
```bash
alembic revision --autogenerate -m "Initial tables"
```

2. Apply migration:
```bash
alembic upgrade head
```

## Alternative: Use init_db.py script

For development, you can also use the init_db.py script which creates tables directly:
```bash
python -m app.scripts.init_db
```

Note: This approach doesn't use migrations and will recreate tables from scratch.
