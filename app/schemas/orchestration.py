"""
Schemas for end-to-end orchestration flow.
Combines user info, problem classification, service resolution, and appeal generation.
"""
from pydantic import BaseModel, Field

from app.schemas.base import PersonalInfo
from app.schemas.problems_schemas import ProblemClassificationResponse
from app.schemas.services import ServiceResponse


class OrchestrationRequest(BaseModel):
    """Complete request with user info and problem description for full processing"""
    user_info: PersonalInfo = Field(..., description="User information")
    problem_text: str = Field(..., min_length=5, description="Problem description from user")


class OrchestrationResponse(BaseModel):
    """Complete response with classification, service, and appeal"""
    user_info: PersonalInfo = Field(..., description="User information")
    classification: ProblemClassificationResponse = Field(..., description="Problem classification")
    service: ServiceResponse = Field(..., description="Assigned service information")
    appeal_text: str = Field(..., description="Generated appeal letter text")
