"""
AWD-M-182: ChildrenService tests — guide management.

Covers:
  - TestGenerateGuideIdempotency: existing guide returned without AI call
  - TestGenerateGuideAIValidation: malformed AI JSON raises HTTP 502
  - TestListGuides: role gate, ownership, filters
  - TestGetGuide: role gate, ownership, 404, 200
  - TestToggleBookmark: role gate, 404, toggle logic
"""

import json
import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException

from children_service_factories import (
    _parent, _educator, _child, _guide,
    VALID_AI_CONTENT, _db_child_not_found,
)

from apps.backend.models import ChildProfile, ParentGuide, Topic
from apps.backend.services.children_service import ChildrenService
from packages.ai.gpt_service import ParentGuideRequest


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

        with patch("apps.backend.services.children_service.AwadeGPTService") as MockAI:
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

        with patch("apps.backend.services.children_service.AwadeGPTService"):
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
        cs.curriculum.curriculum_title = "Nigerian Curriculum"
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

        with patch("apps.backend.services.children_service.AwadeGPTService") as MockAI:
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

        with patch("apps.backend.services.children_service.AwadeGPTService") as MockAI:
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

        with patch("apps.backend.services.children_service.AwadeGPTService") as MockAI:
            instance = MockAI.return_value
            instance.generate_parent_guide.return_value = (
                json.dumps(VALID_AI_CONTENT), True
            )
            result = svc.generate_guide(parent, child_id=5, topic_id=1)

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        assert result.guide_id == 77


# ---------------------------------------------------------------------------
# AWD-M-04 — Guide management: list_guides, get_guide, toggle_bookmark
# ---------------------------------------------------------------------------

class TestListGuides:
    """ChildrenService.list_guides — role gate, ownership, filters."""

    def test_educator_raises_403(self):
        svc = ChildrenService(db=MagicMock())
        with pytest.raises(HTTPException) as exc_info:
            svc.list_guides(_educator(), child_id=1)
        assert exc_info.value.status_code == 403

    def test_wrong_parent_raises_404(self):
        """Child not owned by this parent → 404 via _get_child_or_404."""
        db = _db_child_not_found()
        svc = ChildrenService(db=db)
        with pytest.raises(HTTPException) as exc_info:
            svc.list_guides(_parent(user_id=99), child_id=1)
        assert exc_info.value.status_code == 404

    def test_returns_all_guides_for_child(self):
        parent = _parent(user_id=1)
        child_obj = _child(child_id=5, parent_id=1)
        guide1 = _guide(guide_id=10, child_id=5, topic_id=1)
        guide2 = _guide(guide_id=11, child_id=5, topic_id=2)

        db = MagicMock()
        call_count = [0]

        def query_side(model_arg):
            q = MagicMock()
            call_count[0] += 1
            if call_count[0] == 1:
                # _get_child_or_404
                q.options.return_value.filter.return_value.first.return_value = child_obj
                q.filter.return_value.first.return_value = child_obj
            else:
                # list_guides main query
                q.options.return_value.filter.return_value.filter.return_value.order_by.return_value.all.return_value = [guide1, guide2]
                q.options.return_value.filter.return_value.order_by.return_value.all.return_value = [guide1, guide2]
            return q

        db.query.side_effect = query_side
        svc = ChildrenService(db=db)
        result = svc.list_guides(parent, child_id=5)
        assert result.total == 2
        assert len(result.guides) == 2

    def test_bookmarked_only_filter_applied(self):
        """bookmarked_only=True adds an extra filter; service should not crash."""
        parent = _parent(user_id=1)
        child_obj = _child(child_id=5, parent_id=1)

        db = MagicMock()
        call_count = [0]

        def query_side(model_arg):
            q = MagicMock()
            call_count[0] += 1
            if call_count[0] == 1:
                q.options.return_value.filter.return_value.first.return_value = child_obj
                q.filter.return_value.first.return_value = child_obj
            else:
                # Double-filter chain for bookmarked_only
                q.options.return_value.filter.return_value.filter.return_value.order_by.return_value.all.return_value = []
            return q

        db.query.side_effect = query_side
        svc = ChildrenService(db=db)
        result = svc.list_guides(parent, child_id=5, bookmarked_only=True)
        assert result.total == 0

    def test_returns_empty_when_no_guides(self):
        parent = _parent(user_id=1)
        child_obj = _child(child_id=5, parent_id=1)

        db = MagicMock()
        call_count = [0]

        def query_side(model_arg):
            q = MagicMock()
            call_count[0] += 1
            if call_count[0] == 1:
                q.options.return_value.filter.return_value.first.return_value = child_obj
                q.filter.return_value.first.return_value = child_obj
            else:
                q.options.return_value.filter.return_value.order_by.return_value.all.return_value = []
            return q

        db.query.side_effect = query_side
        svc = ChildrenService(db=db)
        result = svc.list_guides(parent, child_id=5)
        assert result.total == 0
        assert result.guides == []


