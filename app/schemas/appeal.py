"""
Schemas for appeal (simple letter) generation endpoint.
"""
from pydantic import BaseModel, Field


class AppealRequest(BaseModel):
    """Request for simple appeal generation"""
    problem_text: str = Field(..., description="Problem description in informal style")
    address: str = Field(..., description="Whole address where the problem occurred")
class AppealResponse(BaseModel):
    """Response with generated appeal"""
    letter_text: str = Field(..., description="Generated appeal text")
