"""
Tests for AWD-H-11: ChildrenService unit tests.

Covers:
- Role gating: EDUCATOR/unauthenticated-equivalent → 403
- Ownership via _get_child_or_404: wrong parent_id → 404
- create_child: FK validation rejects bad IDs
- list_children: returns only calling parent's children
- delete_child: removes child owned by calling parent
- generate_guide idempotency: existing guide returned without AI call
- generate_guide AI validation: malformed JSON → 502
"""

import json
import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch, PropertyMock
from fastapi import HTTPException

import sys
import os

# Path fixups for sandbox
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "../../../"))
sys.path.insert(0, root_dir)

# Sandbox compat shim: datetime.UTC added in Python 3.11
import datetime as _dt
if not hasattr(_dt, "UTC"):
    _dt.UTC = _dt.timezone.utc

from apps.backend.models import (
    ChildProfile, ParentGuide, User, UserRole,
    Country, Curriculum, GradeLevel, Subject, Topic, CurriculumStructure,
)
from apps.backend.services.children_service import ChildrenService
from apps.backend.schemas.children import (
    ChildProfileCreate, ChildProfileUpdate, ParentGuideAIContent,
)

# ---------------------------------------------------------------------------
# Shared fixtures / factories
# ---------------------------------------------------------------------------

def _now():
    return datetime.now(timezone.utc)


def _make_user(user_id: int, role: UserRole) -> User:
    u = User()
    u.user_id = user_id
    u.email = f"user{user_id}@example.com"
    u.role = role
    u.is_suspended = False
    return u


def _parent(user_id: int = 1) -> User:
    return _make_user(user_id, UserRole.PARENT)


def _educator(user_id: int = 10) -> User:
    return _make_user(user_id, UserRole.EDUCATOR)


def _child(child_id: int, parent_id: int) -> ChildProfile:
    c = ChildProfile()
    c.child_id = child_id
    c.parent_id = parent_id
    c.name = f"Child {child_id}"
    c.age = 9
    c.school_name = None
    c.country_id = None
    c.curricula_id = 1
    c.grade_level_id = 1
    c.subjects = None
    c.created_at = _now()
    c.updated_at = _now()
    c.country = None
    c.curriculum = None
    c.grade_level = None
    return c


def _guide(guide_id: int, child_id: int, topic_id: int = 1) -> ParentGuide:
    g = ParentGuide()
    g.guide_id = guide_id
    g.child_id = child_id
    g.topic_id = topic_id
    g.ai_generated_content = None
    g.user_edited_content = None
    g.is_bookmarked = 0
    g.created_at = _now()
    g.updated_at = _now()
    t = MagicMock()
    t.topic_title = "Fractions"
    t.curriculum_structure = None
    g.topic = t
    return g


VALID_AI_CONTENT = {
    "topic_header": {
        "topic": "Fractions",
        "subject": "Mathematics",
        "grade_level": "Grade 5",
        "country": "Nigeria",
        "curriculum": "Nigerian Curriculum",
    },
    "simple_explanation": {
        "what_it_is": "A fraction represents a part of a whole.",
        "why_it_matters": "Fractions are used daily.",
    },
    "home_activity": {
        "title": "Pizza Fraction Fun",
        "description": "Use paper to model fractions.",
        "materials_needed": ["Paper", "Pencil"],
        "steps": ["Fold paper in half", "Label each half"],
        "what_to_look_for": "Child can name each fraction.",
    },
    "conversation_starters": ["What fraction did you eat?"],
    "common_mistakes": [
        {
            "mistake": "Larger denominator = larger fraction",
            "why_it_happens": "Focus on the bigger number.",
            "how_to_help": "Use visual aids.",
        }
    ],
}


# ---------------------------------------------------------------------------
# Role gating
# ---------------------------------------------------------------------------

class TestRoleGating:
    """_verify_parent must raise 403 for EDUCATOR role."""

    def _service(self):
        return ChildrenService(db=MagicMock())

    def test_educator_create_child_raises_403(self):
        svc = self._service()
        with pytest.raises(HTTPException) as exc_info:
            svc._verify_parent(_educator())
        assert exc_info.value.status_code == 403

    def test_parent_does_not_raise(self):
        svc = self._service()
        # Must not raise for PARENT
        svc._verify_parent(_parent())

    def test_admin_does_not_raise(self):
        svc = self._service()
        admin = _make_user(99, UserRole.ADMIN)
        svc._verify_parent(admin)

    def test_super_admin_does_not_raise(self):
        svc = self._service()
        super_admin = _make_user(100, UserRole.SUPER_ADMIN)
        svc._verify_parent(super_admin)

    def test_create_child_raises_403_for_educator(self):
        mock_db = MagicMock()
        svc = ChildrenService(db=mock_db)
        with pytest.raises(HTTPException) as exc_info:
            svc.create_child(_educator(), ChildProfileCreate(name="Alice"))
        assert exc_info.value.status_code == 403

    def test_list_children_raises_403_for_educator(self):
        mock_db = MagicMock()
        svc = ChildrenService(db=mock_db)
        with pytest.raises(HTTPException) as exc_info:
            svc.list_children(_educator())
        assert exc_info.value.status_code == 403

    def test_get_child_raises_403_for_educator(self):
        mock_db = MagicMock()
        svc = ChildrenService(db=mock_db)
        with pytest.raises(HTTPException) as exc_info:
            svc.get_child(_educator(), child_id=1)
        assert exc_info.value.status_code == 403

    def test_delete_child_raises_403_for_educator(self):
        mock_db = MagicMock()
        svc = ChildrenService(db=mock_db)
        with pytest.raises(HTTPException) as exc_info:
            svc.delete_child(_educator(), child_id=1)
        assert exc_info.value.status_code == 403

    def test_generate_guide_raises_403_for_educator(self):
        mock_db = MagicMock()
        svc = ChildrenService(db=mock_db)
        with pytest.raises(HTTPException) as exc_info:
            svc.generate_guide(_educator(), child_id=1, topic_id=1)
        assert exc_info.value.status_code == 403


