"""
Voice processing service
"""
from typing import BinaryIO
from app.llm.client import get_gemini_client
from app.llm.prompts import AUDIO_TRANSCRIPTION_PROMPT


class VoiceService:
    """Service for voice input processing"""
    
    def __init__(self):
        self.gemini = get_gemini_client()
    
    def transcribe_audio(self, audio_file: BinaryIO, mime_type: str = "audio/webm") -> str:
        """Transcribe audio to Ukrainian text"""
        audio_data = audio_file.read()
        audio_file.seek(0)
        
        response = self.gemini.model.generate_content([
            AUDIO_TRANSCRIPTION_PROMPT,
            {"mime_type": mime_type, "data": audio_data}
        ])
        
        return response.text.strip()


def get_voice_service() -> VoiceService:
    """Get voice service instance"""
    return VoiceService()
