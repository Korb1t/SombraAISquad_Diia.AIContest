from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any

from app.core.logging import get_logger
from app.services.health_check import get_health_check_service

router = APIRouter(prefix="/health", tags=["health"])
logger = get_logger(__name__)


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    services: dict[str, Any]


@router.get("/ping")
async def ping() -> dict:
    """
    Simple ping endpoint for basic liveness check
    
    Returns immediately without any dependencies
    """
    return {"status": "ok"}


@router.get("/", response_model=HealthCheckResponse)
async def health_check() -> HealthCheckResponse:
    """
    Detailed health check endpoint
    
    Checks:
    - Database connectivity and pgvector extension
    - CodeMie LLM API (text generation)
    - CodeMie Embeddings API (vector embeddings)
    - CodeMie Transcription API (audio to text)
    """
    logger.info("Health check requested")
    
    # Get health check service
    health_service = get_health_check_service()
    
    # Check all services
    db_status = health_service.check_database()
    codemie_status = health_service.check_codemie_api()
    
    # Determine overall status
    overall_status = health_service.get_overall_status(db_status, codemie_status)
    
    return HealthCheckResponse(
        status=overall_status,
        services={
            "database": db_status,
            "codemie_api": codemie_status
        }
    )