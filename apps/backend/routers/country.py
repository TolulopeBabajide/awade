from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from apps.backend.database import get_db
from apps.backend.dependencies import get_current_user, require_admin, require_admin_or_educator, get_optional_current_user
from apps.backend.models import Country, User
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
def list_countries(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of all countries.
    Requires authentication.
    """
    return db.query(Country).all()

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
    # Check if country already exists
    existing_country = db.query(Country).filter(Country.country_name == country.country_name).first()
    if existing_country:
        raise HTTPException(status_code=400, detail="Country already exists")
    
    db_country = Country(**country.dict())
    db.add(db_country)
    db.commit()
    db.refresh(db_country)
    return db_country

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
    country = db.query(Country).filter(Country.country_id == country_id).first()
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")
    return country

@router.put("/{country_id}", response_model=CountryResponse)
def update_country(
    country_id: int,
    country: CountryCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Update a country record.
    Requires admin authentication.
    """
    db_country = db.query(Country).filter(Country.country_id == country_id).first()
    if not db_country:
        raise HTTPException(status_code=404, detail="Country not found")
    
    # Check if new name conflicts with existing country
    existing_country = db.query(Country).filter(
        Country.country_name == country.country_name,
        Country.country_id != country_id
    ).first()
    if existing_country:
        raise HTTPException(status_code=400, detail="Country name already exists")
    
    # Update fields
    db_country.country_name = country.country_name
    db_country.iso_code = country.iso_code
    db_country.region = country.region
    
    db.commit()
    db.refresh(db_country)
    return db_country

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
    db_country = db.query(Country).filter(Country.country_id == country_id).first()
    if not db_country:
        raise HTTPException(status_code=404, detail="Country not found")
    
    # Check if country is being used by curricula
    if db_country.curricula:
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete country that has associated curricula"
        )
    
    db.delete(db_country)
    db.commit()
    return {"message": "Country deleted successfully"} 