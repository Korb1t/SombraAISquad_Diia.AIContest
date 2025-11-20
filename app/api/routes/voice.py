from fastapi import APIRouter, HTTPException, UploadFile, File

from app.schemas.voice import (
    VoiceTranscriptionResponse,
    TextDataExtractionRequest,
    ExtractedProblemData
)
from app.services.voice import get_voice_service

router = APIRouter(prefix="/voice", tags=["voice"])


@router.post("/transcribe", response_model=VoiceTranscriptionResponse)
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


@router.post("/extract", response_model=ExtractedProblemData)
async def extract_data_from_text(request: TextDataExtractionRequest) -> ExtractedProblemData:
    """Extract structured data (problem, name, address, city, phone) from user-edited text"""
    try:
        voice_service = get_voice_service()
        return voice_service.extract_data_from_text(request.text)
    except Exception as e:
        raise HTTPException(500, f"Extraction failed: {str(e)}")