# ---------------------------------------------------------------------------
# Ownership — _get_child_or_404
# ---------------------------------------------------------------------------

class TestOwnership:
    """_get_child_or_404 returns child when owner matches, 404 otherwise."""

    def _db_returns(self, child_or_none):
        mock_db = MagicMock()
        q = MagicMock()
        q.options.return_value.filter.return_value.first.return_value = child_or_none
        mock_db.query.return_value = q
        return mock_db

    def test_returns_child_for_correct_owner(self):
        c = _child(child_id=5, parent_id=1)
        svc = ChildrenService(db=self._db_returns(c))
        result = svc._get_child_or_404(child_id=5, parent_id=1)
        assert result.child_id == 5

    def test_raises_404_when_child_not_found(self):
        svc = ChildrenService(db=self._db_returns(None))
        with pytest.raises(HTTPException) as exc_info:
            svc._get_child_or_404(child_id=99, parent_id=1)
        assert exc_info.value.status_code == 404

    def test_get_child_returns_404_for_wrong_parent(self):
        """get_child uses parent_id from user — wrong user → 404."""
        svc = ChildrenService(db=self._db_returns(None))
        parent_a = _parent(user_id=1)
        # DB returns None because parent_id filter doesn't match parent_a
        with pytest.raises(HTTPException) as exc_info:
            svc.get_child(parent_a, child_id=5)
        assert exc_info.value.status_code == 404

    def test_update_child_returns_404_for_wrong_parent(self):
        svc = ChildrenService(db=self._db_returns(None))
        parent_a = _parent(user_id=1)
        with pytest.raises(HTTPException) as exc_info:
            svc.update_child(parent_a, child_id=5, data=ChildProfileUpdate(name="X"))
        assert exc_info.value.status_code == 404

    def test_delete_child_returns_404_for_wrong_parent(self):
        svc = ChildrenService(db=self._db_returns(None))
        parent_a = _parent(user_id=1)
        with pytest.raises(HTTPException) as exc_info:
            svc.delete_child(parent_a, child_id=5)
        assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# create_child FK validation
# ---------------------------------------------------------------------------

class TestCreateChildFKValidation:
    """create_child raises 400 when FK IDs don't exist in the DB."""

    def _db_fk_fails(self, model_to_fail):
        """DB where query for model_to_fail returns None (FK invalid)."""
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
        mock_db = self._db_fk_fails(Subject)
        svc = ChildrenService(db=mock_db)
        with pytest.raises(HTTPException) as exc_info:
            svc.create_child(
                _parent(),
                ChildProfileCreate(name="Alice", subjects=[42]),
            )
        assert exc_info.value.status_code == 400
        assert "subject_id" in exc_info.value.detail


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
# generate_guide idempotency
# ---------------------------------------------------------------------------

class TestGenerateGuideIdempotency:
    """If a guide already exists for child+topic, AI must not be called."""

    def _db_with_existing_guide(self, existing: ParentGuide, child: ChildProfile):
        mock_db = MagicMock()
        call_count = [0]

        def query_side(model):
            call_count[0] += 1
            q = MagicMock()
            if model is ChildProfile:
                q.options.return_value.filter.return_value.first.return_value = child
            elif model is ParentGuide:
                # Service uses a single .filter(child_id=..., topic_id=...) call
                q.options.return_value.filter.return_value.first.return_value = existing
            return q

        mock_db.query.side_effect = query_side
        return mock_db

    def test_existing_guide_returned_no_ai_instantiated(self):
        parent = _parent(user_id=1)
        child_obj = _child(child_id=5, parent_id=1)
        existing = _guide(guide_id=55, child_id=5, topic_id=3)

        mock_db = self._db_with_existing_guide(existing, child_obj)
        svc = ChildrenService(db=mock_db)
        svc._get_child_or_404 = MagicMock(return_value=child_obj)

        with patch("packages.ai.gpt_service.AwadeGPTService") as MockAI:
            result = svc.generate_guide(parent, child_id=5, topic_id=3)
            MockAI.assert_not_called()

        assert result.guide_id == 55
        mock_db.add.assert_not_called()
        mock_db.commit.assert_not_called()

    def test_existing_guide_second_call_same_result(self):
        """Two identical calls return the same guide_id without writing to DB."""
        parent = _parent(user_id=1)
        child_obj = _child(child_id=5, parent_id=1)
        existing = _guide(guide_id=55, child_id=5, topic_id=3)

        mock_db = self._db_with_existing_guide(existing, child_obj)
        svc = ChildrenService(db=mock_db)
        svc._get_child_or_404 = MagicMock(return_value=child_obj)

        with patch("packages.ai.gpt_service.AwadeGPTService"):
            first = svc.generate_guide(parent, child_id=5, topic_id=3)
            second = svc.generate_guide(parent, child_id=5, topic_id=3)

        assert first.guide_id == second.guide_id


