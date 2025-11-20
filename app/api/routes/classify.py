from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.api.deps import get_db
from app.schemas.problems import ProblemRequest, ProblemClassificationResponse
from app.services.classifier.classifier_factory import get_classifier

router = APIRouter(prefix="/classify", tags=["classification"])


@router.post("/", response_model=ProblemClassificationResponse)
async def classify_problem(
    request: ProblemRequest,
    db: Session = Depends(get_db)
) -> ProblemClassificationResponse:
    """Classify utility problem using RAG + few-shot learning"""
    try:
        classifier = get_classifier(db)
        result = classifier.classify_with_category(request.problem_text)
        return ProblemClassificationResponse(**result)
    except Exception as e:
        raise HTTPException(500, f"Classification error: {str(e)}")