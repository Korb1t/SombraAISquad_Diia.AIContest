"""Problem-related request and response schemas"""
from pydantic import BaseModel, Field, field_validator

from app.schemas.base import ClassificationBase, TextValidator, PersonalInfo


class ProblemRequest(BaseModel):
    """User's problem submission"""
    problem_text: str = Field(..., min_length=5, description="Problem description from user")
    user_info: PersonalInfo = Field(..., description="Information about the user submitting the problem")

    @field_validator('problem_text')
    @classmethod
    def validate_problem_text(cls, v: str) -> str:
        """Validate that problem text is not just whitespace"""
        return TextValidator.validate_non_empty_text(v)


class ProblemClassificationResponse(ClassificationBase):
    """Classification analysis response"""
    is_relevant: bool = Field(..., description="Whether this is actually a municipal utility problem")
    category_description: str = Field(..., description="Category description")
    reasoning: str = Field(..., description="Explanation why this category was chosen")


class ProblemResponse(ClassificationBase):
    """Full response with classification, service and letter"""
    service_info: PersonalInfo = Field(..., description="Service contact information")
    letter_text: str = Field(..., description="Generated letter text")
