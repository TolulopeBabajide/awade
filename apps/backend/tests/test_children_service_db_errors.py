"""
AWD-M-182: ChildrenService tests — DB error handling (AWD-M-180, AWD-M-181).

Covers:
  - TestChildrenServiceDBErrors: each mutation method catches unexpected DB
    exceptions, rolls back, logs, and raises HTTP 500; HTTPException re-raised
    unchanged.
"""

import json
import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException

from children_service_factories import (
    _parent, _child, _guide, VALID_AI_CONTENT,
)

from apps.backend.models import ParentGuide, Topic
from apps.backend.services.children_service import ChildrenService
from apps.backend.schemas.children import ChildProfileCreate, ChildProfileUpdate


class TestChildrenServiceDBErrors:
    """
    Each mutation method must catch unexpected DB exceptions, roll back,
    log the error, and raise HTTP 500. HTTPException should be re-raised
    unchanged (not wrapped in another 500).
    """

    # -- helpers -------------------------------------------------------------

    def _simple_db(self, child_obj=None, guide_obj=None):
        """DB mock that returns the given child/guide from query chains."""
        mock_db = MagicMock()
        q = MagicMock()
        if child_obj is not None:
            q.options.return_value.filter.return_value.first.return_value = child_obj
        if guide_obj is not None:
            q.options.return_value.join.return_value.filter.return_value.first.return_value = guide_obj
            q.join.return_value.filter.return_value.first.return_value = guide_obj
        mock_db.query.return_value = q
        return mock_db

    # -- create_child --------------------------------------------------------

    def test_create_child_db_error_raises_500(self):
        parent = _parent(user_id=1)
        child_obj = _child(child_id=5, parent_id=1)

        mock_db = MagicMock()
        mock_db.commit.side_effect = Exception("DB gone away")
        mock_db.rollback = MagicMock()

        svc = ChildrenService(db=mock_db)
        svc._verify_parent = MagicMock()
        svc._require_consent = MagicMock()

        data = ChildProfileCreate(name="Alice", age=8)
        # bypass FK queries — no subjects/country/curricula provided
        with pytest.raises(HTTPException) as exc_info:
            svc.create_child(parent, data)

        assert exc_info.value.status_code == 500
        mock_db.rollback.assert_called_once()

    def test_create_child_http_exception_not_wrapped(self):
        """An HTTPException raised during commit must propagate unchanged."""
        parent = _parent(user_id=1)
        mock_db = MagicMock()
        mock_db.commit.side_effect = HTTPException(status_code=409, detail="conflict")
        mock_db.rollback = MagicMock()

        svc = ChildrenService(db=mock_db)
        svc._verify_parent = MagicMock()
        svc._require_consent = MagicMock()

        data = ChildProfileCreate(name="Alice", age=8)
        with pytest.raises(HTTPException) as exc_info:
            svc.create_child(parent, data)

        assert exc_info.value.status_code == 409
        mock_db.rollback.assert_not_called()

    # -- update_child --------------------------------------------------------

    def test_update_child_db_error_raises_500(self):
        parent = _parent(user_id=1)
        child_obj = _child(child_id=5, parent_id=1)

        mock_db = MagicMock()
        mock_db.commit.side_effect = Exception("lock timeout")
        mock_db.rollback = MagicMock()

        svc = ChildrenService(db=mock_db)
        svc._verify_parent = MagicMock()
        svc._get_child_or_404 = MagicMock(return_value=child_obj)

        data = ChildProfileUpdate(name="Updated Name")
        with pytest.raises(HTTPException) as exc_info:
            svc.update_child(parent, child_id=5, data=data)

        assert exc_info.value.status_code == 500
        mock_db.rollback.assert_called_once()

    # -- delete_child --------------------------------------------------------

    def test_delete_child_db_error_raises_500(self):
        parent = _parent(user_id=1)
        child_obj = _child(child_id=5, parent_id=1)

        mock_db = MagicMock()
        mock_db.commit.side_effect = Exception("connection closed")
        mock_db.rollback = MagicMock()

        svc = ChildrenService(db=mock_db)
        svc._verify_parent = MagicMock()
        svc._get_child_or_404 = MagicMock(return_value=child_obj)

        with pytest.raises(HTTPException) as exc_info:
            svc.delete_child(parent, child_id=5)

        assert exc_info.value.status_code == 500
        mock_db.rollback.assert_called_once()

    # -- toggle_bookmark -----------------------------------------------------

    def test_toggle_bookmark_db_error_raises_500(self):
        parent = _parent(user_id=1)
        guide_obj = _guide(guide_id=10, child_id=5)

        mock_db = MagicMock()
        # query chain for toggle_bookmark: .join().filter().first()
        q = MagicMock()
        q.options.return_value.join.return_value.filter.return_value.first.return_value = guide_obj
        mock_db.query.return_value = q
        mock_db.commit.side_effect = Exception("serialization failure")
        mock_db.rollback = MagicMock()

        svc = ChildrenService(db=mock_db)
        svc._verify_parent = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            svc.toggle_bookmark(parent, guide_id=10)

        assert exc_info.value.status_code == 500
        mock_db.rollback.assert_called_once()

    # -- generate_guide persist ----------------------------------------------

    def test_generate_guide_persist_db_error_raises_500(self):
        """DB error after AI generation and validation must raise 500 with rollback."""
        parent = _parent(user_id=1)
        child_obj = _child(child_id=5, parent_id=1)
        child_obj.country = MagicMock()
        child_obj.country.country_name = "Nigeria"

        mock_topic = MagicMock()
        mock_topic.topic_id = 1
        mock_topic.topic_title = "Fractions"
        cs = MagicMock()
        cs.subject.name = "Mathematics"
        cs.grade_level.name = "Grade 5"
        cs.curriculum.curricula_title = "Nigerian Curriculum"
        mock_topic.curriculum_structure = cs
        mock_topic.learning_objectives = []
        mock_topic.topic_contents = []

        call_count = [0]

        def query_side(model):
            call_count[0] += 1
            q = MagicMock()
            if model is ParentGuide and call_count[0] == 1:
                # existence check — no existing guide
                q.options.return_value.filter.return_value.first.return_value = None
            elif model is Topic:
                q.options.return_value.filter.return_value.first.return_value = mock_topic
            return q

        mock_db = MagicMock()
        mock_db.query.side_effect = query_side
        mock_db.commit.side_effect = Exception("disk full")
        mock_db.rollback = MagicMock()

        svc = ChildrenService(db=mock_db)
        svc._get_child_or_404 = MagicMock(return_value=child_obj)
        svc._verify_parent = MagicMock()

        with patch("apps.backend.services.children_service.AwadeGPTService") as MockAI:
            instance = MockAI.return_value
            instance.generate_parent_guide.return_value = (
                json.dumps(VALID_AI_CONTENT), True
            )
            with pytest.raises(HTTPException) as exc_info:
                svc.generate_guide(parent, child_id=5, topic_id=1)

        assert exc_info.value.status_code == 500
        mock_db.rollback.assert_called_once()

    # -- record_consent ----------------------------------------------------------

    def test_record_consent_db_error_raises_500(self):
        """Generic DB error during consent commit must roll back and raise HTTP 500."""
        parent = _parent(user_id=1)

        mock_db = MagicMock()
        # query returns no existing consent record → will insert
        q = MagicMock()
        q.filter.return_value.first.return_value = None
        mock_db.query.return_value = q
        mock_db.commit.side_effect = Exception("DB unavailable")
        mock_db.rollback = MagicMock()

        svc = ChildrenService(db=mock_db)
        svc._verify_parent = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            svc.record_consent(parent, ip_address="127.0.0.1")

        assert exc_info.value.status_code == 500
        mock_db.rollback.assert_called_once()

    def test_record_consent_http_exception_not_wrapped(self):
        """An HTTPException raised during consent commit must propagate unchanged."""
        parent = _parent(user_id=1)

        mock_db = MagicMock()
        q = MagicMock()
        q.filter.return_value.first.return_value = None
        mock_db.query.return_value = q
        mock_db.commit.side_effect = HTTPException(status_code=409, detail="conflict")
        mock_db.rollback = MagicMock()

        svc = ChildrenService(db=mock_db)
        svc._verify_parent = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            svc.record_consent(parent, ip_address="127.0.0.1")

        assert exc_info.value.status_code == 409
        mock_db.rollback.assert_not_called()
