"""
Schemas for appeal (simple letter) generation endpoint.
"""
from pydantic import BaseModel, Field


class AppealRequest(BaseModel):
    """Request for simple appeal generation"""
    problem_text: str = Field(..., description="Problem description in informal style")
    address: str = Field(..., description="Street name where the problem occurred")
    building: str = Field(..., description="Building number")
    apartment: str = Field(default="", description="Apartment number (optional, extracted from problem_text)")


class AppealResponse(BaseModel):
    """Response with generated appeal"""
    letter_text: str = Field(..., description="Generated appeal text")
