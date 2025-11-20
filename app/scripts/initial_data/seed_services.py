from sqlmodel import Session, select
from app.db_models import Category, Service, Building, ServiceAssignment

# Helper for Service
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

# Helper for Building (NEW)
def get_or_create_building(session: Session, city: str, street_name: str, house_number: str, defaults: dict = None) -> Building:
    """Helper to find a building by address or create it."""
    defaults = defaults or {}
    statement = (
        select(Building)
        .where(Building.city == city)
        .where(Building.street_name == street_name)
        .where(Building.house_number == house_number)
    )
    building = session.exec(statement).first()
    
    if not building:
        building = Building(
            city=city,
            street_name=street_name,
            house_number=house_number,
            **defaults
        )
        session.add(building)
        session.commit()
        session.refresh(building)
        print(f"   [+] Created Building: {city}, {street_name} {house_number}")
    else:
        print(f"   [.] Exists Building: {city}, {street_name} {house_number}")
    
    return building

# Helper for Assignment (REPLACES get_or_create_area)
def get_or_create_assignment(session: Session, service_id: int, category_id: str, coverage_level: str, defaults: dict):
    """Helper to find an assignment or create it."""
    
    # Use building_id if provided in defaults, otherwise NULL
    building_id = defaults.get("building_id")

    statement = (
        select(ServiceAssignment)
        .where(ServiceAssignment.service_id == service_id)
        .where(ServiceAssignment.category_id == category_id)
        .where(ServiceAssignment.coverage_level == coverage_level)
        .where(ServiceAssignment.building_id == building_id)
    )
    assignment = session.exec(statement).first()
    
    if not assignment:
        assignment = ServiceAssignment(
            service_id=service_id,
            category_id=category_id,
            coverage_level=coverage_level,
            **defaults
        )
        session.add(assignment)
        session.commit()
        
        detail = f"Building ID {building_id}" if building_id else "Citywide"
        print(f"   [+] Linked Assignment: Service {service_id} -> Category {category_id} ({detail})")
    else:
        print(f"   [.] Exists Assignment: Service {service_id} -> Category {category_id}")


def load_services_and_areas(session: Session):
    """Load initial utility services using the new assignment structure."""
    print("\n--- Loading Services ---")

    # 1. Define Standard Services (unchanged)
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
    
    osbb_shevchenka = get_or_create_service(
        session,
        name='ОСББ "Затишок на Шевченка"',
        defaults={
            "type": "ОСББ",
            "phone_main": "+38 (067) 500-11-22",
            "address_legal": "м. Львів, вул. Шевченка, 12",
            "website": None,
            "is_emergency": False
        }
    )

    # 2. Define Sample Buildings (NEW)
    building_shev = get_or_create_building(
        session,
        city="Львів",
        street_name="Шевченка",
        house_number="12",
        defaults={"district": "Залізничний"}
    )
    
    # 3. Define Assignments (REPLACES Areas)
    
    # A. Citywide Fallback (Dispatcher)
    get_or_create_assignment(
        session,
        service_id=dispatcher.service_id,
        category_id="other",
        coverage_level="citywide",
        defaults={
            "is_primary": True,
            "building_id": None # Global coverage
        }
    )

    # B. Citywide Lighting (Lvivsvitlo)
    if session.get(Category, "lighting"):
        get_or_create_assignment(
            session,
            service_id=lvivsvitlo.service_id,
            category_id="lighting",
            coverage_level="citywide",
            defaults={
                "is_primary": True,
                "building_id": None
            }
        )
    
    # C. Specific Building Assignment (OSBB handles internal property management)
    if session.get(Category, "property_mgmt"):
        get_or_create_assignment(
            session,
            service_id=osbb_shevchenka.service_id,
            category_id="property_mgmt",
            coverage_level="building",
            defaults={
                "is_primary": True,
                "building_id": building_shev.building_id # Direct link to Building ID
            }
        )
    else:
        print("   [!] Warning: Category 'property_mgmt' not found. Skipping OSBB assignment.")
