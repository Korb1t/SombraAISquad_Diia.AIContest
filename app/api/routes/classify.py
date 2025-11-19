from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import Session

from app.api.deps import get_db
from app.schemas.problems import (
    ProblemRequest,
    ProblemClassificationResponse,
    VoiceTranscriptionResponse,
    TextDataExtractionRequest
)
from app.services.classifier.classifier_factory import get_classifier
from app.services.voice import get_voice_service

router = APIRouter(prefix="/classify", tags=["classification"])


@router.post("/voice/transcribe", response_model=VoiceTranscriptionResponse)
async def transcribe_voice(
    audio: UploadFile = File(..., description="Audio file (mp3, wav, webm, m4a, x-m4a, mp4, ogg)")
) -> VoiceTranscriptionResponse:
    """Transcribe audio to Ukrainian text for user editing"""
    allowed_types = ["audio/mpeg", "audio/mp3", "audio/wav", "audio/webm", "audio/ogg", "audio/m4a", "audio/mp4", "audio/x-m4a"]
    if audio.content_type not in allowed_types:
        raise HTTPException(400, f"Unsupported format: {audio.content_type}")
    
    try:
        voice_service = get_voice_service()
        transcription = voice_service.transcribe_audio(audio.file, audio.content_type or "audio/webm")
        return VoiceTranscriptionResponse(transcription=transcription, transcription_successful=True)
    except Exception as e:
        raise HTTPException(500, f"Transcription failed: {str(e)}")


@router.post("/voice/extract", response_model=ProblemRequest)
async def extract_data_from_text(request: TextDataExtractionRequest) -> ProblemRequest:
    """Extract structured data (problem, name, address, phone) from user-edited text"""
    try:
        voice_service = get_voice_service()
        return voice_service.extract_data_from_text(request.text)
    except Exception as e:
        raise HTTPException(500, f"Extraction failed: {str(e)}")


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