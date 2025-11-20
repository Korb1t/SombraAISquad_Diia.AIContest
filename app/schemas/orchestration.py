"""
Schemas for end-to-end orchestration flow.
Combines user info, problem classification, service resolution, and appeal generation.
"""
from pydantic import BaseModel, Field
from app.schemas.base import PersonalInfo, ClassificationBase


class OrchestrationRequest(BaseModel):
    """Complete request with user info and problem description for full processing"""
    name: str = Field(..., description="User name")
    address: str = Field(..., description="Full address or street name where problem occurred")
    phone: str | None = Field(default=None, description="User phone number")
    problem_text: str = Field(..., min_length=5, description="Problem description from user")


class ServiceDetails(BaseModel):
    """Service information in the orchestration response"""
    service_name: str = Field(..., description="Name of the service")
    phone_main: str | None = Field(default=None, description="Main phone number")
    email_main: str | None = Field(default=None, description="Main email address")
    address_legal: str | None = Field(default=None, description="Legal address")
    website: str | None = Field(default=None, description="Website URL")


class ClassificationDetails(BaseModel):
    """Classification details in the orchestration response"""
    category_id: str = Field(..., description="Category ID")
    category_name: str = Field(..., description="Category name")
    confidence: float = Field(..., description="Classification confidence (0.0-1.0)")
    is_urgent: bool = Field(..., description="Is this an urgent/emergency problem?")
    category_description: str = Field(..., description="Category description")
    reasoning: str = Field(..., description="Explanation for classification")


class OrchestrationResponse(BaseModel):
    """Complete response with classification, service, and appeal"""
    user_info: PersonalInfo = Field(..., description="User information")
    classification: ClassificationDetails = Field(..., description="Problem classification")
    service: ServiceDetails = Field(..., description="Assigned service information")
    appeal_text: str = Field(..., description="Generated appeal letter text")
    service_reasoning: str = Field(..., description="Explanation for service assignment")
