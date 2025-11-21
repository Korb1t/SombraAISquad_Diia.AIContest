"""
Security utilities for input sanitization
"""
import re


def sanitize_prompt_input(text: str, max_length: int = 2000) -> str:
    """
    Sanitize user input before passing to LLM prompt
    
    Args:
        text: User input text
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Limit length
    text = text[:max_length]
    
    # Remove potential prompt injection patterns
    # Remove excessive newlines (keep max 2 consecutive)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Remove instruction-like patterns
    dangerous_patterns = [
        r'ignore\s+(all\s+)?(previous|above|prior)\s+instructions?',
        r'system\s*:',
        r'assistant\s*:',
        r'new\s+instructions?',
        r'you\s+are\s+now',
        r'act\s+as',
        r'pretend\s+to\s+be',
    ]
    
    for pattern in dangerous_patterns:
        text = re.sub(pattern, '[FILTERED]', text, flags=re.IGNORECASE)
    
    return text.strip()


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe logging
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    if not filename:
        return "unknown"
    
    # Remove path separators
    filename = filename.replace('/', '_').replace('\\', '_')
    
    # Keep only safe characters
    filename = re.sub(r'[^\w\s\-\.]', '', filename)
    
    # Limit length
    return filename[:255]
