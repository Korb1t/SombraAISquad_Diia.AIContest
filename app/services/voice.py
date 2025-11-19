"""
Voice processing service
"""
from typing import BinaryIO
from app.llm.client import get_gemini_client, get_llm
from app.llm.utils import parse_llm_json
from app.llm.prompts import AUDIO_TRANSCRIPTION_PROMPT, EXTRACT_DATA_FROM_TEXT_PROMPT
from app.schemas.problems import ProblemRequest


class VoiceService:
    """Service for voice input processing"""
    
    def __init__(self):
        self.gemini = get_gemini_client()
        self.llm = get_llm()
    
    def transcribe_audio(self, audio_file: BinaryIO, mime_type: str = "audio/webm") -> str:
        """Transcribe audio to Ukrainian text"""
        audio_data = audio_file.read()
        audio_file.seek(0)
        
        response = self.gemini.model.generate_content([
            AUDIO_TRANSCRIPTION_PROMPT,
            {"mime_type": mime_type, "data": audio_data}
        ])
        
        return response.text.strip()
    
    def extract_data_from_text(self, text: str) -> ProblemRequest:
        """Extract structured data from user-edited text using LLM"""
        prompt = EXTRACT_DATA_FROM_TEXT_PROMPT.format(text=text)
        response = self.llm.invoke(prompt)
        data = parse_llm_json(response.content)
        
        return ProblemRequest(
            problem_text=data.get("problem_text") or text,
            user_name=data.get("user_name"),
            user_address=data.get("user_address"),
            user_phone=data.get("user_phone")
        )


def get_voice_service() -> VoiceService:
    """Get voice service instance"""
    return VoiceService()
