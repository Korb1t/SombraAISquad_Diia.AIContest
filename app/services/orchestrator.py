"""
Orchestrator service that coordinates the flow:
1. Classify problem -> get category
2. Resolve service -> get responsible service based on category and address
3. Generate appeal -> create letter text
4. Return complete solution
"""
import re
from typing import Dict

from sqlmodel import Session
from app.schemas.orchestration import OrchestrationRequest, OrchestrationResponse
from app.schemas.base import PersonalInfo
from app.schemas.problems_schemas import ProblemClassificationResponse
from app.schemas.appeal import AppealRequest
from app.services.classifier.classifier_factory import get_classifier
from app.services.service_resolver import ServiceRouter
from app.services.appeal import generate_appeal_text


class OrchestrationService:
    """
    Coordinates the complete workflow for problem resolution.
    Orchestrates: classification -> service resolution -> appeal generation
    """
    
    def __init__(self, session: Session):
        self.session = session
        self.classifier = get_classifier(session)
        self.service_router = ServiceRouter(session)
    
    async def process_complete_flow(self, request: OrchestrationRequest) -> OrchestrationResponse:
        """
        Execute the complete end-to-end flow:
        1. Classify the problem
        2. Find responsible service
        3. Generate appeal text
        4. Return orchestrated response
        
        Args:
            request: OrchestrationRequest with user info and problem text
            
        Returns:
            OrchestrationResponse with all processed information
            
        Raises:
            Exception: If any step in the flow fails
        """
        
        # Step 1: Classify the problem
        classification_result = self.classifier.classify_with_category(request.problem_text)
        classification = ProblemClassificationResponse(**classification_result)
        
        # Parse address - extract street name and building number
        street_info = self._parse_address(request.user_info.address)
        street_name = street_info["street"]
        building_number = street_info["building"]
        
        # Step 2: Find responsible service based on classification and location
        service_response = self.service_router.find_responsible_service(
            category_id=classification.category_id,
            is_urgent=classification.is_urgent,
            street_name=street_name,
            house_number=building_number
        )
        
        # Step 3: Generate appeal text
        appeal_request = AppealRequest(
            problem_text=request.problem_text,
            address=request.user_info.address
        )
        appeal_text = await generate_appeal_text(appeal_request)
        
        # Step 4: Construct and return orchestrated response
        user_info = PersonalInfo(
            name=request.user_info.name,
            address=request.user_info.address,
            phone=request.user_info.phone
        )
        
        return OrchestrationResponse(
            user_info=user_info,
            classification=classification,
            service=service_response,
            appeal_text=appeal_text
        )
    
    @staticmethod
    def _parse_address(address: str) -> Dict[str, str]:
        """
        Parse a free-form Ukrainian address and extract street & house number.
        
        Handles inputs like:
        - "Україна, область Львівська, місто Львів, вулиця Володимира Великого 10б, кв 54"
        - "Львів, проспект Червоної Калини 36"
        - "Стрийська, 45"
        """
        if not address:
            return {"street": "", "building": ""}

        cleaned = address.replace("\n", " ")
        parts = [p.strip() for p in re.split(r"[;,]", cleaned) if p.strip()]

        street_segment = ""
        house_number = ""

        street_keywords = [
            "вулиця",
            "вул",
            "улица",
            "проспект",
            "просп",
            "площа",
            "пл",
            "бульвар",
            "бул",
            "провулок",
            "пров",
            "въезд",
            "street",
        ]
        house_pattern = re.compile(r"\b(\d+\s*[а-яА-Яa-zA-Z]?)\b")

        apartment_tokens = {"кв", "квартира", "apt", "apartment"}

        for idx in range(len(parts) - 1, -1, -1):
            segment = parts[idx]
            lower_segment = segment.lower()
            if any(token in lower_segment.split() for token in apartment_tokens):
                continue

            match = house_pattern.search(segment)
            if match:
                house_number = match.group(1).replace(" ", "")
                prefix = segment[: match.start()].strip()
                if prefix:
                    street_segment = prefix
                elif idx > 0:
                    street_segment = parts[idx - 1]
                else:
                    street_segment = segment
                break

        if not street_segment and parts:
            street_segment = parts[-1]

        street = OrchestrationService._cleanup_street_name(street_segment, street_keywords)

        return {
            "street": street,
            "building": house_number,
        }

    @staticmethod
    def _cleanup_street_name(segment: str, keywords: list[str]) -> str:
        """Remove country/city prefixes and street keywords."""
        if not segment:
            return ""

        lowered = segment.lower()
        removal_tokens = ["україна", "область", "район", "місто", "м.", "обл.", "р-н"]
        for token in removal_tokens:
            if lowered.startswith(token):
                segment = segment[len(token) :].strip(", .")
                lowered = segment.lower()

        for keyword in keywords:
            pattern = re.compile(rf"\b{keyword}\.?\b", re.IGNORECASE)
            if pattern.search(segment):
                segment = pattern.sub("", segment).strip()
                break

        segment = re.sub(r"\s+", " ", segment)
        return segment.strip()
