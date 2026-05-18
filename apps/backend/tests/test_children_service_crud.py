"""
AWD-M-182: ChildrenService tests — CRUD operations.

Covers:
  - TestCreateChildFKValidation: create_child raises 400 when FK IDs don't exist
  - TestListChildrenIsolation: list_children filters by calling parent's user_id
  - TestDeleteChild: delete_child removes the record and returns a success message
  - TestGetChildTopics: get_child_topics returns topics with subject info resolved
  - TestUpdateChildSubjectValidation: update_child uses batch query for subject FK validation
"""

import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException

from children_service_factories import (
    _parent, _educator, _child,
)

from apps.backend.models import (
    Country, Curriculum, GradeLevel, Subject, Topic, CurriculumStructure,
    ChildProfile,
)
from apps.backend.services.children_service import ChildrenService
from apps.backend.schemas.children import ChildProfileCreate, ChildProfileUpdate


# ---------------------------------------------------------------------------
# create_child FK validation
# ---------------------------------------------------------------------------

class TestCreateChildFKValidation:
    """create_child raises 400 when FK IDs don't exist in the DB."""

    def _db_fk_fails(self, model_to_fail):
        """DB where query for model_to_fail (a class) returns None (FK invalid)."""
        mock_db = MagicMock()

        def query_side(model):
            q = MagicMock()
            if model is model_to_fail:
                q.filter.return_value.first.return_value = None
            else:
                q.filter.return_value.first.return_value = MagicMock()
            return q

        mock_db.query.side_effect = query_side
        return mock_db

    def _db_subjects_not_found(self, valid_ids=None):
        """DB mock for subject batch validation.

        Single-FK queries (Country/Curriculum/GradeLevel) use a class argument
        and .filter().first(); the subject batch query uses Subject.subject_id
        (an InstrumentedAttribute) and .filter().all().
        """
        valid_ids = valid_ids or []
        mock_db = MagicMock()

        single_q = MagicMock()
        single_q.filter.return_value.first.return_value = MagicMock()

        batch_q = MagicMock()
        batch_q.filter.return_value.all.return_value = [(sid,) for sid in valid_ids]

        def query_side(model_arg):
            import inspect
            return single_q if inspect.isclass(model_arg) else batch_q

        mock_db.query.side_effect = query_side
        return mock_db

    def test_invalid_country_id_raises_400(self):
        mock_db = self._db_fk_fails(Country)
        svc = ChildrenService(db=mock_db)
        with pytest.raises(HTTPException) as exc_info:
            svc.create_child(
                _parent(),
                ChildProfileCreate(name="Alice", country_id=999),
            )
        assert exc_info.value.status_code == 400
        assert "country_id" in exc_info.value.detail

    def test_invalid_curricula_id_raises_400(self):
        mock_db = self._db_fk_fails(Curriculum)
        svc = ChildrenService(db=mock_db)
        with pytest.raises(HTTPException) as exc_info:
            svc.create_child(
                _parent(),
                ChildProfileCreate(name="Alice", curricula_id=999),
            )
        assert exc_info.value.status_code == 400
        assert "curricula_id" in exc_info.value.detail

    def test_invalid_grade_level_id_raises_400(self):
        mock_db = self._db_fk_fails(GradeLevel)
        svc = ChildrenService(db=mock_db)
        with pytest.raises(HTTPException) as exc_info:
            svc.create_child(
                _parent(),
                ChildProfileCreate(name="Alice", grade_level_id=999),
            )
        assert exc_info.value.status_code == 400
        assert "grade_level_id" in exc_info.value.detail

    def test_invalid_subject_id_raises_400(self):
        """All subjects absent from DB → 400 with the invalid id in detail."""
        mock_db = self._db_subjects_not_found(valid_ids=[])
        svc = ChildrenService(db=mock_db)
        with pytest.raises(HTTPException) as exc_info:
            svc.create_child(
                _parent(),
                ChildProfileCreate(name="Alice", subjects=[42]),
            )
        assert exc_info.value.status_code == 400
        assert "subject_id" in exc_info.value.detail
        assert "42" in exc_info.value.detail

    def test_partial_invalid_subjects_raises_400_for_first_bad_id(self):
        """DB has subject 10 but not 99 — error reports 99."""
        mock_db = self._db_subjects_not_found(valid_ids=[10])
        svc = ChildrenService(db=mock_db)
        with pytest.raises(HTTPException) as exc_info:
            svc.create_child(
                _parent(),
                ChildProfileCreate(name="Alice", subjects=[10, 99]),
            )
        assert exc_info.value.status_code == 400
        assert "99" in exc_info.value.detail

    def test_all_valid_subjects_does_not_raise(self):
        """All subject IDs found in DB — no exception raised, commit called."""
        mock_db = self._db_subjects_not_found(valid_ids=[5, 6])
        # After FK checks, create_child calls db.add/commit/refresh then _get_child_or_404.
        # We need _get_child_or_404 to work, so patch it.
        svc = ChildrenService(db=mock_db)
        child_obj = _child(child_id=1, parent_id=1)
        svc._get_child_or_404 = MagicMock(return_value=child_obj)
        # Should not raise
        result = svc.create_child(
            _parent(user_id=1),
            ChildProfileCreate(name="Bob", subjects=[5, 6]),
        )
        assert result.name == "Child 1"

    def test_subject_validation_uses_single_batch_query(self):
        """Subjects list with N items must trigger exactly one DB query, not N."""
        mock_db = self._db_subjects_not_found(valid_ids=[1, 2, 3])
        svc = ChildrenService(db=mock_db)
        child_obj = _child(child_id=1, parent_id=1)
        svc._get_child_or_404 = MagicMock(return_value=child_obj)

        svc.create_child(
            _parent(user_id=1),
            ChildProfileCreate(name="Alice", subjects=[1, 2, 3]),
        )
        # batch_q is the non-class query mock; filter().all() should be called once
        import inspect
        batch_calls = [
            call_args for call_args in mock_db.query.call_args_list
            if not inspect.isclass(call_args.args[0])
        ]
        assert len(batch_calls) == 1, (
            f"Expected 1 batch subject query, got {len(batch_calls)}"
        )


