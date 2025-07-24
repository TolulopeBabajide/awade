from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from apps.backend.database import get_db
from apps.backend.models import Country
from pydantic import BaseModel

router = APIRouter(prefix="/api/countries", tags=["countries"])

class CountryCreate(BaseModel):
    country_name: str
    iso_code: str = None
    region: str = None

class CountryResponse(BaseModel):
    country_id: int
    country_name: str
    iso_code: str = None
    region: str = None
    class Config:
        orm_mode = True

@router.get("/", response_model=List[CountryResponse])
def list_countries(db: Session = Depends(get_db)):
    return db.query(Country).all()

@router.post("/", response_model=CountryResponse)
def create_country(country: CountryCreate, db: Session = Depends(get_db)):
    db_country = Country(**country.dict())
    db.add(db_country)
    db.commit()
    db.refresh(db_country)
    return db_country 