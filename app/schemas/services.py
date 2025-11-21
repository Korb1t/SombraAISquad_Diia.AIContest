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


class ServiceResponse(ClassificationBase):
    """Response schema with responsible service contacts"""
    service_type: str = Field(..., description="Type of service")
    phone_main: str | None = Field(default=None, description="Main phone number")
    email_main: str | None = Field(default=None, description="Main email address")
    reasoning: str = Field(..., description="Explanation for service selection")


class ServiceInfo(BaseModel):
    """Service information details"""
    service_name: str = Field(..., description="Name of the service")
    service_phone: str | None = Field(default=None, description="Service phone")
    service_email: str | None = Field(default=None, description="Service email")
    service_address: str | None = Field(default=None, description="Service address")
