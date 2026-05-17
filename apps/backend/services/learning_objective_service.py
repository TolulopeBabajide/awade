"""
Learning Objective Service for Awade

Extracted from CurriculumService as part of AWD-M-178 (service over 400-line threshold).
Handles all CRUD operations for LearningObjective records.

Author: Tolulope Babajide
"""

import logging
from contextlib import contextmanager

from sqlalchemy.orm import Session
from typing import Generator, List, Optional
from fastapi import HTTPException

from apps.backend.models import LearningObjective
from apps.backend.schemas.curriculum import (
    LearningObjectiveCreate, LearningObjectiveUpdate,
)

logger = logging.getLogger(__name__)


class LearningObjectiveService:
    """Service class for learning objective CRUD operations.

    AWD-M-178: Extracted from CurriculumService to keep each module under the
    400-line threshold. Takes the same (db,) constructor so callers can swap
    the class name without changing instantiation patterns.
    """

    def __init__(self, db: Session):
        """
        Initialize the LearningObjectiveService with a database session.

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
    # Learning Objective CRUD operations
    # ------------------------------------------------------------------

    def create_learning_objective(self, objective_data: LearningObjectiveCreate) -> LearningObjective:
        """Create a new learning objective.

        Args:
            objective_data (LearningObjectiveCreate): The objective data to create.

        Returns:
            LearningObjective: The created learning objective ORM object.
        """
        with self._db_guard("Failed to create learning objective"):
            objective = LearningObjective(**objective_data.model_dump())
            self.db.add(objective)
            self.db.commit()
            self.db.refresh(objective)
            return objective

    def get_learning_objectives(self, topic_id: int) -> List[LearningObjective]:
        """Get all learning objectives for a topic.

        Args:
            topic_id (int): The topic ID to filter by.

        Returns:
            List[LearningObjective]: List of learning objective ORM objects.
        """
        return self.db.query(LearningObjective).filter(LearningObjective.topic_id == topic_id).all()

    def update_learning_objective(self, objective_id: int, objective_data: LearningObjectiveUpdate) -> Optional[LearningObjective]:
        """Update a learning objective.

        Args:
            objective_id (int): The learning objective ID.
            objective_data (LearningObjectiveUpdate): The updated data.

        Returns:
            Optional[LearningObjective]: The updated ORM object or None if not found.
        """
        with self._db_guard("Failed to update learning objective"):
            objective = self.db.query(LearningObjective).filter(LearningObjective.learning_objective_id == objective_id).first()
            if not objective:
                return None

            objective.objective = objective_data.objective
            self.db.commit()
            self.db.refresh(objective)
            return objective

    def delete_learning_objective(self, objective_id: int) -> bool:
        """Delete a learning objective.

        Args:
            objective_id (int): The learning objective ID.

        Returns:
            bool: True if deleted, False if not found.
        """
        with self._db_guard("Failed to delete learning objective"):
            objective = self.db.query(LearningObjective).filter(LearningObjective.learning_objective_id == objective_id).first()
            if not objective:
                return False

            self.db.delete(objective)
            self.db.commit()
            return True
