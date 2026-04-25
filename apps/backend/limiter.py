"""
Rate Limiter Module

This module provides a shared Limiter instance for rate limiting across the application.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

# Initialize limiter with remote address as the key function
limiter = Limiter(key_func=get_remote_address)
