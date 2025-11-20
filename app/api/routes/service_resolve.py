from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.api.deps import get_db
from app.schemas.services import IssueRequest, ServiceResponse
from app.services.service_resolver import ServiceRouter

router = APIRouter(prefix="/resolve_service", tags=["resolve service"])

@router.post("/", response_model=ServiceResponse)
def route_problem_to_service(
    request: IssueRequest,
    session: Session = Depends(get_db)
):
    """
    Classifies the problem and determines the responsible
    utility based on category, urgency and address.
    """
    try:
        service_router = ServiceRouter(session)
        
        responsible_service = service_router.find_responsible_service(
            category_id=request.category_id,
            is_urgent=request.is_urgent,
            street_name=request.street_name,
            house_number=request.house_number
        )
        
        return responsible_service
    
    except Exception as e:
        print(f"Error during service routing: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during problem routing.")