"""Export all schemas for easy importing"""
from app.schemas.base import ClassificationBase, TextValidator, PersonalInfo
from app.schemas.problems_schemas import (
    ProblemClassificationResponse,
    ProblemRequest,
    ProblemResponse,
)
from app.schemas.services import IssueRequest, ServiceInfo, ServiceResponse

__all__ = [
    # Base
    "ClassificationBase",
    "TextValidator",
    "PersonalInfo",
    # Problems
    "ProblemRequest",
    "ProblemClassificationResponse",
    "ProblemResponse",
    # Services
    "IssueRequest",
    "ServiceInfo",
    "ServiceResponse",
]
