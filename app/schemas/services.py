"""Service-related request and response schemas"""
from typing import Literal
from pydantic import BaseModel, Field

from app.schemas.base import ClassificationBase


class IssueRequest(BaseModel):
    """Request schema for problem routing"""
    category_id: str = Field(..., description="Category ID")
    is_urgent: bool = Field(..., description="Is this an urgent/emergency problem?")
    street_name: str = Field(..., description="Street name")
    house_number: str = Field(..., description="House number")
    city: Literal["Львів"] = Field(default="Львів", description="City (fixed for safety)")

class ServiceInfo(BaseModel):
    """Service information details"""
    service_type: str = Field(..., description="Type of service")
    service_name: str = Field(..., description="Name of the service")
    service_phone: str | None = Field(default=None, description="Service phone")
    service_email: str | None = Field(default=None, description="Service email")
    service_website: str | None = Field(default=None, description="Service website")
    service_address: str | None = Field(default=None, description="Service address")

class ServiceResponse(ClassificationBase):
    """Response schema with responsible service contacts"""
    service_info: ServiceInfo = Field(..., description="Information about the responsible service")
    reasoning: str = Field(..., description="Explanation for service selection")