# ---------------------------------------------------------------------------
# list_children isolation
# ---------------------------------------------------------------------------

class TestListChildrenIsolation:
    """list_children filters by the calling parent's user_id."""

    def test_returns_only_parent_own_children(self):
        parent = _parent(user_id=3)
        own_child = _child(child_id=10, parent_id=3)

        mock_db = MagicMock()
        q = MagicMock()
        # Simulate .options().filter().order_by().all() returning only own_child
        q.options.return_value.filter.return_value.order_by.return_value.all.return_value = [own_child]
        mock_db.query.return_value = q

        svc = ChildrenService(db=mock_db)
        result = svc.list_children(parent)

        assert result.total == 1
        assert result.children[0].parent_id == 3

    def test_returns_empty_list_when_no_children(self):
        parent = _parent(user_id=7)

        mock_db = MagicMock()
        q = MagicMock()
        q.options.return_value.filter.return_value.order_by.return_value.all.return_value = []
        mock_db.query.return_value = q

        svc = ChildrenService(db=mock_db)
        result = svc.list_children(parent)

        assert result.total == 0
        assert result.children == []


# ---------------------------------------------------------------------------
# delete_child
# ---------------------------------------------------------------------------

class TestDeleteChild:
    """delete_child removes the record and returns a success message."""

    def test_delete_own_child_returns_message(self):
        parent = _parent(user_id=1)
        child_obj = _child(child_id=5, parent_id=1)

        mock_db = MagicMock()
        q = MagicMock()
        q.options.return_value.filter.return_value.first.return_value = child_obj
        mock_db.query.return_value = q
        mock_db.delete = MagicMock()
        mock_db.commit = MagicMock()

        svc = ChildrenService(db=mock_db)
        result = svc.delete_child(parent, child_id=5)

        mock_db.delete.assert_called_once_with(child_obj)
        mock_db.commit.assert_called_once()
        assert result["message"] == "Child profile deleted successfully"


# ---------------------------------------------------------------------------
# get_child_topics — AWD-M-13 N+1 fix
# ---------------------------------------------------------------------------

