"""Base schemas with common fields and validators"""
from pydantic import BaseModel, Field


class PersonalInfo(BaseModel):
    """Common user information fields"""
    name: str | None = Field(default=None, description="Applicant name")
    address: str | None = Field(default=None, description="Applicant address")
    city: str | None = Field(default=None, description="Applicant city")
    phone: str | None = Field(default=None, description="Applicant phone")
    apartment: str | None = Field(default=None, description="Apartment number")


class ClassificationBase(BaseModel):
    """Base classification fields used across multiple schemas"""
    category_id: str = Field(..., description="Category ID")
    category_name: str = Field(..., description="Category name")
    confidence: float = Field(..., description="Classification confidence (0.0-1.0)")
    is_urgent: bool = Field(..., description="Is this an urgent/emergency problem?")


class TextValidator:
    """Reusable text validators"""
    
    @staticmethod
    def validate_non_empty_text(v: str) -> str:
        """Validate that text is not just whitespace"""
        if not v or not v.strip():
            raise ValueError("Text cannot be empty or whitespace only")
        return v.strip()
