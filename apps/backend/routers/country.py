"""
Country Router for Awade API

This module provides endpoints for managing country data, including CRUD operations
and country information retrieval. It delegates business logic to the CountryService
for clean separation of concerns.

Endpoints:
- /api/countries: CRUD for countries
- /api/countries/search: Search countries
- /api/countries/region/{region}: Get countries by region

Author: Tolulope Babajide
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from apps.backend.database import get_db
from apps.backend.dependencies import get_current_user, require_admin, require_admin_or_educator
from apps.backend.services.country_service import CountryService
from apps.backend.schemas.country import CountryCreate, CountryResponse, CountryUpdate
from apps.backend.models import User

router = APIRouter(prefix="/api/countries", tags=["countries"])

@router.get("/", response_model=List[CountryResponse])
def list_countries(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of all countries with pagination.
    Requires authentication.
    """
    service = CountryService(db)
    return service.get_countries(skip, limit)

@router.post("/", response_model=CountryResponse)
def create_country(
    country: CountryCreate, 
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Create a new country record.
    Requires admin authentication.
    """
    service = CountryService(db)
    return service.create_country(country)

@router.get("/{country_id}", response_model=CountryResponse)
def get_country(
    country_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific country by ID.
    Requires authentication.
    """
    service = CountryService(db)
    return service.get_country(country_id)

@router.put("/{country_id}", response_model=CountryResponse)
def update_country(
    country_id: int,
    country: CountryUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Update a country record.
    Requires admin authentication.
    """
    service = CountryService(db)
    return service.update_country(country_id, country)

@router.delete("/{country_id}")
def delete_country(
    country_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Delete a country record.
    Requires admin authentication.
    """
    service = CountryService(db)
    return service.delete_country(country_id)

@router.get("/search", response_model=List[CountryResponse])
def search_countries(
    q: str = Query(..., description="Search term"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search countries by name, ISO code, or region.
    Requires authentication.
    """
    service = CountryService(db)
    return service.search_countries(q, skip, limit)

@router.get("/region/{region}", response_model=List[CountryResponse])
def get_countries_by_region(
    region: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get countries by region.
    Requires authentication.
    """
    service = CountryService(db)
    return service.get_countries_by_region(region, skip, limit) 