class TestGetGuide:
    """ChildrenService.get_guide — role gate, ownership, 404, 200."""

    def test_educator_raises_403(self):
        svc = ChildrenService(db=MagicMock())
        with pytest.raises(HTTPException) as exc_info:
            svc.get_guide(_educator(), guide_id=1)
        assert exc_info.value.status_code == 403

    def test_guide_not_found_raises_404(self):
        db = MagicMock()
        q = MagicMock()
        q.options.return_value.join.return_value.filter.return_value.first.return_value = None
        db.query.return_value = q
        svc = ChildrenService(db=db)
        with pytest.raises(HTTPException) as exc_info:
            svc.get_guide(_parent(user_id=1), guide_id=999)
        assert exc_info.value.status_code == 404

    def test_guide_belonging_to_other_parent_returns_404(self):
        """The join on ChildProfile ensures cross-parent access → None → 404."""
        db = MagicMock()
        q = MagicMock()
        # Simulate DB join returning nothing for wrong parent
        q.options.return_value.join.return_value.filter.return_value.first.return_value = None
        db.query.return_value = q
        svc = ChildrenService(db=db)
        with pytest.raises(HTTPException) as exc_info:
            svc.get_guide(_parent(user_id=99), guide_id=10)
        assert exc_info.value.status_code == 404

    def test_returns_guide_response_for_owner(self):
        parent = _parent(user_id=1)
        guide_obj = _guide(guide_id=10, child_id=5, topic_id=1)
        guide_obj.ai_generated_content = '{"topic": "Fractions"}'
        guide_obj.updated_at = guide_obj.created_at

        db = MagicMock()
        q = MagicMock()
        q.options.return_value.join.return_value.filter.return_value.first.return_value = guide_obj
        db.query.return_value = q
        svc = ChildrenService(db=db)
        result = svc.get_guide(parent, guide_id=10)
        assert result.guide_id == 10
        assert result.child_id == 5
        assert result.topic_id == 1
        assert result.topic_title == "Fractions"

    def test_is_bookmarked_is_bool(self):
        """is_bookmarked Boolean column returns bool in response."""
        parent = _parent(user_id=1)
        guide_obj = _guide(guide_id=10, child_id=5)
        guide_obj.is_bookmarked = True
        guide_obj.updated_at = guide_obj.created_at

        db = MagicMock()
        q = MagicMock()
        q.options.return_value.join.return_value.filter.return_value.first.return_value = guide_obj
        db.query.return_value = q
        svc = ChildrenService(db=db)
        result = svc.get_guide(parent, guide_id=10)
        assert result.is_bookmarked is True
        assert isinstance(result.is_bookmarked, bool)