class TestGetChildTopics:
    """
    get_child_topics must:
    - return [] when child has no curricula_id or grade_level_id
    - return topic dicts with subject_name and subject_id resolved
    - filter by subject_id when provided
    - raise 403 for EDUCATOR role
    """

    def _make_topic(self, topic_id: int, title: str, subject_name: str, subject_id: int) -> MagicMock:
        subj = MagicMock()
        subj.name = subject_name
        subj.subject_id = subject_id

        cs = MagicMock()
        cs.subject = subj
        cs.subject_id = subject_id

        t = MagicMock()
        t.topic_id = topic_id
        t.topic_title = title
        t.curriculum_structure = cs
        return t

    def _db_with_topics(self, child_obj: ChildProfile, topics: list) -> MagicMock:
        mock_db = MagicMock()

        def query_side(model):
            q = MagicMock()
            if model is ChildProfile:
                q.options.return_value.filter.return_value.first.return_value = child_obj
            elif model is Topic:
                # Simulate .join().options().filter().all() chain
                chain = MagicMock()
                chain.all.return_value = topics
                q.join.return_value.options.return_value.filter.return_value = chain
                q.join.return_value.options.return_value.filter.return_value.filter.return_value = chain
            return q

        mock_db.query.side_effect = query_side
        return mock_db

    def test_returns_empty_list_when_no_curricula_id(self):
        parent = _parent(user_id=1)
        child_obj = _child(child_id=1, parent_id=1)
        child_obj.curricula_id = None  # not set

        mock_db = MagicMock()
        q = MagicMock()
        q.options.return_value.filter.return_value.first.return_value = child_obj
        mock_db.query.return_value = q
        svc = ChildrenService(db=mock_db)
        svc._get_child_or_404 = MagicMock(return_value=child_obj)

        result = svc.get_child_topics(parent, child_id=1)
        assert result == []

    def test_returns_empty_list_when_no_grade_level_id(self):
        parent = _parent(user_id=1)
        child_obj = _child(child_id=1, parent_id=1)
        child_obj.grade_level_id = None  # not set

        svc = ChildrenService(db=MagicMock())
        svc._get_child_or_404 = MagicMock(return_value=child_obj)
        svc._verify_parent = MagicMock()

        result = svc.get_child_topics(parent, child_id=1)
        assert result == []

    def test_returns_topic_list_with_subject_info(self):
        parent = _parent(user_id=1)
        child_obj = _child(child_id=1, parent_id=1)

        topic1 = self._make_topic(101, "Fractions", "Mathematics", 5)
        topic2 = self._make_topic(102, "Photosynthesis", "Biology", 7)

        mock_db = self._db_with_topics(child_obj, [topic1, topic2])
        svc = ChildrenService(db=mock_db)
        svc._get_child_or_404 = MagicMock(return_value=child_obj)
        svc._verify_parent = MagicMock()

        result = svc.get_child_topics(parent, child_id=1)

        assert len(result) == 2
        assert result[0]["topic_id"] == 101
        assert result[0]["topic_title"] == "Fractions"
        assert result[0]["subject_name"] == "Mathematics"
        assert result[0]["subject_id"] == 5
        assert result[1]["topic_id"] == 102
        assert result[1]["subject_name"] == "Biology"

    def test_none_curriculum_structure_gives_none_subject(self):
        """Topics with null curriculum_structure must not crash — return None fields."""
        parent = _parent(user_id=1)
        child_obj = _child(child_id=1, parent_id=1)

        t = MagicMock()
        t.topic_id = 200
        t.topic_title = "Unknown Topic"
        t.curriculum_structure = None

        mock_db = self._db_with_topics(child_obj, [t])
        svc = ChildrenService(db=mock_db)
        svc._get_child_or_404 = MagicMock(return_value=child_obj)
        svc._verify_parent = MagicMock()

        result = svc.get_child_topics(parent, child_id=1)
        assert len(result) == 1
        assert result[0]["subject_name"] is None
        assert result[0]["subject_id"] is None

    def test_educator_raises_403(self):
        svc = ChildrenService(db=MagicMock())
        with pytest.raises(HTTPException) as exc_info:
            svc.get_child_topics(_educator(), child_id=1)
        assert exc_info.value.status_code == 403


# ---------------------------------------------------------------------------
# update_child subject FK batch validation — AWD-M-14
# ---------------------------------------------------------------------------

class TestUpdateChildSubjectValidation:
    """update_child uses a batch query for subject FK validation."""

    def _db_for_update(self, child_obj, valid_subject_ids=None):
        """DB mock supporting _get_child_or_404 and subject batch validation."""
        valid_subject_ids = valid_subject_ids or []
        mock_db = MagicMock()

        single_q = MagicMock()
        single_q.options.return_value.filter.return_value.first.return_value = child_obj

        batch_q = MagicMock()
        batch_q.filter.return_value.all.return_value = [
            (sid,) for sid in valid_subject_ids
        ]

        def query_side(model_arg):
            import inspect
            return single_q if inspect.isclass(model_arg) else batch_q

        mock_db.query.side_effect = query_side
        mock_db.commit = MagicMock()
        mock_db.refresh = MagicMock()
        return mock_db

    def test_update_invalid_subject_raises_400(self):
        parent = _parent(user_id=1)
        child_obj = _child(child_id=5, parent_id=1)
        mock_db = self._db_for_update(child_obj, valid_subject_ids=[])
        svc = ChildrenService(db=mock_db)

        with pytest.raises(HTTPException) as exc_info:
            svc.update_child(parent, child_id=5, data=ChildProfileUpdate(subjects=[77]))
        assert exc_info.value.status_code == 400
        assert "77" in exc_info.value.detail

    def test_update_valid_subjects_commits(self):
        parent = _parent(user_id=1)
        child_obj = _child(child_id=5, parent_id=1)
        mock_db = self._db_for_update(child_obj, valid_subject_ids=[3, 4])
        svc = ChildrenService(db=mock_db)
        # Patch final reload to avoid secondary DB interaction
        svc._get_child_or_404 = MagicMock(return_value=child_obj)

        svc.update_child(parent, child_id=5, data=ChildProfileUpdate(subjects=[3, 4]))
        mock_db.commit.assert_called_once()

    def test_update_subject_uses_single_batch_query(self):
        parent = _parent(user_id=1)
        child_obj = _child(child_id=5, parent_id=1)
        mock_db = self._db_for_update(child_obj, valid_subject_ids=[3, 4, 5])
        svc = ChildrenService(db=mock_db)
        svc._get_child_or_404 = MagicMock(return_value=child_obj)

        svc.update_child(parent, child_id=5, data=ChildProfileUpdate(subjects=[3, 4, 5]))

        import inspect
        batch_calls = [
            c for c in mock_db.query.call_args_list
            if not inspect.isclass(c.args[0])
        ]
        assert len(batch_calls) == 1, (
            f"Expected 1 batch subject query for update, got {len(batch_calls)}"
        )
