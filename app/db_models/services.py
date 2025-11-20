from typing import Optional, List
from sqlalchemy import UniqueConstraint
from sqlmodel import Column, Field, SQLModel, Relationship


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

    # Relationship to assignments
    assignments: List["ServiceAssignment"] = Relationship(back_populates="service")


class Building(SQLModel, table=True):
    """Unique geographic object (house number on a street)."""
    __tablename__ = "buildings"
    __table_args__ = (
        UniqueConstraint("city", "street_name", "house_number", name="uq_building_address"),
    )

    building_id: Optional[int] = Field(default=None, primary_key=True)
    
    city: str = Field(default="Львів", index=True)
    district: Optional[str] = Field(
        default=None, index=True, description="Administrative district name"
    )
    street_name: str = Field(index=True, description="Street name")
    house_number: str = Field(description="House number (e.g., '12', '12А')")

    assignments: List["ServiceAssignment"] = Relationship(back_populates="building")


class ServiceAssignment(SQLModel, table=True):
    """Link between a Service, a Problem Category, and a specific Building/Area."""
    __tablename__ = "service_assignments"
    __table_args__ = (
        UniqueConstraint(
            "building_id",
            "category_id",
            "service_id",
            name="uq_assignment_building_category_service",
        ),
    )

    assignment_id: Optional[int] = Field(default=None, primary_key=True)

    service_id: int = Field(
        foreign_key="services.service_id",
        index=True,
        description="Service responsible for this assignment",
    )
    category_id: str = Field(
        foreign_key="categories.id",
        index=True,
        description="Problem category ID handled",
    )

    building_id: Optional[int] = Field(
        default=None,
        foreign_key="buildings.building_id",
        index=True,
        description="Specific building ID covered (NULL for wider coverage)",
    )

    # Coverage granularity: building | street | district | citywide
    coverage_level: str = Field(
        default="building",
        description="Coverage granularity",
    )
    
    is_primary: bool = Field(
        default=True,
        description="Marks primary/priority service for this combination",
    )

    # Relationships
    service: Service = Relationship(back_populates="assignments")
    building: Optional[Building] = Relationship(back_populates="assignments")
