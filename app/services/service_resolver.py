from typing import Optional, Tuple, List, Dict
from sqlmodel import Session, select
from app.db_models import Category, Service, Building, ServiceAssignment
from app.schemas.problems import ServiceResponse

# Визначення категорій, які ми вважаємо "районними"
RA_CATEGORIES = ["roads", "trees", "yard", "infrastructure"]

# Визначення категорій, які є "міськими монополістами" (глобальна відповідальність)
CITYWIDE_MONOPOLISTS_CATEGORIES = ["water_supply", "heating", "gas", "lighting"]

# Назви РА для перевірки, оскільки вони прив'язані citywide
RA_SERVICE_TYPES = ["РА"]

class ServiceRouter:
    """
    Маршрутизатор, який визначає відповідальний сервіс 
    на основі категорії проблеми, терміновості та адреси.
    """
    def __init__(self, session: Session):
        self.session = session
        
    def _find_building(self, street_name: str, house_number: str, city: str = "Львів") -> Optional[Building]:
        """Шукає Building ID за адресою."""
        stmt = (
            select(Building)
            .where(Building.city == city)
            .where(Building.street_name == street_name)
            .where(Building.house_number == house_number)
        )
        return self.session.exec(stmt).first()

    def _format_response(self, service: Service, confidence: float, reasoning: str) -> ServiceResponse:
        """Форматує відповідь для API."""
        return ServiceResponse(
            service_name=service.name_ua,
            service_type=service.type,
            phone_main=service.phone_main,
            email_main=service.email_main,
            is_emergency=service.is_emergency,
            confidence=confidence,
            reasoning=reasoning
        )
        
    def _get_hotline_fallback(self) -> ServiceResponse:
        """Повертає Міську гарячу лінію 1580 як фолбек."""
        hotline = self.session.exec(
            select(Service).where(Service.name_ua == "Міська гаряча лінія 1580")
        ).first()
        
        if hotline:
            return self._format_response(
                hotline,
                confidence=0.1, # Низька впевненість, оскільки це фолбек
                reasoning="Проблема не була ідентифікована жодним спеціалізованим виконавцем. Звернення перенаправлено на Міську гарячу лінію 1580 для ручної диспетчеризації."
            )
        # Крайній випадок, якщо навіть гарячої лінії немає
        return ServiceResponse(
            service_name="Невідома служба",
            service_type="Невідомий",
            phone_main="1580",
            email_main="",
            is_emergency=False,
            confidence=0.0,
            reasoning="Критична помилка: Не вдалося знайти навіть аварійну/диспетчерську службу в базі даних."
        )

    def find_responsible_service(self, category_id: str, is_urgent: bool, street_name: str, house_number: str) -> ServiceResponse:
        """
        Основна логіка пошуку виконавця згідно з ієрархією.
        
        Ієрархія:
        1. Терміновість (is_emergency)
        2. Будинковий рівень (ОСББ/ЛКП по building_id)
        3. Районний рівень (РА по district)
        4. Міський рівень (Монополісти citywide)
        5. Фолбек (1580)
        """
        
        # 0. Визначення Building ID та District (якщо можливо)
        building = self._find_building(street_name, house_number)
        building_id = building.building_id if building else None
        district = building.district if building else None

        # --- 1. ТЕРМІНОВІСТЬ (Emergency Check) ---
        if is_urgent:
            # Шукаємо лише аварійні служби за категорією
            emergency_stmt = (
                select(Service, ServiceAssignment)
                .join(ServiceAssignment, Service.service_id == ServiceAssignment.service_id)
                .where(Service.is_emergency == True)
                .where(ServiceAssignment.category_id == category_id)
            )
            emergency_result = self.session.exec(emergency_stmt).first()
            
            if emergency_result:
                service, _ = emergency_result
                return self._format_response(
                    service,
                    confidence=0.95,
                    reasoning=f"Пріоритет: Знайдено аварійну службу {service.name_ua} для термінової проблеми '{category_id}'."
                )
            
            # Якщо немає специфічної аварійної, повертаємо загальну гарячу лінію як терміновий фолбек
            return self._get_hotline_fallback()
            
        # --- 2. БУДИНКОВА СПЕЦИФІКАЦІЯ (ОСББ/ЛКП) ---
        if category_id not in RA_CATEGORIES and building_id is not None:
            
            # Шукаємо прив'язку за конкретним будинком (найвища специфікація)
            specific_stmt = (
                select(Service, ServiceAssignment)
                .join(ServiceAssignment, Service.service_id == ServiceAssignment.service_id)
                .where(ServiceAssignment.category_id == category_id)
                .where(ServiceAssignment.building_id == building_id)
                .where(ServiceAssignment.is_primary == True)
                .where(Service.type.in_(['ОСББ', 'ЛКП/УК'])) # Лише керуючі компанії
            )
            specific_result = self.session.exec(specific_stmt).first()

            if specific_result:
                service, _ = specific_result
                return self._format_response(
                    service,
                    confidence=0.9,
                    reasoning=f"Адресна прив'язка: Будинок {house_number} на вул. {street_name} обслуговується {service.name_ua}."
                )
            
            # Фолбек на рівні вулиці/району (покриття ЛКП, яке обслуговує вулицю, якщо немає ОСББ)
            # Примітка: Оскільки ми нормалізували БД, тут ми шукаємо лише глобальних виконавців

        # --- 3. РАЙОННА ВІДПОВІДАЛЬНІСТЬ (District Responsibility) ---
        if category_id in RA_CATEGORIES and district and district != "Невідомий":
            search_district = district
            if district.endswith("ий"):
                search_district = district[:-2] + "а"
            
            # Шукаємо сервіс типу "РА" (Районна Адміністрація)
            ra_stmt = (
                select(Service, ServiceAssignment)
                .join(ServiceAssignment, Service.service_id == ServiceAssignment.service_id)
                .where(ServiceAssignment.category_id == category_id)
                .where(Service.type.in_(RA_SERVICE_TYPES))
                .where(Service.name_ua.like(f"%{search_district}%")) # Шукаємо РА по назві району
            )
            ra_result = self.session.exec(ra_stmt).first()
            
            if ra_result:
                service, _ = ra_result
                return self._format_response(
                    service,
                    confidence=0.85,
                    reasoning=f"Районний рівень: Проблема '{category_id}' на вулиці {street_name} належить до юрисдикції {service.name_ua}."
                )

        # --- 4. МІСЬКІ МОНОПОЛІСТИ (Citywide Monopolists) ---
        if category_id in CITYWIDE_MONOPOLISTS_CATEGORIES:
            
            citywide_stmt = (
                select(Service, ServiceAssignment)
                .join(ServiceAssignment, Service.service_id == ServiceAssignment.service_id)
                .where(ServiceAssignment.category_id == category_id)
                .where(ServiceAssignment.coverage_level == 'citywide')
                .where(Service.type == 'КП') # Комунальні підприємства
            )
            citywide_result = self.session.exec(citywide_stmt).first()
            
            if citywide_result:
                service, _ = citywide_result
                return self._format_response(
                    service,
                    confidence=0.7,
                    reasoning=f"Міський монополіст: Проблема '{category_id}' є загальноміською та обслуговується {service.name_ua}."
                )

        # --- 5. ФОЛБЕК НА ГАРЯЧУ ЛІНІЮ ---
        return self._get_hotline_fallback()
