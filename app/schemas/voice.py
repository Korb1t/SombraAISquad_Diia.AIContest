from pydantic import BaseModel, Field


class VoiceTranscriptionResponse(BaseModel):
    """Response from voice audio transcription"""
    transcription: str = Field(..., description="Full text transcription from audio")
    transcription_successful: bool = Field(..., description="Whether transcription succeeded")