class TestToggleBookmark:
    """ChildrenService.toggle_bookmark — role gate, 404, toggle logic."""

    def _db_with_guide(self, guide_obj) -> MagicMock:
        db = MagicMock()
        q = MagicMock()
        q.options.return_value.join.return_value.filter.return_value.first.return_value = guide_obj
        db.query.return_value = q
        db.commit = MagicMock()
        db.refresh = MagicMock()
        return db

    def _db_no_guide(self) -> MagicMock:
        db = MagicMock()
        q = MagicMock()
        q.options.return_value.join.return_value.filter.return_value.first.return_value = None
        db.query.return_value = q
        return db

    def test_educator_raises_403(self):
        svc = ChildrenService(db=MagicMock())
        with pytest.raises(HTTPException) as exc_info:
            svc.toggle_bookmark(_educator(), guide_id=1)
        assert exc_info.value.status_code == 403

    def test_guide_not_found_raises_404(self):
        svc = ChildrenService(db=self._db_no_guide())
        with pytest.raises(HTTPException) as exc_info:
            svc.toggle_bookmark(_parent(user_id=1), guide_id=99)
        assert exc_info.value.status_code == 404

    def test_toggle_unbookmarked_to_bookmarked(self):
        parent = _parent(user_id=1)
        guide_obj = _guide(guide_id=10, child_id=5)
        guide_obj.is_bookmarked = False
        guide_obj.updated_at = guide_obj.created_at

        db = self._db_with_guide(guide_obj)

        def refresh_side_effect(obj):
            # refresh doesn't change anything; guide_obj was mutated in place
            pass

        db.refresh.side_effect = refresh_side_effect
        svc = ChildrenService(db=db)
        result = svc.toggle_bookmark(parent, guide_id=10)

        assert guide_obj.is_bookmarked is True, "Expected is_bookmarked to be set to True"
        db.commit.assert_called_once()
        assert result.is_bookmarked is True

    def test_toggle_bookmarked_to_unbookmarked(self):
        parent = _parent(user_id=1)
        guide_obj = _guide(guide_id=11, child_id=5)
        guide_obj.is_bookmarked = True
        guide_obj.updated_at = guide_obj.created_at

        db = self._db_with_guide(guide_obj)
        db.refresh.side_effect = lambda obj: None
        svc = ChildrenService(db=db)
        result = svc.toggle_bookmark(parent, guide_id=11)

        assert guide_obj.is_bookmarked is False, "Expected is_bookmarked to be set to False"
        db.commit.assert_called_once()
        assert result.is_bookmarked is False

    def test_commit_called_on_toggle(self):
        parent = _parent(user_id=1)
        guide_obj = _guide(guide_id=10, child_id=5)
        guide_obj.is_bookmarked = False
        guide_obj.updated_at = guide_obj.created_at

        db = self._db_with_guide(guide_obj)
        db.refresh.side_effect = lambda obj: None
        svc = ChildrenService(db=db)
        svc.toggle_bookmark(parent, guide_id=10)
        db.commit.assert_called_once()


# ---------------------------------------------------------------------------
# AWD-M-185 — _build_guide_ai_payload + _persist_guide helpers
# ---------------------------------------------------------------------------

