"""
Service for appeal generation.
"""
from app.schemas.appeal import AppealRequest
from app.llm.prompts import APPEAL_TEMPLATE
from app.llm.client import SimpleLLM


def format_appeal_prompt(request: AppealRequest) -> str:
    """
    Format appeal generation prompt from request data.
    
    Args:
        request: Appeal request with problem text, street, and building
        
    Returns:
        Formatted prompt for LLM
    """
    return APPEAL_TEMPLATE.format(
        problem_text=request.problem_text,
        street=request.address,
        building=request.building
    )


async def generate_appeal_text(request: AppealRequest) -> str:
    """
    Generate appeal text using LLM.
    
    Args:
        request: Appeal request with problem text and address
        
    Returns:
        Generated appeal text
    """
    # Prepare prompt with user data
    prompt = format_appeal_prompt(request)
    
    # Generate appeal using LLM
    llm = SimpleLLM()
    letter_text = await llm.generate_text(prompt, temperature=0.7)
    
    return letter_text.strip()
