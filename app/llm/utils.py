"""
LLM utilities
"""
import json


def parse_llm_json(content: str) -> dict:
    """Parse JSON from LLM response, removing markdown if present"""
    content = content.strip()
    if content.startswith("```"):
        content = content.split("```")[1].lstrip("json").strip()
    return json.loads(content)