class TestBuildGuideAIPayloadM185:
    """Unit tests for ChildrenService._build_guide_ai_payload (AWD-M-185)."""

    def _mock_topic(
        self,
        title="Fractions",
        subject="Mathematics",
        grade="Grade 5",
        curriculum_title="Nigerian Curriculum",
        objectives=None,
        contents=None,
        student_activities=None,
        teaching_materials=None,
        evaluation_guide=None,
    ):
        cs = MagicMock()
        cs.subject.name = subject
        cs.grade_level.name = grade
        cs.curriculum.curriculum_title = curriculum_title

        topic = MagicMock()
        topic.topic_title = title
        topic.curriculum_structure = cs

        obj1 = MagicMock()
        obj1.objective = objectives[0] if objectives else "Understand halves"
        topic.learning_objectives = [obj1]

        c1 = MagicMock()
        c1.content_area = contents[0] if contents else "Introduction to fractions"
        topic.topic_contents = [c1]

        # NERDC pedagogy collections (AWD-M-208)
        def _items(values, field):
            mocks = []
            for value in values or []:
                m = MagicMock()
                setattr(m, field, value)
                mocks.append(m)
            return mocks

        topic.student_activities = _items(student_activities, "activity")
        topic.teaching_learning_materials = _items(teaching_materials, "material")
        topic.evaluation_guides = _items(evaluation_guide, "guide_item")
        return topic

    def _mock_child(self, country_name="Nigeria"):
        child = MagicMock()
        country = MagicMock()
        country.country_name = country_name
        child.country = country
        return child

    def test_payload_contains_expected_keys(self):
        svc = ChildrenService(db=MagicMock())
        payload = svc._build_guide_ai_payload(
            self._mock_child(), self._mock_topic()
        )
        assert set(payload.keys()) == {
            "subject", "grade", "topic", "country", "curriculum",
            "objectives", "contents",
            "student_activities", "teaching_learning_materials", "evaluation_guide",
        }

    def test_payload_includes_pedagogy_fields(self):
        """AWD-M-208: NERDC pedagogy collections flow into the AI payload."""
        svc = ChildrenService(db=MagicMock())
        topic = self._mock_topic(
            student_activities=["Group counting game", "Sort objects by size"],
            teaching_materials=["Counters", "Chart of shapes"],
            evaluation_guide=["Ask the child to name three shapes"],
        )
        payload = svc._build_guide_ai_payload(self._mock_child(), topic)

        assert payload["student_activities"] == [
            "Group counting game", "Sort objects by size",
        ]
        assert payload["teaching_learning_materials"] == ["Counters", "Chart of shapes"]
        assert payload["evaluation_guide"] == ["Ask the child to name three shapes"]

    def test_payload_pedagogy_fields_default_empty(self):
        """Topics imported before AWD-M-208 have no pedagogy rows — payload stays valid."""
        svc = ChildrenService(db=MagicMock())
        payload = svc._build_guide_ai_payload(self._mock_child(), self._mock_topic())
        assert payload["student_activities"] == []
        assert payload["teaching_learning_materials"] == []
        assert payload["evaluation_guide"] == []

    def test_payload_values_match_topic_and_child(self):
        svc = ChildrenService(db=MagicMock())
        topic = self._mock_topic(
            title="Algebra",
            subject="Maths",
            grade="JSS1",
            curriculum_title="Lagos Curriculum",
            objectives=["Solve linear equations"],
            contents=["Introduction to variables"],
        )
        child = self._mock_child(country_name="Ghana")
        payload = svc._build_guide_ai_payload(child, topic)

        assert payload["topic"] == "Algebra"
        assert payload["subject"] == "Maths"
        assert payload["grade"] == "JSS1"
        assert payload["curriculum"] == "Lagos Curriculum"
        assert payload["country"] == "Ghana"
        assert payload["objectives"] == ["Solve linear equations"]
        assert payload["contents"] == ["Introduction to variables"]

    def test_missing_curriculum_structure_uses_defaults(self):
        """When curriculum_structure is None, defaults are applied."""
        svc = ChildrenService(db=MagicMock())
        topic = MagicMock()
        topic.topic_title = "Decimals"
        topic.curriculum_structure = None
        topic.learning_objectives = []
        topic.topic_contents = []

        child = MagicMock()
        child.country = None

        payload = svc._build_guide_ai_payload(child, topic)
        assert payload["subject"] == "Unknown Subject"
        assert payload["grade"] == "Unknown Grade"
        assert payload["curriculum"] == "National Curriculum"
        assert payload["country"] == "Nigeria"
        assert payload["objectives"] == []
        assert payload["contents"] == []

    def test_multiple_objectives_and_contents(self):
        svc = ChildrenService(db=MagicMock())
        cs = MagicMock()
        cs.subject.name = "Science"
        cs.grade_level.name = "SS1"
        cs.curriculum.curriculum_title = "National"

        topic = MagicMock()
        topic.topic_title = "Photosynthesis"
        topic.curriculum_structure = cs

        obj1, obj2 = MagicMock(), MagicMock()
        obj1.objective = "Explain the process"
        obj2.objective = "Identify reactants"
        topic.learning_objectives = [obj1, obj2]

        c1, c2 = MagicMock(), MagicMock()
        c1.content_area = "Light energy"
        c2.content_area = "Chlorophyll"
        topic.topic_contents = [c1, c2]

        child = self._mock_child("Nigeria")
        payload = svc._build_guide_ai_payload(child, topic)
        assert payload["objectives"] == ["Explain the process", "Identify reactants"]
        assert payload["contents"] == ["Light energy", "Chlorophyll"]