# ---------------------------------------------------------------------------
# generate_guide AI validation
# ---------------------------------------------------------------------------

class TestGenerateGuideAIValidation:
    """Malformed AI JSON must raise HTTP 502 and must not persist anything."""

    def _db_no_existing_guide(self, child_obj: ChildProfile):
        """DB where no guide exists and topic query returns a mock topic."""
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
        mock_db = MagicMock()

        def query_side(model):
            call_count[0] += 1
            q = MagicMock()
            if model is ParentGuide:
                inner = MagicMock()
                inner.first.return_value = None
                # Service uses a single .filter(child_id=..., topic_id=...) call
                q.options.return_value.filter.return_value = inner
            elif model is Topic:
                q.options.return_value.filter.return_value.first.return_value = mock_topic
            else:
                q.options.return_value.filter.return_value.first.return_value = child_obj
                q.filter.return_value.first.return_value = child_obj
            return q

        mock_db.query.side_effect = query_side
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock()
        mock_db.refresh = MagicMock()
        return mock_db

    def test_invalid_json_raises_502(self):
        parent = _parent(user_id=1)
        child_obj = _child(child_id=5, parent_id=1)
        child_obj.country = MagicMock()
        child_obj.country.country_name = "Nigeria"
        mock_db = self._db_no_existing_guide(child_obj)
        svc = ChildrenService(db=mock_db)
        svc._get_child_or_404 = MagicMock(return_value=child_obj)

        with patch("packages.ai.gpt_service.AwadeGPTService") as MockAI:
            instance = MockAI.return_value
            instance.generate_parent_guide.return_value = ("not-json{{{", True)
            with pytest.raises(HTTPException) as exc_info:
                svc.generate_guide(parent, child_id=5, topic_id=1)

        assert exc_info.value.status_code == 502
        mock_db.add.assert_not_called()
        mock_db.commit.assert_not_called()

    def test_missing_required_field_raises_502(self):
        parent = _parent(user_id=1)
        child_obj = _child(child_id=5, parent_id=1)
        child_obj.country = MagicMock()
        child_obj.country.country_name = "Nigeria"
        mock_db = self._db_no_existing_guide(child_obj)
        svc = ChildrenService(db=mock_db)
        svc._get_child_or_404 = MagicMock(return_value=child_obj)

        bad = {k: v for k, v in VALID_AI_CONTENT.items() if k != "home_activity"}

        with patch("packages.ai.gpt_service.AwadeGPTService") as MockAI:
            instance = MockAI.return_value
            instance.generate_parent_guide.return_value = (json.dumps(bad), False)
            with pytest.raises(HTTPException) as exc_info:
                svc.generate_guide(parent, child_id=5, topic_id=1)

        assert exc_info.value.status_code == 502

    def test_valid_ai_json_persists_guide(self):
        parent = _parent(user_id=1)
        child_obj = _child(child_id=5, parent_id=1)
        child_obj.country = MagicMock()
        child_obj.country.country_name = "Nigeria"
        mock_db = self._db_no_existing_guide(child_obj)

        # The final reload query — add a ParentGuide query chain at the end
        reload_guide = _guide(guide_id=77, child_id=5, topic_id=1)
        reload_q = MagicMock()
        reload_q.options.return_value.filter.return_value.first.return_value = reload_guide

        call_count = [0]
        original_side = mock_db.query.side_effect

        def patched_query_side(model):
            call_count[0] += 1
            # _get_child_or_404 is mocked so 3 DB calls occur:
            #   #1 ParentGuide existence, #2 Topic fetch, #3 ParentGuide reload
            if call_count[0] >= 3 and model is ParentGuide:
                return reload_q
            return original_side(model)

        mock_db.query.side_effect = patched_query_side

        svc = ChildrenService(db=mock_db)
        svc._get_child_or_404 = MagicMock(return_value=child_obj)

        with patch("packages.ai.gpt_service.AwadeGPTService") as MockAI:
            instance = MockAI.return_value
            instance.generate_parent_guide.return_value = (
                json.dumps(VALID_AI_CONTENT), True
            )
            result = svc.generate_guide(parent, child_id=5, topic_id=1)

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        assert result.guide_id == 77


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
