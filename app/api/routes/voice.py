from fastapi import APIRouter, HTTPException, UploadFile, File

from app.core.logging import get_logger
from app.schemas.voice import VoiceTranscriptionResponse
from app.services.voice import get_voice_service

router = APIRouter(prefix="/voice", tags=["voice"])
logger = get_logger(__name__)


@router.post("/transcribe", response_model=VoiceTranscriptionResponse)
async def transcribe_voice(
    audio: UploadFile = File(..., description="Audio file (mp3, wav, webm, m4a, x-m4a, mp4, ogg)")
) -> VoiceTranscriptionResponse:
    """Transcribe audio to Ukrainian text for user editing"""
    logger.info(f"Transcribing audio file: {audio.filename}, type: {audio.content_type}")
    allowed_types = ["audio/mpeg", "audio/mp3", "audio/wav", "audio/webm", "audio/ogg", "audio/m4a", "audio/mp4", "audio/x-m4a"]
    if audio.content_type not in allowed_types:
        raise HTTPException(400, f"Unsupported format: {audio.content_type}")
    
    try:
        voice_service = get_voice_service()
        transcription = voice_service.transcribe_audio(audio.file, audio.content_type or "audio/webm")
        logger.info(f"Transcription successful, length: {len(transcription)} characters")
        return VoiceTranscriptionResponse(transcription=transcription, transcription_successful=True)
    except Exception as e:
        logger.error(f"Transcription failed: {str(e)}")
        raise HTTPException(500, f"Transcription failed: {str(e)}")
