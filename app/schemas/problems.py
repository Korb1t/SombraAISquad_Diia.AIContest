"""
Backwards compatibility module. All schemas have been refactored into separate files.

For new code, import directly from:
- base: ClassificationBase, TextValidator, PersonalInfo
- problems_schemas: ProblemRequest, ProblemClassificationResponse, ProblemResponse
- services: IssueRequest, ServiceInfo, ServiceResponse
"""

# TODO: Refactor existing imports in the codebase to use the new schema files directly.
from app.schemas.base import ClassificationBase, TextValidator, PersonalInfo
from app.schemas.problems_schemas import (
    ProblemClassificationResponse,
    ProblemRequest,
    ProblemResponse,
)
from app.schemas.services import IssueRequest, ServiceInfo, ServiceResponse

__all__ = [
    "ProblemRequest",
    "ProblemClassificationResponse",
    "ProblemResponse",
    "ServiceInfo",
    "IssueRequest",
    "ServiceResponse",
    "ClassificationBase",
    "TextValidator",
    "PersonalInfo",
]
