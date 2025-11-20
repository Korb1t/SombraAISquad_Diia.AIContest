from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.api.deps import get_db
from app.core.logging import get_logger
from app.schemas.problems import ProblemRequest, ProblemClassificationResponse
from app.services.classifier.classifier_factory import get_classifier

router = APIRouter(prefix="/classify", tags=["classification"])
logger = get_logger(__name__)


@router.post("/", response_model=ProblemClassificationResponse)
async def classify_problem(
    request: ProblemRequest,
    db: Session = Depends(get_db)
) -> ProblemClassificationResponse:
    """Classify utility problem using RAG + few-shot learning"""
    logger.info(f"Classifying problem, text length: {len(request.problem_text)} characters")
    try:
        classifier = get_classifier(db)
        result = classifier.classify_with_category(request.problem_text)
        logger.info(f"Classification result: category={result.get('category_name')}, confidence={result.get('confidence'):.2f}")
        return ProblemClassificationResponse(**result)
    except Exception as e:
        logger.error(f"Classification error: {str(e)}")
        raise HTTPException(500, f"Classification error: {str(e)}")