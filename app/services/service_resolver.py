from typing import Optional
from sqlmodel import Session, select
from app.db_models import Category
from app.db_models import Service, Building, ServiceAssignment
from app.schemas.services import ServiceResponse, ServiceInfo

# TODO: Move category definitions out
# Definition of categories we consider "district-level"
RA_CATEGORIES = ["roads", "trees", "yard", "infrastructure"]

# Definition of categories handled by "citywide monopolists" (global responsibility)
CITYWIDE_MONOPOLISTS_CATEGORIES = ["water_supply", "heating", "gas", "lighting"]

# Names of district administrations for validation, since they are tied to citywide
RA_SERVICE_TYPES = ["РА"]

# TODO: extract hardcoded strings and magic confidence numbers
class ServiceRouter:
    """
    Router that determines the responsible service
    based on problem category, urgency, and address.
    """
    def __init__(self, session: Session):
        self.session = session
        
    def _find_building(self, street_name: str, house_number: str, city: str = "Львів") -> Optional[Building]:
        """Searches for Building ID by address."""
        stmt = (
            select(Building)
            .where(Building.city == city)
            .where(Building.street_name == street_name)
            .where(Building.house_number == house_number)
        )
        return self.session.exec(stmt).first()

    def _format_response(
        self, service: Service, confidence: float, reasoning: str,
        category_id: str = "", category_name: str = "", is_urgent: bool = False
    ) -> ServiceResponse:
        """Formats the response for the API."""
        return ServiceResponse(
            category_id=category_id,
            category_name=category_name,
            confidence=confidence,
            is_urgent=is_urgent,
            service_info=ServiceInfo(
                service_type=service.type,
                service_name=service.name_ua,
                service_phone=service.phone_main,
                service_email=service.email_main,
                service_address=service.address_legal,
                service_website=service.website,
            ),
            reasoning=reasoning
        )
        
    def _get_hotline_fallback(self, category_id: str, category_name: str, is_urgent: bool) -> ServiceResponse:
        """Returns the City Hotline 1580 as a fallback."""
        hotline = self.session.exec(
            select(Service).where(Service.name_ua == "Міська гаряча лінія 1580")
        ).first()
        
        if hotline:
            if is_urgent:
                reasoning = "Не було знайдено спеціальну аварійну службу для цієї проблеми. Звернення перенаправлено на Міську гарячу лінію 1580 для ручної диспетчеризації."
            else:
                reasoning = "Проблема не була ідентифікована жодним спеціалізованим виконавцем. Звернення перенаправлено на Міську гарячу лінію 1580 для ручної диспетчеризації."
        
            return self._format_response(
                hotline,
                confidence=0.1,
                reasoning=reasoning,
                category_id=category_id,
                category_name=category_name,
                is_urgent=is_urgent
            )
        # Extreme case if even the hotline is not found
        return ServiceResponse(
            category_id=category_id,
            category_name=category_name,
            confidence=0.0,
            is_urgent=is_urgent,
            service_info=ServiceInfo(
                service_type="Гаряча лінія",
                service_name="Невідома служба",
                service_phone="1580",
                service_email=None,
                service_address=None,
                service_website=None,
            ),
            reasoning="Критична помилка: Не вдалося знайти навіть аварійну/диспетчерську службу в базі даних."
        )

    def find_responsible_service(self, category_id: str, is_urgent: bool, street_name: str, house_number: str) -> ServiceResponse:
        """
        Main logic for finding the executor according to hierarchy.
        
        Hierarchy:
        1. Urgency (is_emergency)
        2. Building-level responsibility (OSBB/LKP via building_id)
        3. District level (district administrations)
        4. City level (citywide monopolists)
        5. Fallback (1580)
        """
        
        # 0. Determine Building ID and District (if possible)
        building = self._find_building(street_name, house_number)
        building_id = building.building_id if building else None
        district = building.district if building else None

        # --- 1. URGENCY (Emergency Check) ---
        if is_urgent:
            # Search only for emergency services by category
            emergency_stmt = (
                select(Service, ServiceAssignment, Category)
                .join(ServiceAssignment, Service.service_id == ServiceAssignment.service_id)
                .join(Category, Category.id == ServiceAssignment.category_id)
                .where(Service.is_emergency.is_(True))
                .where(ServiceAssignment.category_id == category_id)
            )
            emergency_result = self.session.exec(emergency_stmt).first()
            
            if emergency_result:
                service, assignment, category = emergency_result
                return self._format_response(
                    service,
                    confidence=0.95,
                    reasoning=f"Пріоритет: Знайдено аварійну службу {service.name_ua} для термінової проблеми '{category_id}'.",
                    category_id=category_id,
                    category_name=category.name,
                    is_urgent=True
                )

            # If no specific emergency service, return the general hotline as an urgent fallback
            return self._get_hotline_fallback(category_id=category_id, category_name=category.name, is_urgent=True)

        # --- 2. BUILDING-LEVEL RESPONSIBILITY (OSBB/LKP) ---
        if category_id not in RA_CATEGORIES and building_id is not None:
            
            # Search for assignment by specific building (highest specificity)
            specific_stmt = (
                select(Service, ServiceAssignment, Category)
                .join(ServiceAssignment, Service.service_id == ServiceAssignment.service_id)
                .join(Category, Category.id == ServiceAssignment.category_id)
                .where(ServiceAssignment.category_id == category_id)
                .where(ServiceAssignment.building_id == building_id)
                .where(ServiceAssignment.is_primary)
                .where(Service.type.in_(['ОСББ', 'ЛКП/УК'])) # Лише керуючі компанії
            )
            specific_result = self.session.exec(specific_stmt).first()

            if specific_result:
                service, assignment, category = specific_result
                return self._format_response(
                    service,
                    confidence=0.9,
                    reasoning=f"Адресна прив'язка: Будинок {house_number} на вул. {street_name} обслуговується {service.name_ua}.",
                    category_id=category_id,
                    category_name=category.name,
                    is_urgent=is_urgent
                )
            
            # Fallback at street/district level (LKP covering the street if no OSBB)

        # --- 3. DISTRICT RESPONSIBILITY ---
        if category_id in RA_CATEGORIES and district and district != "Невідомий":
            search_district = district
            if district.endswith("ий"):
                search_district = district[:-2] + "а"
            
            # Search for service of type "РА" (District Administration)
            like_pattern = f"%{search_district}%"
            ra_stmt = (
                select(Service, ServiceAssignment, Category)
                .join(ServiceAssignment, Service.service_id == ServiceAssignment.service_id)
                .join(Category, Category.id == ServiceAssignment.category_id)
                .where(ServiceAssignment.category_id == category_id)
                .where(Service.type.in_(RA_SERVICE_TYPES))
                .where(Service.name_ua.like(like_pattern)) # Search RA by district name
            )
            ra_result = self.session.exec(ra_stmt).first()
            
            if ra_result:
                service, assignment, category = ra_result
                return self._format_response(
                    service,
                    confidence=0.85,
                    reasoning=f"Районний рівень: Проблема '{category_id}' на вулиці {street_name} належить до юрисдикції {service.name_ua}.",
                    category_id=category_id,
                    category_name=category.name,
                    is_urgent=is_urgent
                )

        # --- 4. Citywide Monopolists ---
        if category_id in CITYWIDE_MONOPOLISTS_CATEGORIES:
            
            citywide_stmt = (
                select(Service, ServiceAssignment, Category)
                .join(ServiceAssignment, Service.service_id == ServiceAssignment.service_id)
                .join(Category, Category.id == ServiceAssignment.category_id)
                .where(ServiceAssignment.category_id == category_id)
                .where(ServiceAssignment.coverage_level == 'citywide')
                .where(Service.type == 'КП')
            )
            citywide_result = self.session.exec(citywide_stmt).first()
            
            if citywide_result:
                service, assignment, category = citywide_result
                return self._format_response(
                    service,
                    confidence=0.7,
                    reasoning=f"Міський монополіст: Проблема '{category_id}' є загальноміською та обслуговується {service.name_ua}.",
                    category_id=category_id,
                    category_name=category.name,
                    is_urgent=is_urgent
                )

        # --- 5. HOTLINE FALLBACK ---
        return self._get_hotline_fallback(category_id=category_id, category_name=category.name, is_urgent=is_urgent)