# ---------------------------------------------------------------------------
# AWD-H-98 — ParentGuideRequest TypedDict + single-arg call site
# ---------------------------------------------------------------------------

class TestParentGuideRequestH98:
    """Verify ParentGuideRequest TypedDict and the refactored call surface."""

    _REQUIRED_KEYS = {
        "subject", "grade", "topic", "country", "curriculum",
        "objectives", "contents", "student_activities",
        "teaching_learning_materials", "evaluation_guide",
    }

    def _minimal_request(self) -> ParentGuideRequest:
        return ParentGuideRequest(
            subject="Mathematics",
            grade="JSS1",
            topic="Fractions",
            country="Nigeria",
            curriculum="NERDC",
            objectives=["Understand halves"],
            contents=["Intro to fractions"],
            student_activities=[],
            teaching_learning_materials=[],
            evaluation_guide=[],
        )

    def test_parent_guide_request_has_all_required_keys(self):
        req = self._minimal_request()
        assert set(req.keys()) == self._REQUIRED_KEYS

    def test_build_guide_ai_payload_returns_parent_guide_request_shape(self):
        """_build_guide_ai_payload always returns the full ParentGuideRequest key-set."""
        svc = ChildrenService(db=MagicMock())
        cs = MagicMock()
        cs.subject.name = "Science"
        cs.grade_level.name = "SS2"
        cs.curriculum.curriculum_title = "Federal"
        topic = MagicMock()
        topic.topic_title = "Photosynthesis"
        topic.curriculum_structure = cs
        topic.learning_objectives = []
        topic.topic_contents = []
        topic.student_activities = []
        topic.teaching_learning_materials = []
        topic.evaluation_guides = []
        child = MagicMock()
        child.country.country_name = "Nigeria"

        payload = svc._build_guide_ai_payload(child, topic)
        assert set(payload.keys()) == self._REQUIRED_KEYS

    def test_build_guide_ai_payload_result_is_valid_parent_guide_request(self):
        """_build_guide_ai_payload returns a dict usable as ParentGuideRequest directly."""
        svc = ChildrenService(db=MagicMock())
        cs = MagicMock()
        cs.subject.name = "Mathematics"
        cs.grade_level.name = "JSS1"
        cs.curriculum.curriculum_title = "NERDC"
        topic = MagicMock()
        topic.topic_title = "Fractions"
        topic.curriculum_structure = cs
        o = MagicMock(); o.objective = "Understand halves"
        topic.learning_objectives = [o]
        c = MagicMock(); c.content_area = "Intro to fractions"
        topic.topic_contents = [c]
        a = MagicMock(); a.activity = "Counting game"
        topic.student_activities = [a]
        topic.teaching_learning_materials = []
        topic.evaluation_guides = []
        child = MagicMock()
        child.country.country_name = "Nigeria"

        payload = svc._build_guide_ai_payload(child, topic)
        # Should be directly passable as a ParentGuideRequest (same key set)
        req: ParentGuideRequest = payload
        assert req["subject"] == "Mathematics"
        assert req["grade"] == "JSS1"
        assert req["topic"] == "Fractions"
        assert req["country"] == "Nigeria"
        assert req["curriculum"] == "NERDC"
        assert req["objectives"] == ["Understand halves"]
        assert req["contents"] == ["Intro to fractions"]
        assert req["student_activities"] == ["Counting game"]


