# Database Initialization Module

This module handles the setup of the PostgreSQL database, including:
1. Enabling the `pgvector` extension.
2. Creating database tables (SQLModel).
3. Seeding initial data (Categories, RAG Examples, Services, Service Areas).

## File Structure

- **`main.py`**: The entry point script. Orchestrates the initialization process.
- **`db_setup.py`**: Low-level DB tasks (creating extensions, tables).
- **`seed_classification.py`**: Loads AI categories and generates embeddings for examples.
- **`seed_services.py`**: Loads utility service providers (e.g., Lvivsvitlo) and their coverage areas.

## Usage

**Important:** Run this script from the **root** of the project (where `.env` is located) to ensure imports work correctly.

### Standard Run
Safe to run multiple times. It checks if data exists before adding it (idempotent).
```bash
python app/scripts/initial_data/main.py
