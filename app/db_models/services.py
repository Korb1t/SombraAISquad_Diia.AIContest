from typing import Optional, List
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Column, Field, SQLModel, Relationship

# We need to import Category for type hints if using Relationships across files,
# but usually, string forward references are safer to avoid circular imports.
# from .classification import Category 

class Service(SQLModel, table=True):
    """Utility service provider (КП, ЖЕК, ОСББ, etc.)."""
    __tablename__ = "services"

    service_id: Optional[int] = Field(default=None, primary_key=True)
    name_ua: str = Field(index=True, description="Official Ukrainian name")
    type: str = Field(description="Service type: КП, ЖЕК, ОСББ, etc.")
    
    phone_main: Optional[str] = Field(default=None)
    email_main: Optional[str] = Field(default=None)
    address_legal: Optional[str] = Field(default=None)
    website: Optional[str] = Field(default=None)
    is_emergency: bool = Field(default=False)

    # Relationship to areas
    areas: List["ServiceArea"] = Relationship(back_populates="service")


class ServiceArea(SQLModel, table=True):
    """Responsibility area for a given service and category."""
    __tablename__ = "service_areas"
    __table_args__ = (
        UniqueConstraint(
            "street_name",
            "service_id",
            "category_id",
            name="uq_service_areas_street_service_category",
        ),
    )

    area_id: Optional[int] = Field(default=None, primary_key=True)

    service_id: int = Field(foreign_key="services.service_id", index=True)
    category_id: str = Field(foreign_key="categories.id", index=True)

    city: str = Field(default="Львів")
    district: Optional[str] = Field(default=None)
    street_name: Optional[str] = Field(default=None)

    # JSONB for house numbers
    house_numbers: Optional[list[str]] = Field(
        default=None,
        sa_column=Column(JSONB),
        description="List/range of house numbers covered"
    )

    coverage_level: str = Field(default="building")
    is_primary: bool = Field(default=True)

    service: Service = Relationship(back_populates="areas")
    # Note: You can add a relationship to Category here too if needed
