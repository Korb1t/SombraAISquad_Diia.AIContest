"""
End-to-end orchestration API route.
Provides a single endpoint for the complete flow:
problem classification -> service resolution -> appeal generation
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.api.deps import get_db
from app.schemas.orchestration import OrchestrationRequest, OrchestrationResponse
from app.services.orchestrator import OrchestrationService


router = APIRouter(prefix="/solve", tags=["solve problem"])


@router.post("/", response_model=OrchestrationResponse)
async def solve_problem(
    request: OrchestrationRequest,
    db: Session = Depends(get_db)
) -> OrchestrationResponse:
    """
    End-to-end solution for citizen problem resolution.
    
    Takes user information and problem description, then:
    1. Classifies the problem to determine issue category
    2. Finds the responsible service based on category and location
    3. Generates a formal appeal letter
    4. Returns complete solution with all details and service contacts
    
    Args:
        request: OrchestrationRequest containing:
            - name: User's name (should be removed, but remains for compatibility with rest of API)
            - address: Address where problem occurred
            - phone: User's phone (should be removed, but remains for compatibility with rest of API)
            - problem_text: Description of the problem
        db: Database session
        
    Returns:
        OrchestrationResponse with:
            - user_info: User information
            - classification: Problem classification with category and confidence
            - service: Responsible service details and contacts
            - appeal_text: Generated formal letter
            - service_reasoning: Explanation for service assignment
            
    Raises:
        HTTPException: If processing fails at any step
    """
    try:
        service = OrchestrationService(db)
        result = await service.process_complete_flow(request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
