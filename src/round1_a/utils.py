import re
from typing import Dict, Any

def clean_text(text: str) -> str:
    """Clean and normalize extracted text"""
    text = re.sub(r'\s+', ' ', text)  # Collapse whitespace
    text = re.sub(r'^\W+|\W+$', '', text)  # Trim non-alphanum
    return text.strip()

def is_heading_candidate(text: str) -> bool:
    """Determine if text is likely a heading"""
    # Skip common non-heading elements
    if not text or len(text) > 200:  # Too long for heading
        return False
    if text.isdigit():  # Page numbers
        return False
    if re.match(r'^\d+\.\d+\.\d+', text):  # Version numbers
        return False
    if re.match(r'^[A-Za-z]\.\s', text):  # List items
        return False
    if text.lower() in {'copyright', 'confidential', 'page', 'date'}:
        return False
    return True