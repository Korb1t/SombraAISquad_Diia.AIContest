"""Problem-related request and response schemas"""
from pydantic import BaseModel, Field, field_validator

from .base import ClassificationBase, TextValidator, UserInfo


class ProblemRequest(BaseModel):
    """User's problem submission"""
    problem_text: str = Field(..., min_length=5, description="Problem description from user")
    user_info: UserInfo = Field(..., description="Information about the user submitting the problem")

    @field_validator('problem_text')
    @classmethod
    def validate_problem_text(cls, v: str) -> str:
        """Validate that problem text is not just whitespace"""
        return TextValidator.validate_non_empty_text(v)


class ProblemClassificationResponse(ClassificationBase):
    """Classification analysis response"""
    category_description: str = Field(..., description="Category description")
    reasoning: str = Field(..., description="Explanation why this category was chosen")


class ProblemResponse(ClassificationBase):
    """Full response with classification, service and letter"""
    service_name: str = Field(..., description="Name of the responsible service")
    service_phone: str | None = Field(default=None, description="Service phone contact")
    service_email: str | None = Field(default=None, description="Service email contact")
    service_address: str | None = Field(default=None, description="Service address")
    letter_text: str = Field(..., description="Generated letter text")
