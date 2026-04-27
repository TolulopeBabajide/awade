"""
Children Router for Awade API

This module provides endpoints for managing child profiles and parent guides.
Parents can add children, view their curriculum topics, and access saved guides.

Endpoints:
- GET    /api/consent/status         — Check COPPA consent status (AWD-GRC-01)
- POST   /api/consent                — Record COPPA parental consent (AWD-GRC-01)
- POST   /api/children              — Create a child profile (requires consent)
- GET    /api/children              — List all children for the current parent
- GET    /api/children/{child_id}   — Get a single child profile
- PUT    /api/children/{child_id}   — Update a child profile
- DELETE /api/children/{child_id}   — Delete a child profile
- GET    /api/children/{child_id}/topics  — Get curriculum topics for a child
- GET    /api/children/{child_id}/guides  — List guides for a child
- GET    /api/guides/{guide_id}           — Get a single guide
- POST   /api/guides/{guide_id}/bookmark  — Toggle guide bookmark
- GET    /api/guides/{guide_id}/export    — Export guide as PDF

Author: Tolulope Babajide
"""

import json
import logging
import re

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from sqlalchemy.orm import Session
from typing import Optional

from apps.backend.database import get_db
from apps.backend.models import User
from apps.backend.dependencies import require_parent
from apps.backend.limiter import limiter

logger = logging.getLogger(__name__)
from apps.backend.schemas.children import (
    ChildProfileCreate,
    ChildProfileUpdate,
    ChildProfileResponse,
    ChildProfileListResponse,
    ParentGuideResponse,
    ParentGuideListResponse,
    ParentalConsentResponse,
    ConsentStatusResponse,
)
from apps.backend.services.children_service import ChildrenService

router = APIRouter(prefix="/api", tags=["children"])


# ── COPPA Consent (AWD-GRC-01) ────────────────────────────────────────

@router.get("/consent/status", response_model=ConsentStatusResponse)
def get_consent_status(
    current_user: User = Depends(require_parent),
    db: Session = Depends(get_db),
):
    """Return whether the authenticated parent has given COPPA consent."""
    service = ChildrenService(db)
    return service.get_consent_status(current_user)


@router.post("/consent", response_model=ParentalConsentResponse, status_code=201)
@limiter.limit("10/minute")
def record_consent(
    request: Request,
    current_user: User = Depends(require_parent),
    db: Session = Depends(get_db),
):
    """
    Record COPPA parental consent for the authenticated parent.

    Idempotent — re-posting updates the consent timestamp.
    The client must display the full disclosure text before calling this endpoint.
    Rate-limited to 10 requests/minute to prevent abuse.
    """
    ip_address = request.client.host if request.client else None
    service = ChildrenService(db)
    return service.record_consent(current_user, ip_address=ip_address)


# ── Child Profile CRUD ────────────────────────────────────────────────

@router.post("/children", response_model=ChildProfileResponse, status_code=201)
def create_child(
    data: ChildProfileCreate,
    current_user: User = Depends(require_parent),
    db: Session = Depends(get_db),
):
    """Create a new child profile for the current parent."""
    service = ChildrenService(db)
    return service.create_child(current_user, data)


@router.get("/children", response_model=ChildProfileListResponse)
def list_children(
    current_user: User = Depends(require_parent),
    db: Session = Depends(get_db),
):
    """List all child profiles for the current parent."""
    service = ChildrenService(db)
    return service.list_children(current_user)


@router.get("/children/{child_id}", response_model=ChildProfileResponse)
def get_child(
    child_id: int,
    current_user: User = Depends(require_parent),
    db: Session = Depends(get_db),
):
    """Get a single child profile by ID."""
    service = ChildrenService(db)
    return service.get_child(current_user, child_id)


@router.put("/children/{child_id}", response_model=ChildProfileResponse)
def update_child(
    child_id: int,
    data: ChildProfileUpdate,
    current_user: User = Depends(require_parent),
    db: Session = Depends(get_db),
):
    """Update a child profile."""
    service = ChildrenService(db)
    return service.update_child(current_user, child_id, data)


@router.delete("/children/{child_id}")
def delete_child(
    child_id: int,
    current_user: User = Depends(require_parent),
    db: Session = Depends(get_db),
):
    """Delete a child profile and all associated guides."""
    service = ChildrenService(db)
    return service.delete_child(current_user, child_id)


