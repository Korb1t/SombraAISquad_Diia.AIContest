from sqlmodel import Session, select
from app.db_models import Category, Service, ServiceArea

def get_or_create_service(session: Session, name: str, defaults: dict) -> Service:
    """Helper to find a service by name or create it."""
    statement = select(Service).where(Service.name_ua == name)
    service = session.exec(statement).first()
    
    if not service:
        service = Service(name_ua=name, **defaults)
        session.add(service)
        session.commit()
        session.refresh(service)
        print(f"   [+] Created Service: {name}")
    else:
        print(f"   [.] Exists Service: {name}")
    
    return service

def get_or_create_area(session: Session, service_id: int, category_id: str, defaults: dict):
    """Helper to find an area or create it."""
    statement = (
        select(ServiceArea)
        .where(ServiceArea.service_id == service_id)
        .where(ServiceArea.category_id == category_id)
        .where(ServiceArea.coverage_level == defaults.get("coverage_level"))
    )
    area = session.exec(statement).first()
    
    if not area:
        area = ServiceArea(
            service_id=service_id,
            category_id=category_id,
            **defaults
        )
        session.add(area)
        session.commit()
        print(f"   [+] Linked Area: Service {service_id} -> Category {category_id}")
    else:
        print(f"   [.] Exists Area: Service {service_id} -> Category {category_id}")


def load_services_and_areas(session: Session):
    """Load initial utility services."""
    print("\n--- Loading Services ---")

    # 1. Define Services
    dispatcher = get_or_create_service(
        session, 
        name="Міська гаряча лінія 1580", 
        defaults={
            "type": "Диспетчерська",
            "phone_main": "1580",
            "address_legal": "м. Львів, пл. Ринок, 1",
            "website": "https://city-adm.lviv.ua",
            "is_emergency": True
        }
    )

    lvivsvitlo = get_or_create_service(
        session,
        name='КП "Львівсвітло"',
        defaults={
            "type": "КП",
            "phone_main": "+38 (032) 297-51-11",
            "address_legal": "м. Львів, вул. Стрийська, 45",
            "website": "https://kp-lvivsvitlo.lviv.ua",
            "is_emergency": False
        }
    )

    # 2. Define Areas
    get_or_create_area(
        session,
        service_id=dispatcher.service_id,
        category_id="other",
        defaults={
            "city": "Львів",
            "coverage_level": "citywide",
            "is_primary": True
        }
    )

    # Check for category existence before linking
    if session.get(Category, "lighting"):
        get_or_create_area(
            session,
            service_id=lvivsvitlo.service_id,
            category_id="lighting",
            defaults={
                "city": "Львів",
                "coverage_level": "citywide",
                "is_primary": True
            }
        )
    else:
        print("   [!] Warning: Category 'lighting' not found. Skipping area assignment.")
