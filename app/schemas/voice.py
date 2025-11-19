from pydantic import BaseModel, Field


class VoiceTranscriptionResponse(BaseModel):
    """Response from voice audio transcription"""
    transcription: str = Field(..., description="Full text transcription from audio")
    transcription_successful: bool = Field(..., description="Whether transcription succeeded")


class TextDataExtractionRequest(BaseModel):
    """Request to extract structured data from text (after user edits)"""
    text: str = Field(..., min_length=5, description="User-edited transcription text")


class ExtractedProblemData(BaseModel):
    """Extracted structured data from text"""
    problem_text: str = Field(..., description="Problem description")
    user_name: str | None = Field(default=None, description="Applicant name")
    user_address: str | None = Field(default=None, description="Applicant address")
    user_city: str | None = Field(default=None, description="Applicant city")
    user_phone: str | None = Field(default=None, description="Applicant phone")
