"""
Orchestrator service that coordinates the flow:
1. Classify problem -> get category
2. Resolve service -> get responsible service based on category and address
3. Generate appeal -> create letter text
4. Return complete solution
"""
from sqlmodel import Session
from app.schemas.orchestration import OrchestrationRequest, OrchestrationResponse, ClassificationDetails, ServiceDetails
from app.schemas.base import PersonalInfo
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
        
        # Parse classification result into structured data
        classification = ClassificationDetails(
            category_id=classification_result["category_id"],
            category_name=classification_result["category_name"],
            confidence=classification_result["confidence"],
            is_urgent=classification_result["is_urgent"],
            category_description=classification_result.get("category_description", ""),
            reasoning=classification_result.get("reasoning", "")
        )
        
        # Parse address - extract street name and building number
        # Expected format: "street_name, building_number" or just "street_name"
        street_info = self._parse_address(request.address)
        street_name = street_info["street"]
        building_number = street_info["building"]
        
        # Step 2: Find responsible service based on classification and location
        service_response = self.service_router.find_responsible_service(
            category_id=classification.category_id,
            is_urgent=classification.is_urgent,
            street_name=street_name,
            house_number=building_number
        )
        
        service = ServiceDetails(
            service_name=service_response.service_name,
            phone_main=service_response.phone_main,
            email_main=service_response.email_main,
            address_legal=service_response.address_legal,
            website=service_response.website
        )
        
        # Step 3: Generate appeal text
        appeal_request = AppealRequest(
            problem_text=request.problem_text,
            address=street_name,
            building=building_number
        )
        appeal_text = await generate_appeal_text(appeal_request)
        
        # Step 4: Construct and return orchestrated response
        user_info = PersonalInfo(
            name=request.name,
            address=request.address,
            phone=request.phone
        )
        
        return OrchestrationResponse(
            user_info=user_info,
            classification=classification,
            service=service,
            appeal_text=appeal_text,
            service_reasoning=service_response.reasoning
        )
    
    @staticmethod
    def _parse_address(address: str) -> dict:
        """
        Parse address string to extract street name and building number.
        Expected formats:
        - "вулиця Лева, 42"
        - "Leva street, 42"
        - "вулиця Лева"
        
        Args:
            address: Address string from user
            
        Returns:
            Dict with "street" and "building" keys
        """
        # Try to split by comma
        if "," in address:
            parts = [p.strip() for p in address.split(",")]
            street = parts[0]
            # Try to extract building number from the second part
            building = parts[1] if len(parts) > 1 else ""
            # Extract only the number from building string if it contains text
            building = ''.join(c for c in building.split()[0] if c.isdigit()) or building
        else:
            # No comma, use whole string as street
            street = address.strip()
            building = ""
        
        return {
            "street": street if street else address,
            "building": building if building else "0"
        }
