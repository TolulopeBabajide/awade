from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from apps.backend.database import get_db
from apps.backend.models import Country
from pydantic import BaseModel

router = APIRouter(prefix="/api/countries", tags=["countries"])

class CountryCreate(BaseModel):
    """Schema for creating a new country."""
    country_name: str
    iso_code: str = None
    region: str = None

class CountryResponse(BaseModel):
    """Schema for country response data."""
    country_id: int
    country_name: str
    iso_code: str = None
    region: str = None
    class Config:
        """Pydantic configuration for ORM mode."""
        orm_mode = True

@router.get("/", response_model=List[CountryResponse])
def list_countries(db: Session = Depends(get_db)):
    """
    Retrieve a list of all countries.

    Args:
        db (Session): Database session dependency.

    Returns:
        List[CountryResponse]: List of countries.
    """
    return db.query(Country).all()

@router.post("/", response_model=CountryResponse)
def create_country(country: CountryCreate, db: Session = Depends(get_db)):
    """
    Create a new country record.

    Args:
        country (CountryCreate): The country data to create.
        db (Session): Database session dependency.

    Returns:
        CountryResponse: The created country.
    """
    db_country = Country(**country.dict())
    db.add(db_country)
    db.commit()
    db.refresh(db_country)
    return db_country 