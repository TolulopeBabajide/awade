"""
Country Service for Awade

This module provides service methods for managing country data, including CRUD operations
and country information retrieval. It handles all business logic related to countries,
separating concerns from the router layer.

Author: Tolulope Babajide
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException

import sys
import os

# Add parent directories to Python path for imports
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(parent_dir)
sys.path.extend([parent_dir, root_dir])
from apps.backend.models import Country
import sys
import os

# Add parent directories to Python path for imports
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(parent_dir)
sys.path.extend([parent_dir, root_dir])
from apps.backend.schemas.country import CountryCreate, CountryResponse, CountryUpdate

class CountryService:
    """Service class for country operations."""
    
    def __init__(self, db: Session):
        """
        Initialize the CountryService with a database session.
        
        Args:
            db (Session): SQLAlchemy database session
        """
        self.db = db
    
    def get_countries(self, skip: int = 0, limit: int = 100) -> List[CountryResponse]:
        """
        Get all countries with pagination.
        
        Args:
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return
            
        Returns:
            List[CountryResponse]: List of country responses
            
        Raises:
            HTTPException: If retrieval fails
        """
        try:
            countries = self.db.query(Country).offset(skip).limit(limit).all()
            return [self._create_country_response(country) for country in countries]
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while retrieving countries: {str(e)}"
            )
    
    def get_country(self, country_id: int) -> CountryResponse:
        """
        Get a specific country by ID.
        
        Args:
            country_id (int): Country ID
            
        Returns:
            CountryResponse: Country response
            
        Raises:
            HTTPException: If country not found
        """
        try:
            country = self.db.query(Country).filter(Country.country_id == country_id).first()
            if not country:
                raise HTTPException(status_code=404, detail="Country not found")
            
            return self._create_country_response(country)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while retrieving the country: {str(e)}"
            )
    
    def create_country(self, country_data: CountryCreate) -> CountryResponse:
        """
        Create a new country record.
        
        Args:
            country_data (CountryCreate): Country creation data
            
        Returns:
            CountryResponse: Created country response
            
        Raises:
            HTTPException: If country already exists or creation fails
        """
        try:
            # Check if country already exists
            existing_country = self.db.query(Country).filter(
                Country.country_name == country_data.country_name
            ).first()
            if existing_country:
                raise HTTPException(status_code=400, detail="Country already exists")
            
            # Create new country
            country = Country(**country_data.dict())
            self.db.add(country)
            self.db.commit()
            self.db.refresh(country)
            
            return self._create_country_response(country)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while creating the country: {str(e)}"
            )
    
    def update_country(self, country_id: int, country_data: CountryUpdate) -> CountryResponse:
        """
        Update a country record.
        
        Args:
            country_id (int): Country ID
            country_data (CountryUpdate): Update data
            
        Returns:
            CountryResponse: Updated country response
            
        Raises:
            HTTPException: If country not found or update fails
        """
        try:
            country = self.db.query(Country).filter(Country.country_id == country_id).first()
            if not country:
                raise HTTPException(status_code=404, detail="Country not found")
            
            # Check if new name conflicts with existing country
            if country_data.country_name:
                existing_country = self.db.query(Country).filter(
                    Country.country_name == country_data.country_name,
                    Country.country_id != country_id
                ).first()
                if existing_country:
                    raise HTTPException(status_code=400, detail="Country name already exists")
            
            # Update fields
            update_data = country_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(country, field, value)
            
            self.db.commit()
            self.db.refresh(country)
            
            return self._create_country_response(country)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while updating the country: {str(e)}"
            )
    
    def delete_country(self, country_id: int) -> dict:
        """
        Delete a country record.
        
        Args:
            country_id (int): Country ID
            
        Returns:
            dict: Success message
            
        Raises:
            HTTPException: If country not found or deletion fails
        """
        try:
            country = self.db.query(Country).filter(Country.country_id == country_id).first()
            if not country:
                raise HTTPException(status_code=404, detail="Country not found")
            
            # Check if country is referenced by other entities
            # This would need to be implemented based on your database constraints
            
            self.db.delete(country)
            self.db.commit()
            
            return {"message": "Country deleted successfully"}
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while deleting the country: {str(e)}"
            )
    
    def search_countries(self, search_term: str, skip: int = 0, limit: int = 100) -> List[CountryResponse]:
        """
        Search countries by name, ISO code, or region.
        
        Args:
            search_term (str): Search term
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return
            
        Returns:
            List[CountryResponse]: List of matching country responses
            
        Raises:
            HTTPException: If search fails
        """
        try:
            from sqlalchemy import or_
            
            countries = self.db.query(Country).filter(
                or_(
                    Country.country_name.ilike(f"%{search_term}%"),
                    Country.iso_code.ilike(f"%{search_term}%"),
                    Country.region.ilike(f"%{search_term}%")
                )
            ).offset(skip).limit(limit).all()
            
            return [self._create_country_response(country) for country in countries]
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while searching countries: {str(e)}"
            )
    
    def get_countries_by_region(self, region: str, skip: int = 0, limit: int = 100) -> List[CountryResponse]:
        """
        Get countries by region.
        
        Args:
            region (str): Region name
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return
            
        Returns:
            List[CountryResponse]: List of country responses in the region
            
        Raises:
            HTTPException: If retrieval fails
        """
        try:
            countries = self.db.query(Country).filter(
                Country.region == region
            ).offset(skip).limit(limit).all()
            
            return [self._create_country_response(country) for country in countries]
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while retrieving countries by region: {str(e)}"
            )
    
    def _create_country_response(self, country: Country) -> CountryResponse:
        """
        Create a country response from a Country model.
        
        Args:
            country (Country): Country model instance
            
        Returns:
            CountryResponse: Country response object
        """
        try:
            return CountryResponse(
                country_id=country.country_id,
                country_name=country.country_name,
                iso_code=country.iso_code,
                region=country.region
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error creating country response: {str(e)}"
            )
