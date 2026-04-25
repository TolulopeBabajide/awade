"""
Context schemas for API request/response validation.

This module contains Pydantic models for context-related operations
including creating, updating, and retrieving context information.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

class ContextBase(BaseModel):
    """Base context schema with common fields."""
    context_text: str = Field(..., description="The context text content")
    context_type: Optional[str] = Field(None, description="Type of context (e.g., cultural, resources, student_background)")

class ContextCreate(ContextBase):
    """Schema for creating a new context."""
    lesson_plan_id: int = Field(..., description="ID of the lesson plan this context belongs to")

class ContextUpdate(BaseModel):
    """Schema for updating an existing context."""
    context_text: Optional[str] = Field(None, description="The context text content")
    context_type: Optional[str] = Field(None, description="Type of context")

class ContextResponse(ContextBase):
    """Schema for context response."""
    context_id: int
    lesson_plan_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ContextListResponse(BaseModel):
    """Schema for list of contexts response."""
    contexts: List[ContextResponse]
    total: int

class ContextSubmissionRequest(BaseModel):
    """Schema for submitting context from frontend."""
    context_text: str = Field(..., description="The context text content")
    context_type: Optional[str] = Field(None, description="Type of context") 