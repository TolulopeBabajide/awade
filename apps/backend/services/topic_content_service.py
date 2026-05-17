"""
Topic Content Service for Awade

Extracted from CurriculumService as part of AWD-M-178 (service over 400-line threshold).
Handles all CRUD operations for TopicContent records.

Author: Tolulope Babajide
"""

import logging
from contextlib import contextmanager

from sqlalchemy.orm import Session
from typing import Generator, List, Optional
from fastapi import HTTPException

from apps.backend.models import TopicContent
from apps.backend.schemas.curriculum import (
    ContentCreate, ContentUpdate,
)

logger = logging.getLogger(__name__)


class TopicContentService:
    """Service class for topic content CRUD operations.

    AWD-M-178: Extracted from CurriculumService to keep each module under the
    400-line threshold. Takes the same (db,) constructor so callers can swap
    the class name without changing instantiation patterns.
    """

    def __init__(self, db: Session):
        """
        Initialize the TopicContentService with a database session.

        Args:
            db (Session): SQLAlchemy database session.
        """
        self.db = db

    @contextmanager
    def _db_guard(self, error_msg: str) -> Generator[None, None, None]:
        """Context manager that absorbs and converts DB errors to HTTP 500.

        Re-raises HTTPException unchanged so callers' explicit 404/403
        responses are not swallowed.  Any other exception is logged (with full
        traceback) and re-raised as ``HTTPException(status_code=500,
        detail=error_msg)``.

        Args:
            error_msg (str): Detail string for the HTTP 500 response.
        """
        try:
            yield
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error("%s: %s", error_msg, e, exc_info=True)
            raise HTTPException(status_code=500, detail=error_msg)

    # ------------------------------------------------------------------
    # Topic Content CRUD operations
    # ------------------------------------------------------------------

    def create_content(self, content_data: ContentCreate) -> TopicContent:
        """Create a new content area.

        Args:
            content_data (ContentCreate): The content data to create.

        Returns:
            TopicContent: The created content ORM object.
        """
        with self._db_guard("Failed to create content"):
            content = TopicContent(**content_data.model_dump())
            self.db.add(content)
            self.db.commit()
            self.db.refresh(content)
            return content

    def get_contents(self, topic_id: int) -> List[TopicContent]:
        """Get all content areas for a topic.

        Args:
            topic_id (int): The topic ID to filter by.

        Returns:
            List[TopicContent]: List of topic content ORM objects.
        """
        return self.db.query(TopicContent).filter(TopicContent.topic_id == topic_id).all()

    def update_content(self, content_id: int, content_data: ContentUpdate) -> Optional[TopicContent]:
        """Update a content area.

        Args:
            content_id (int): The content ID.
            content_data (ContentUpdate): The updated data.

        Returns:
            Optional[TopicContent]: The updated ORM object or None if not found.
        """
        with self._db_guard("Failed to update content"):
            content = self.db.query(TopicContent).filter(TopicContent.topic_contents_id == content_id).first()
            if not content:
                return None

            content.content_area = content_data.content_area
            self.db.commit()
            self.db.refresh(content)
            return content

    def delete_content(self, content_id: int) -> bool:
        """Delete a content area.

        Args:
            content_id (int): The content ID.

        Returns:
            bool: True if deleted, False if not found.
        """
        with self._db_guard("Failed to delete content"):
            content = self.db.query(TopicContent).filter(TopicContent.topic_contents_id == content_id).first()
            if not content:
                return False

            self.db.delete(content)
            self.db.commit()
            return True