class TestPersistGuideM185:
    """Unit tests for ChildrenService._persist_guide (AWD-M-185)."""

    def _db_persist_ok(self, reload_guide) -> MagicMock:
        """DB mock that succeeds on add/commit/refresh and returns reload_guide."""
        db = MagicMock()
        db.add = MagicMock()
        db.commit = MagicMock()
        db.refresh = MagicMock()
        reload_q = MagicMock()
        reload_q.options.return_value.filter.return_value.first.return_value = reload_guide
        db.query.return_value = reload_q
        return db

    def test_adds_and_commits_guide(self):
        reload_guide = _guide(guide_id=42, child_id=5, topic_id=3)
        db = self._db_persist_ok(reload_guide)
        svc = ChildrenService(db=db)
        result = svc._persist_guide(child_id=5, topic_id=3, ai_content='{"key": "val"}')
        db.add.assert_called_once()
        db.commit.assert_called_once()
        assert result.guide_id == 42

    def test_db_error_raises_500_and_rolls_back(self):
        db = MagicMock()
        db.add = MagicMock()
        db.commit.side_effect = Exception("disk full")
        db.rollback = MagicMock()

        svc = ChildrenService(db=db)
        with pytest.raises(HTTPException) as exc_info:
            svc._persist_guide(child_id=5, topic_id=3, ai_content='{}')

        assert exc_info.value.status_code == 500
        db.rollback.assert_called_once()

    def test_http_exception_propagated_unchanged(self):
        """An HTTPException raised in commit must not be wrapped."""
        db = MagicMock()
        db.commit.side_effect = HTTPException(status_code=409, detail="conflict")
        svc = ChildrenService(db=db)
        with pytest.raises(HTTPException) as exc_info:
            svc._persist_guide(child_id=5, topic_id=3, ai_content='{}')
        assert exc_info.value.status_code == 409

    def test_reload_query_uses_returned_guide_id(self):
        """After commit, _persist_guide reloads using the guide_id assigned by the DB."""
        from apps.backend.models import ParentGuide

        reload_guide = _guide(guide_id=99, child_id=5, topic_id=3)
        db = MagicMock()
        db.add = MagicMock()
        db.commit = MagicMock()

        # refresh sets guide_id on the new ParentGuide instance
        def mock_refresh(obj):
            obj.guide_id = 99

        db.refresh.side_effect = mock_refresh
        reload_q = MagicMock()
        reload_q.options.return_value.filter.return_value.first.return_value = reload_guide
        db.query.return_value = reload_q

        svc = ChildrenService(db=db)
        result = svc._persist_guide(child_id=5, topic_id=3, ai_content='{"key": "val"}')
        assert result.guide_id == 99

    def test_persist_guide_reload_returns_none_raises_500(self):
        """AWD-M-188: if reload after commit returns None, _persist_guide raises HTTP 500."""
        db = MagicMock()
        db.add = MagicMock()
        db.commit = MagicMock()
        db.refresh = MagicMock()
        reload_q = MagicMock()
        # Simulate the guide disappearing before the reload query completes
        reload_q.options.return_value.filter.return_value.first.return_value = None
        db.query.return_value = reload_q

        svc = ChildrenService(db=db)
        with pytest.raises(HTTPException) as exc_info:
            svc._persist_guide(child_id=5, topic_id=3, ai_content='{"key": "val"}')

        assert exc_info.value.status_code == 500
        assert "reload" in exc_info.value.detail.lower()
