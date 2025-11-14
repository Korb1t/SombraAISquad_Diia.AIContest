from pydantic import BaseModel, Field


class ProblemRequest(BaseModel):
    problem_text: str = Field(..., description="Опис проблеми від користувача")
    user_name: str | None = Field(default=None, description="Ім'я заявника")
    user_address: str | None = Field(default=None, description="Адреса заявника")
    user_phone: str | None = Field(default=None, description="Телефон заявника")


class ServiceInfo(BaseModel):
    service_name: str
    service_phone: str | None = None
    service_email: str | None = None
    service_address: str | None = None


class ProblemResponse(BaseModel):
    category_id: str
    category_name: str
    confidence: float
    service: ServiceInfo
    letter_text: str
