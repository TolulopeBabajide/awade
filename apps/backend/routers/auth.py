from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..database import get_db
from ..schemas.users import AuthResponse, UserResponse, UserCreate
from ..models import User, UserRole
import requests
import os
import jwt
from datetime import datetime, timedelta
import bcrypt

router = APIRouter(prefix="/api/auth", tags=["auth"])

class GoogleAuthRequest(BaseModel):
    credential: str

@router.post("/google", response_model=AuthResponse)
def google_auth(
    payload: GoogleAuthRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user with Google OAuth credential (ID token).
    """
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "YOUR_GOOGLE_CLIENT_ID")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret")
    JWT_EXPIRES_MINUTES = int(os.getenv("JWT_EXPIRES_MINUTES", "60"))
    id_token = payload.credential

    # Verify the token with Google
    google_verify_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
    resp = requests.get(google_verify_url)
    if resp.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid Google token")
    google_data = resp.json()

    # Check audience
    if google_data.get("aud") != GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=401, detail="Invalid Google client ID")

    # Extract user info
    email = google_data.get("email")
    full_name = google_data.get("name")
    if not email:
        raise HTTPException(status_code=400, detail="Google account missing email")

    # Lookup or create user in DB
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            email=email,
            password_hash="google-oauth",  # Not used for Google users
            full_name=full_name or email,
            role=UserRole.EDUCATOR,
            country="",
            created_at=datetime.utcnow()
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        user.last_login = datetime.utcnow()
        db.commit()
        db.refresh(user)

    # Generate JWT token
    payload = {
        "sub": str(user.user_id),
        "email": user.email,
        "exp": datetime.utcnow() + timedelta(minutes=JWT_EXPIRES_MINUTES)
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")

    user_response = UserResponse(
        user_id=user.user_id,
        email=user.email,
        full_name=user.full_name,
        role=user.role.value if hasattr(user.role, 'value') else user.role,
        country=user.country,
        region=user.region,
        school_name=user.school_name,
        subjects=user.subjects,
        grade_levels=user.grade_levels,
        languages_spoken=user.languages_spoken,
        created_at=user.created_at,
        last_login=user.last_login
    )
    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user=user_response
    )

@router.post("/signup", response_model=AuthResponse)
def signup(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user with email and password.
    """
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret")
    JWT_EXPIRES_MINUTES = int(os.getenv("JWT_EXPIRES_MINUTES", "60"))

    # Check if user already exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(user_data.password.encode('utf-8'), salt).decode('utf-8')

    # Create user
    user = User(
        email=user_data.email,
        password_hash=password_hash,
        full_name=user_data.full_name,
        role=user_data.role,
        country=user_data.country,
        region=user_data.region,
        school_name=user_data.school_name,
        subjects=user_data.subjects,
        grade_levels=user_data.grade_levels,
        languages_spoken=user_data.languages_spoken,
        created_at=datetime.utcnow()
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Generate JWT token
    payload = {
        "sub": str(user.user_id),
        "email": user.email,
        "exp": datetime.utcnow() + timedelta(minutes=JWT_EXPIRES_MINUTES)
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")

    user_response = UserResponse(
        user_id=user.user_id,
        email=user.email,
        full_name=user.full_name,
        role=user.role.value 
        country=user.country,
        region=user.region,
        school_name=user.school_name,
        subjects=user.subjects,
        grade_levels=user.grade_levels,
        languages_spoken=user.languages_spoken,
        created_at=user.created_at,
        last_login=user.last_login
    )
    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user=user_response
    ) 