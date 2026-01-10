"""
Input Sanitization Utility

This module provides functions to sanitize and normalize user input
to prevent injection attacks and ensure data consistency.
"""

import re
import html

def sanitize_input(input_str: str) -> str:
    """
    Sanitizes a string input by removing dangerous characters and normalizing whitespace.
    
    Args:
        input_str (str): The raw input string
        
    Returns:
        str: The sanitized string
    """
    if not input_str:
        return ""

    # 1. Normalize whitespace (replace multiple spaces/newlines with single space)
    sanitized = re.sub(r'\s+', ' ', input_str).strip()

    # 2. Remove potential prompt injection patterns
    # This is a basic list and should be expanded based on threat models
    injection_patterns = [
        r'ignore previous instructions',
        r'system prompt',
        r'you are a', # Context dependent, but often used in jailbreaks
        r'bypass',
        r'override'
    ]

    for pattern in injection_patterns:
        sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)

    # 3. Strip control characters (except common ones like newline if needed, but we normalized above)
    # Remove non-printable ASCII characters
    sanitized = re.sub(r'[\x00-\x1F\x7F]', '', sanitized)

    # 4. Basic HTML escaping
    # We keep this lightweight as we are primarily concerned with LLM injection here
    # and preventing stored XSS if data is rendered raw (though React handles this mostly)
    sanitized = html.escape(sanitized, quote=True)

    return sanitized
