from pathlib import Path

# Get prompts directory
PROMPTS_DIR = Path(__file__).parent / "prompts"


def _load_prompt(filename: str) -> str:
    """Load prompt from text file"""
    prompt_path = PROMPTS_DIR / filename
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


# Classifier prompts
CLASSIFIER_PROMPT_TEMPLATE = _load_prompt("classifier.txt")

# Letter generation prompts
LETTER_SYSTEM_PROMPT = _load_prompt("letter_system.txt")
LETTER_USER_PROMPT = _load_prompt("letter_user.txt")

# Voice input prompts
AUDIO_TRANSCRIPTION_PROMPT = _load_prompt("audio_transcription.txt")
