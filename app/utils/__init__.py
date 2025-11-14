# SAMPLE UTILITY FUNCTIONS FOR TEXT PROCESSING

import re
import unicodedata

def normalize_text(text: str, 
                  lowercase: bool = True,
                  remove_accents: bool = True,
                  remove_extra_whitespace: bool = True,
                  remove_punctuation: bool = False) -> str:
    """
    Normalize text by applying various transformations.
    
    Args:
        text: Input text to normalize
        lowercase: Convert to lowercase
        remove_accents: Remove accent marks
        remove_extra_whitespace: Remove extra whitespace and trim
        remove_punctuation: Remove punctuation marks
    
    Returns:
        Normalized text string
    """
    if not text:
        return ""
    
    result = text
    
    # Remove accents
    if remove_accents:
        result = unicodedata.normalize('NFD', result)
        result = ''.join(c for c in result if unicodedata.category(c) != 'Mn')
    
    # Convert to lowercase
    if lowercase:
        result = result.lower()
    
    # Remove punctuation
    if remove_punctuation:
        result = re.sub(r'[^\w\s]', '', result)
    
    # Remove extra whitespace
    if remove_extra_whitespace:
        result = ' '.join(result.split())
    
    return result

def clean_whitespace(text: str) -> str:
    """Remove extra whitespace and normalize line breaks."""
    return ' '.join(text.split())

def remove_special_chars(text: str, keep_spaces: bool = True) -> str:
    """Remove special characters, optionally keeping spaces."""
    pattern = r'[^\w\s]' if keep_spaces else r'[^\w]'
    return re.sub(pattern, '', text)