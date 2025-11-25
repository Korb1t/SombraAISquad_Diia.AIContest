import re
from typing import Optional, List

from sqlalchemy import func, or_
from sqlmodel import Session, select

from app.db_models import Category
from app.db_models import Service, Building, ServiceAssignment
from app.schemas.services import ServiceResponse, ServiceInfo

# TODO: Move category definitions out
# Definition of categories we consider "district-level"
RA_CATEGORIES = ["roads", "trees", "yard", "parking"]

# Definition of categories handled by "citywide monopolists" (global responsibility)
CITYWIDE_MONOPOLISTS_CATEGORIES = ["water_supply", "heating", "gas", "lighting", "animals"]

# This is not used, but for display what other categories exist
BUILDING_LEVEL_CATEGORIES = ["sewage", "elevator", "cleaning", "roof", "entrance_doors", "noise"]

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
        
    @staticmethod
    def _normalize_house_number(number: Optional[str]) -> str:
        if not number:
            return ""
        return number.strip().lower().replace(" ", "")

    @staticmethod
    def _digits_only(number: str) -> str:
        return "".join(ch for ch in number if ch.isdigit())

    @staticmethod
    def _normalize_street(name: str) -> str:
        cleaned = name.lower()
        cleaned = re.sub(r"[.,]", " ", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned

    @staticmethod
    def _street_tokens(name: str) -> List[str]:
        stopwords = {"україна", "львів", "місто", "м", "область", "обл", "район", "р-н"}
        words = [w for w in ServiceRouter._normalize_street(name).split() if w not in stopwords]
        return [w for w in words if len(w) > 2]

    def _find_building(self, street_name: str, house_number: str, city: str = "Львів") -> Optional[Building]:
        """Fuzzy search for building by address."""
        street_tokens = self._street_tokens(street_name)
        normalized_house = self._normalize_house_number(house_number)
        house_variants = {normalized_house} if normalized_house else set()
        digits_variant = self._digits_only(normalized_house)
        if digits_variant and digits_variant != normalized_house:
            house_variants.add(digits_variant)

        stmt = select(Building).where(Building.city == city)

        if street_tokens:
            like_filters = [
                func.lower(Building.street_name).like(f"%{token}%")
                for token in street_tokens[:2]
            ]
            stmt = stmt.where(or_(*like_filters))
        else:
            stmt = stmt.where(func.lower(Building.street_name).like(f"%{self._normalize_street(street_name)}%"))

        candidates = self.session.exec(stmt).all()
        if not candidates:
            return None

        def matches(building: Building) -> bool:
            normalized_existing = self._normalize_house_number(building.house_number)
            if normalized_existing in house_variants:
                return True
            digits_existing = self._digits_only(normalized_existing)
            return digits_existing and digits_variant and digits_existing == digits_variant

        for candidate in candidates:
            if matches(candidate):
                return candidate

        return candidates[0]

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
                reasoning = "Для надання термінової допомоги, звертайтесь на Міську гарячу лінію 1580 для ручної диспетчеризації."
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
            category_obj = self.session.exec(select(Category).where(Category.id == category_id)).first()
            category_name = category_obj.name if category_obj else ""

            return self._get_hotline_fallback(category_id=category_id, category_name=category_name, is_urgent=True)

        # --- 2. BUILDING-LEVEL RESPONSIBILITY (OSBB/LKP) ---
        if category_id not in RA_CATEGORIES and category_id not in CITYWIDE_MONOPOLISTS_CATEGORIES and building_id is not None:
            
            # Search for assignment by specific building (highest specificity)
            specific_stmt = (
                select(Service, ServiceAssignment, Category)
                .join(ServiceAssignment, Service.service_id == ServiceAssignment.service_id)
                .join(Category, Category.id == ServiceAssignment.category_id)
                .where(ServiceAssignment.building_id == building_id)
                .where(ServiceAssignment.is_primary)
                .where(Service.type.in_(['ОСББ', 'ЛКП/УК']))
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
        category_obj = self.session.exec(select(Category).where(Category.id == category_id)).first()
        category_name = category_obj.name if category_obj else ""

        return self._get_hotline_fallback(category_id=category_id, category_name=category_name, is_urgent=is_urgent)
