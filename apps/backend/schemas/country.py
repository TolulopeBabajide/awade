"""
Country schemas for Awade

This module defines Pydantic models for country data validation and serialization.
It includes schemas for creating, updating, and responding with country information.

Author: Tolulope Babajide
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CountryBase(BaseModel):
    """Base country schema with common fields."""
    country_name: str = Field(..., min_length=1, max_length=100, description="Name of the country")
    iso_code: Optional[str] = Field(None, max_length=2, description="ISO 2-letter country code")
    region: Optional[str] = Field(None, max_length=100, description="Geographic region of the country")

class CountryCreate(CountryBase):
    """Schema for creating a new country."""
    pass

class CountryUpdate(BaseModel):
    """Schema for updating an existing country."""
    country_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Name of the country")
    iso_code: Optional[str] = Field(None, max_length=2, description="ISO 2-letter country code")
    region: Optional[str] = Field(None, max_length=100, description="Geographic region of the country")

class CountryResponse(CountryBase):
    """Schema for country response."""
    country_id: int = Field(..., description="Unique identifier for the country")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "country_id": 1,
                "country_name": "Nigeria",
                "iso_code": "NG",
                "region": "West Africa"
            }
        }