# ── Child's Curriculum Topics ─────────────────────────────────────────

@router.get("/children/{child_id}/topics")
def get_child_topics(
    child_id: int,
    subject_id: Optional[int] = Query(None, description="Filter topics by subject ID"),
    current_user: User = Depends(require_parent),
    db: Session = Depends(get_db),
):
    """
    Get curriculum topics available for a child based on their
    curriculum and grade level. Optionally filter by subject.
    """
    service = ChildrenService(db)
    return service.get_child_topics(current_user, child_id, subject_id)


# ── Parent Guides ─────────────────────────────────────────────────────

@router.get("/children/{child_id}/guides", response_model=ParentGuideListResponse)
def list_child_guides(
    child_id: int,
    bookmarked: bool = Query(False, description="Only return bookmarked guides"),
    current_user: User = Depends(require_parent),
    db: Session = Depends(get_db),
):
    """List all parent guides for a child."""
    service = ChildrenService(db)
    return service.list_guides(current_user, child_id, bookmarked_only=bookmarked)


@router.post("/children/{child_id}/guides/generate", response_model=ParentGuideResponse, status_code=201)
@limiter.limit("5/minute")
def generate_guide(
    request: Request,
    child_id: int,
    topic_id: int = Query(..., description="Topic ID to generate a guide for"),
    current_user: User = Depends(require_parent),
    db: Session = Depends(get_db),
):
    """
    Generate (or retrieve existing) a 'How to Help' guide for a child and topic.
    If a guide already exists for this child+topic, returns the existing one.
    Rate-limited to 5 requests/minute per IP to prevent OpenAI cost abuse.
    """
    service = ChildrenService(db)
    return service.generate_guide(current_user, child_id, topic_id)


@router.get("/guides/{guide_id}", response_model=ParentGuideResponse)
def get_guide(
    guide_id: int,
    current_user: User = Depends(require_parent),
    db: Session = Depends(get_db),
):
    """Get a single parent guide by ID."""
    service = ChildrenService(db)
    return service.get_guide(current_user, guide_id)


@router.post("/guides/{guide_id}/bookmark", response_model=ParentGuideResponse)
def toggle_bookmark(
    guide_id: int,
    current_user: User = Depends(require_parent),
    db: Session = Depends(get_db),
):
    """Toggle the bookmark status of a guide."""
    service = ChildrenService(db)
    return service.toggle_bookmark(current_user, guide_id)


@router.get("/guides/{guide_id}/export")
def export_guide_pdf(
    guide_id: int,
    current_user: User = Depends(require_parent),
    db: Session = Depends(get_db),
):
    """
    Export a parent guide as a downloadable PDF for offline printing.

    Returns a PDF binary with Content-Disposition: attachment.
    Requires the guide to belong to the current parent (404 otherwise).
    """
    from apps.backend.services.pdf_service import PDFService

    service = ChildrenService(db)
    # Raises 404 if guide not found or not owned by this parent
    guide = service.get_guide(current_user, guide_id)

    if not guide.ai_generated_content:
        raise HTTPException(
            status_code=422,
            detail="This guide has no content to export.",
        )

    try:
        content = json.loads(guide.ai_generated_content)
    except (json.JSONDecodeError, ValueError):
        raise HTTPException(
            status_code=422,
            detail="Guide content is malformed and cannot be exported.",
        )

    meta = {
        "guide_id": guide.guide_id,
        "topic_title": guide.topic_title,
        "subject_name": guide.subject_name,
    }

    pdf_svc = PDFService()
    try:
        pdf_bytes = pdf_svc.generate_guide_pdf(content, meta)
    except RuntimeError:
        raise HTTPException(
            status_code=503,
            detail="PDF generation is not available. Please try again later.",
        )
    except Exception:
        logger.error("Unexpected error exporting guide %s", guide_id, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while exporting the guide.",
        )

    # Build a safe filename from the topic title
    raw_title = guide.topic_title or f"guide_{guide_id}"
    safe_title = re.sub(r"[^\w\s-]", "", raw_title).strip()
    safe_title = re.sub(r"\s+", "_", safe_title)[:60]
    filename = f"{safe_title}.pdf" if safe_title else f"guide_{guide_id}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
