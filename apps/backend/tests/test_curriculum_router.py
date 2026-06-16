"""
Unit tests for ``apps/backend/routers/curriculum.py`` handler-level 404 guards.

AWD-M-252: update_learning_objective, delete_learning_objective, update_content,
and delete_content were returning the service result directly (None or False when
not found), causing FastAPI to 500 (on None) or return JSON false on 200 (on
False) instead of raising a 404.  These tests verify the guards are in place.

Covers:
- update_learning_objective: service returns None → 404 "Learning objective not found"
- update_learning_objective: service returns ORM obj → that obj is returned
- delete_learning_objective: service returns False → 404 "Learning objective not found"
- delete_learning_objective: service returns True  → {"message": "...deleted..."}
- update_content:            service returns None  → 404 "Content not found"
- update_content:            service returns ORM obj → that obj is returned
- delete_content:            service returns False → 404 "Content not found"
- delete_content:            service returns True  → {"message": "...deleted..."}
"""

import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
root_dir = os.path.abspath(os.path.join(backend_dir, "../.."))
sys.path.insert(0, root_dir)

import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException

from apps.backend.routers.curriculum import (
    update_learning_objective,
    delete_learning_objective,
    update_content,
    delete_content,
)
from apps.backend.schemas.curriculum import LearningObjectiveUpdate, ContentUpdate


class TestUpdateLearningObjectiveM252:
    """AWD-M-252: update_learning_objective raises 404 when service returns None."""

    def test_not_found_raises_404(self):
        """Service returning None must raise HTTPException 404."""
        mock_db = MagicMock()
        mock_user = MagicMock()
        data = LearningObjectiveUpdate(objective="Updated objective text")

        with patch(
            "apps.backend.routers.curriculum.LearningObjectiveService"
        ) as MockService:
            MockService.return_value.update_learning_objective.return_value = None
            with pytest.raises(HTTPException) as exc_info:
                update_learning_objective(
                    objective_id=999,
                    objective_data=data,
                    current_user=mock_user,
                    db=mock_db,
                )
            assert exc_info.value.status_code == 404
            assert "learning objective" in exc_info.value.detail.lower()

    def test_found_returns_result(self):
        """Service returning an ORM object must be returned directly."""
        mock_db = MagicMock()
        mock_user = MagicMock()
        data = LearningObjectiveUpdate(objective="Updated objective text")
        fake_obj = MagicMock()

        with patch(
            "apps.backend.routers.curriculum.LearningObjectiveService"
        ) as MockService:
            MockService.return_value.update_learning_objective.return_value = fake_obj
            result = update_learning_objective(
                objective_id=1,
                objective_data=data,
                current_user=mock_user,
                db=mock_db,
            )
            assert result is fake_obj


class TestDeleteLearningObjectiveM252:
    """AWD-M-252: delete_learning_objective raises 404 when service returns False."""

    def test_not_found_raises_404(self):
        """Service returning False must raise HTTPException 404."""
        mock_db = MagicMock()
        mock_user = MagicMock()

        with patch(
            "apps.backend.routers.curriculum.LearningObjectiveService"
        ) as MockService:
            MockService.return_value.delete_learning_objective.return_value = False
            with pytest.raises(HTTPException) as exc_info:
                delete_learning_objective(
                    objective_id=999,
                    current_user=mock_user,
                    db=mock_db,
                )
            assert exc_info.value.status_code == 404
            assert "learning objective" in exc_info.value.detail.lower()

    def test_success_returns_message(self):
        """Service returning True must yield a success message dict."""
        mock_db = MagicMock()
        mock_user = MagicMock()

        with patch(
            "apps.backend.routers.curriculum.LearningObjectiveService"
        ) as MockService:
            MockService.return_value.delete_learning_objective.return_value = True
            result = delete_learning_objective(
                objective_id=1,
                current_user=mock_user,
                db=mock_db,
            )
            assert isinstance(result, dict)
            assert "message" in result
            assert "deleted" in result["message"].lower()


class TestUpdateContentM252:
    """AWD-M-252: update_content raises 404 when service returns None."""

    def test_not_found_raises_404(self):
        """Service returning None must raise HTTPException 404."""
        mock_db = MagicMock()
        mock_user = MagicMock()
        data = ContentUpdate(content_area="Updated content area")

        with patch(
            "apps.backend.routers.curriculum.TopicContentService"
        ) as MockService:
            MockService.return_value.update_content.return_value = None
            with pytest.raises(HTTPException) as exc_info:
                update_content(
                    content_id=999,
                    content_data=data,
                    current_user=mock_user,
                    db=mock_db,
                )
            assert exc_info.value.status_code == 404
            assert "content" in exc_info.value.detail.lower()

    def test_found_returns_result(self):
        """Service returning an ORM object must be returned directly."""
        mock_db = MagicMock()
        mock_user = MagicMock()
        data = ContentUpdate(content_area="Updated content area")
        fake_obj = MagicMock()

        with patch(
            "apps.backend.routers.curriculum.TopicContentService"
        ) as MockService:
            MockService.return_value.update_content.return_value = fake_obj
            result = update_content(
                content_id=1,
                content_data=data,
                current_user=mock_user,
                db=mock_db,
            )
            assert result is fake_obj


class TestDeleteContentM252:
    """AWD-M-252: delete_content raises 404 when service returns False."""

    def test_not_found_raises_404(self):
        """Service returning False must raise HTTPException 404."""
        mock_db = MagicMock()
        mock_user = MagicMock()

        with patch(
            "apps.backend.routers.curriculum.TopicContentService"
        ) as MockService:
            MockService.return_value.delete_content.return_value = False
            with pytest.raises(HTTPException) as exc_info:
                delete_content(
                    content_id=999,
                    current_user=mock_user,
                    db=mock_db,
                )
            assert exc_info.value.status_code == 404
            assert "content" in exc_info.value.detail.lower()

    def test_success_returns_message(self):
        """Service returning True must yield a success message dict."""
        mock_db = MagicMock()
        mock_user = MagicMock()

        with patch(
            "apps.backend.routers.curriculum.TopicContentService"
        ) as MockService:
            MockService.return_value.delete_content.return_value = True
            result = delete_content(
                content_id=1,
                current_user=mock_user,
                db=mock_db,
            )
            assert isinstance(result, dict)
            assert "message" in result
            assert "deleted" in result["message"].lower()
