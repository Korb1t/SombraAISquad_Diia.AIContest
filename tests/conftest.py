"""
Pytest configuration and fixtures for end-to-end tests

These tests run against a real PostgreSQL database with pgvector extension.
Ensure that:
1. PostgreSQL is running (e.g., via docker-compose up)
2. Database is initialized with migrations
3. Test data exists in the database
"""

import asyncio
import sys
import os
from pathlib import Path
import pytest
from typing import Generator
from sqlmodel import Session, create_engine
from sqlalchemy.pool import NullPool

# Add project root to path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.core.config import settings

# Configure event loop
@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_db() -> Generator[Session, None, None]:
    """Create database session using real PostgreSQL"""
    # Use the production database URI from settings
    engine = create_engine(
        str(settings.SQLALCHEMY_DATABASE_URI),
        poolclass=NullPool,  # Don't reuse connections for tests
        echo=False,
    )
    
    with Session(engine) as session:
        yield session


@pytest.fixture
def app_with_db_override(test_db: Session):
    """Override database dependency for app"""
    from app.main import app
    from app.api.deps import get_db
    
    def get_test_db():
        return test_db
    
    app.dependency_overrides[get_db] = get_test_db
    
    yield app
    
    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
async def async_client(app_with_db_override):
    """Create async test client for FastAPI app"""
    from httpx import AsyncClient, ASGITransport
    
    # Use ASGI transport to connect to FastAPI app
    async with AsyncClient(
        transport=ASGITransport(app=app_with_db_override),
        base_url="http://test"
    ) as client:
        yield client


# Markers
def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line(
        "markers", "asyncio: mark test as async"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
