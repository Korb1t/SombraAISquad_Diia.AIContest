from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.api.deps import get_db
from app.schemas.problems import ProblemRequest, ProblemClassificationResponse
from app.services.classifier import get_classifier

router = APIRouter(prefix="/classify", tags=["classification"])


@router.post("/", response_model=ProblemClassificationResponse)
async def classify_problem(
    request: ProblemRequest,
    db: Session = Depends(get_db),
) -> ProblemClassificationResponse:
    """
    Classify user's utility problem
    
    Process:
    1. Check urgency with LLM
    2. Uses RAG to search for similar examples
    3. Few-shot classification via LLM
    4. Returns category with confidence score and urgency
    """
    classifier = get_classifier(db)
    
    try:
        result = classifier.classify_with_category(request.problem_text)
        return ProblemClassificationResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification error: {str(e)}")