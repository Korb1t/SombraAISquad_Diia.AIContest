from fastapi import APIRouter, HTTPException

from app.schemas.appeal import AppealRequest, AppealResponse
from app.services.appeal import generate_appeal_text

router = APIRouter(prefix="/appeal", tags=["appeal"])


@router.post("/generate", response_model=AppealResponse)
async def generate_appeal(request: AppealRequest) -> AppealResponse:
    """
    Generate a formal appeal based on problem description and address.
    Uses LLM to rephrase informal problem description into formal language.
    """
    try:
        letter_text = await generate_appeal_text(request)
        return AppealResponse(letter_text=letter_text)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate appeal: {str(e)}"
        )
