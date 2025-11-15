from pydantic import BaseModel, Field, field_validator


class ProblemRequest(BaseModel):
    problem_text: str = Field(..., min_length=5, description="Problem description from user")
    user_name: str | None = Field(default=None, description="Applicant name")
    user_address: str | None = Field(default=None, description="Applicant address")
    user_phone: str | None = Field(default=None, description="Applicant phone")
    
    @field_validator('problem_text')
    @classmethod
    def validate_problem_text(cls, v: str) -> str:
        """Validate that problem text is not just whitespace"""
        if not v or not v.strip():
            raise ValueError("Problem text cannot be empty or whitespace only")
        return v.strip()


class ProblemClassificationResponse(BaseModel):
    """Classifier response"""
    category_id: str = Field(..., description="Category ID")
    category_name: str = Field(..., description="Category name")
    category_description: str = Field(..., description="Category description")
    confidence: float = Field(..., description="Classification confidence (0.0-1.0)")
    reasoning: str = Field(..., description="Explanation why this category was chosen")


class ServiceInfo(BaseModel):
    service_name: str
    service_phone: str | None = None
    service_email: str | None = None
    service_address: str | None = None


class ProblemResponse(BaseModel):
    """Full response with classification, service and letter"""
    category_id: str
    category_name: str
    confidence: float
    service: ServiceInfo
    letter_text: str