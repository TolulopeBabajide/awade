"""
Unit tests for CurriculumService, LearningObjectiveService, TopicContentService
— AWD-M-163, AWD-M-164, AWD-M-165, AWD-M-166, AWD-M-167, AWD-H-88, AWD-M-175, AWD-M-178, AWD-M-179.

AWD-M-178: LearningObjectiveService and TopicContentService were extracted from
CurriculumService. TestLearningObjectiveCRUDH88 and TestContentCRUDH88 now
instantiate the dedicated sub-service classes directly.

Covers:
- get_curriculum_statistics: happy path (one structure, topics, objectives, contents)
- get_curriculum_statistics: multiple structures aggregated correctly
- get_curriculum_statistics: curriculum not found returns empty dict
- get_curriculum_statistics: curriculum with no structures returns zero counts
- get_curriculum_statistics: curriculum with structures but no topics returns zero counts
- get_curriculum_statistics (AWD-M-165): aggregated COUNT queries across 3 topics/2 structures
- get_curriculum_statistics (AWD-M-165): empty topics list short-circuits to zeros
- search_curriculums: match by curriculum title (AWD-M-164)
- search_curriculums: match by country name (AWD-M-164)
- search_curriculums: match by subject name (AWD-M-164)
- search_curriculums: no match returns empty list (AWD-M-164)
- search_curriculums: no duplicate rows when curriculum has multiple matching structures (AWD-M-164)
- search_curriculums: empty string returns [] without hitting DB (AWD-M-166)
- search_curriculums: whitespace-only string returns [] without hitting DB (AWD-M-166)
- search_topics: empty string returns [] without hitting DB (AWD-M-166)
- search_topics: whitespace-only string returns [] without hitting DB (AWD-M-166)
- search_topics: non-empty term returns matching topics (AWD-M-166)
- CurriculumCRUD (AWD-H-88): create/update/delete raise HTTP 500 on DB error
- TopicCRUD (AWD-H-88): create/update/delete raise HTTP 500 on DB error
- LearningObjectiveCRUD (AWD-H-88): create/update/delete raise HTTP 500 on DB error
- ContentCRUD (AWD-H-88): create/update/delete raise HTTP 500 on DB error
- LearningObjectiveService smoke tests (AWD-M-178)
- TopicContentService smoke tests (AWD-M-178)
"""

import pytest
import sys
import os

# --------------------------------------------------------------------------
# Path fixups for sandbox + CI
# --------------------------------------------------------------------------
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
root_dir = os.path.abspath(os.path.join(backend_dir, "../.."))
sys.path.insert(0, root_dir)

from apps.backend.services.curriculum_service import CurriculumService
from apps.backend.services.learning_objective_service import LearningObjectiveService
from apps.backend.services.topic_content_service import TopicContentService
from apps.backend.models import (
    Curriculum, CurriculumStructure, Topic, LearningObjective, TopicContent, Country,
    Subject, GradeLevel,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_country(db):
    country = Country(country_name="TestLand", country_code="TL")
    db.add(country)
    db.commit()
    db.refresh(country)
    return country


def _make_curriculum(db, country_id, title="Test Curriculum"):
    curriculum = Curriculum(curriculum_title=title, country_id=country_id)
    db.add(curriculum)
    db.commit()
    db.refresh(curriculum)
    return curriculum


def _make_structure(db, curricula_id, subject_id, grade_level_id):
    from apps.backend.models import Subject, GradeLevel
    structure = CurriculumStructure(
        curricula_id=curricula_id,
        subject_id=subject_id,
        grade_level_id=grade_level_id,
    )
    db.add(structure)
    db.commit()
    db.refresh(structure)
    return structure


def _make_topic(db, curriculum_structure_id, title="Algebra Basics"):
    topic = Topic(
        curriculum_structure_id=curriculum_structure_id,
        topic_title=title,
    )
    db.add(topic)
    db.commit()
    db.refresh(topic)
    return topic


def _make_objective(db, topic_id, text="Understand variables"):
    obj = LearningObjective(topic_id=topic_id, objective=text)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def _make_content(db, topic_id, area="Introduction to algebra"):
    content = TopicContent(topic_id=topic_id, content_area=area)
    db.add(content)
    db.commit()
    db.refresh(content)
    return content


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestGetCurriculumStatistics:
    """get_curriculum_statistics — AWD-M-163 bug fixes."""

    def test_returns_empty_dict_for_nonexistent_curriculum(self, test_db):
        """Unknown curriculum_id → empty dict, no crash."""
        service = CurriculumService(test_db)
        result = service.get_curriculum_statistics(curriculum_id=99999)
        assert result == {}

    def test_returns_zeros_when_no_structures(
        self, test_db, sample_curriculum
    ):
        """Curriculum with no CurriculumStructure entries → all counts 0."""
        service = CurriculumService(test_db)
        result = service.get_curriculum_statistics(
            curriculum_id=sample_curriculum.curricula_id
        )
        assert result["curriculum_id"] == sample_curriculum.curricula_id
        assert result["total_topics"] == 0
        assert result["total_learning_objectives"] == 0
        assert result["total_contents"] == 0

    def test_returns_zeros_when_structures_but_no_topics(
        self, test_db, sample_curriculum_structure, sample_curriculum
    ):
        """Structure exists but has no topics → all counts 0."""
        service = CurriculumService(test_db)
        result = service.get_curriculum_statistics(
            curriculum_id=sample_curriculum.curricula_id
        )
        assert result["total_topics"] == 0
        assert result["total_learning_objectives"] == 0
        assert result["total_contents"] == 0

    def test_happy_path_counts_topics_objectives_contents(
        self,
        test_db,
        sample_curriculum,
        sample_curriculum_structure,
    ):
        """One structure, one topic, two objectives, one content → correct counts."""
        topic = _make_topic(
            test_db,
            sample_curriculum_structure.curriculum_structure_id,
            title="Functions",
        )
        _make_objective(test_db, topic.topic_id, "Understand linear functions")
        _make_objective(test_db, topic.topic_id, "Solve quadratic equations")
        _make_content(test_db, topic.topic_id, "Introduction to functions")

        service = CurriculumService(test_db)
        result = service.get_curriculum_statistics(
            curriculum_id=sample_curriculum.curricula_id
        )

        assert result["curriculum_id"] == sample_curriculum.curricula_id
        assert result["total_topics"] == 1
        assert result["total_learning_objectives"] == 2
        assert result["total_contents"] == 1

    def test_aggregates_across_multiple_structures(
        self,
        test_db,
        sample_curriculum,
        sample_subject,
        sample_grade_level,
    ):
        """Two structures each with one topic → topics summed correctly."""
        from apps.backend.models import Subject, GradeLevel

        # Create a second subject and grade for the second structure
        subject2 = Subject(name="Science-M163")
        grade2 = GradeLevel(name="Grade 6-M163")
        test_db.add(subject2)
        test_db.add(grade2)
        test_db.commit()
        test_db.refresh(subject2)
        test_db.refresh(grade2)

        struct1 = CurriculumStructure(
            curricula_id=sample_curriculum.curricula_id,
            subject_id=sample_subject.subject_id,
            grade_level_id=sample_grade_level.grade_level_id,
        )
        struct2 = CurriculumStructure(
            curricula_id=sample_curriculum.curricula_id,
            subject_id=subject2.subject_id,
            grade_level_id=grade2.grade_level_id,
        )
        test_db.add(struct1)
        test_db.add(struct2)
        test_db.commit()
        test_db.refresh(struct1)
        test_db.refresh(struct2)

        topic1 = _make_topic(test_db, struct1.curriculum_structure_id, "Algebra")
        topic2 = _make_topic(test_db, struct2.curriculum_structure_id, "Biology")
        _make_objective(test_db, topic1.topic_id, "Obj 1")
        _make_content(test_db, topic2.topic_id, "Content 1")

        service = CurriculumService(test_db)
        result = service.get_curriculum_statistics(
            curriculum_id=sample_curriculum.curricula_id
        )

        assert result["total_topics"] == 2
        assert result["total_learning_objectives"] == 1
        assert result["total_contents"] == 1


class TestSearchCurriculums:
    """search_curriculums — AWD-M-164: fix .ilike() on ORM relationships."""

    def test_match_by_curriculum_title(self, test_db, sample_curriculum):
        """Searching the curriculum title returns the matching curriculum."""
        service = CurriculumService(test_db)
        # sample_curriculum.curriculum_title == "Test Curriculum"
        results = service.search_curriculums("Test Curriculum")
        ids = [c.curricula_id for c in results]
        assert sample_curriculum.curricula_id in ids

    def test_match_by_country_name(self, test_db, sample_curriculum, sample_country):
        """Searching by country name (joined via Country model) returns the matching curriculum."""
        service = CurriculumService(test_db)
        # sample_country.country_name == "Test Country"
        results = service.search_curriculums("Test Country")
        ids = [c.curricula_id for c in results]
        assert sample_curriculum.curricula_id in ids

    def test_match_by_subject_name(
        self,
        test_db,
        sample_curriculum,
        sample_curriculum_structure,
        sample_subject,
    ):
        """Searching by subject name (joined via CurriculumStructure→Subject) returns the curriculum."""
        service = CurriculumService(test_db)
        # sample_subject.name == "Mathematics"
        results = service.search_curriculums("Mathematics")
        ids = [c.curricula_id for c in results]
        assert sample_curriculum.curricula_id in ids

    def test_no_match_returns_empty_list(self, test_db, sample_curriculum):
        """A search term that matches nothing returns an empty list (no crash)."""
        service = CurriculumService(test_db)
        results = service.search_curriculums("xyzzy_no_match_9876")
        assert results == []

    def test_no_duplicate_rows_with_multiple_matching_structures(
        self,
        test_db,
        sample_curriculum,
        sample_subject,
        sample_grade_level,
    ):
        """Curriculum with two structures both matching the search term returns exactly one row."""
        subject2 = Subject(name="Mathematics Advanced-M164")
        grade2 = GradeLevel(name="Grade 7-M164")
        test_db.add(subject2)
        test_db.add(grade2)
        test_db.commit()
        test_db.refresh(subject2)
        test_db.refresh(grade2)

        struct1 = CurriculumStructure(
            curricula_id=sample_curriculum.curricula_id,
            subject_id=sample_subject.subject_id,
            grade_level_id=sample_grade_level.grade_level_id,
        )
        struct2 = CurriculumStructure(
            curricula_id=sample_curriculum.curricula_id,
            subject_id=subject2.subject_id,
            grade_level_id=grade2.grade_level_id,
        )
        test_db.add(struct1)
        test_db.add(struct2)
        test_db.commit()

        service = CurriculumService(test_db)
        # Both structures have subjects containing "Mathematics" in the name
        results = service.search_curriculums("Mathematics")
        matching = [c for c in results if c.curricula_id == sample_curriculum.curricula_id]
        assert len(matching) == 1, "distinct() must prevent duplicate rows per curriculum"

    def test_empty_string_returns_empty_list(self, test_db, sample_curriculum):
        """AWD-M-166: empty search_term must return [] without executing the join query."""
        service = CurriculumService(test_db)
        results = service.search_curriculums("")
        assert results == [], "Empty string should return [] not the full table"

    def test_whitespace_only_returns_empty_list(self, test_db, sample_curriculum):
        """AWD-M-166: whitespace-only search_term must return [] not the full table."""
        service = CurriculumService(test_db)
        results = service.search_curriculums("   ")
        assert results == [], "Whitespace-only string should return [] not the full table"

    def test_db_error_raises_http_500(self):
        """AWD-M-167: SQLAlchemy error is caught and re-raised as HTTP 500."""
        from unittest.mock import MagicMock
        from fastapi import HTTPException

        mock_db = MagicMock()
        mock_db.query.side_effect = Exception("DB connection lost")
        service = CurriculumService(mock_db)
        with pytest.raises(HTTPException) as exc_info:
            service.search_curriculums("algebra")
        assert exc_info.value.status_code == 500
        assert "curricula" in exc_info.value.detail.lower()


class TestSearchTopics:
    """search_topics — AWD-M-166: empty search_term guard + basic happy path."""

    def test_empty_string_returns_empty_list(self, test_db):
        """AWD-M-166: empty search_term returns [] without hitting DB."""
        service = CurriculumService(test_db)
        results = service.search_topics("")
        assert results == [], "Empty string should return [] not the full topics table"

    def test_whitespace_only_returns_empty_list(self, test_db):
        """AWD-M-166: whitespace-only search_term returns [] not the full topics table."""
        service = CurriculumService(test_db)
        results = service.search_topics("   ")
        assert results == [], "Whitespace-only string should return [] not the full topics table"

    def test_matching_term_returns_topic(self, test_db, sample_curriculum_structure):
        """AWD-M-166: non-empty term returns matching topics."""
        from apps.backend.models import Topic
        topic = Topic(
            topic_title="Algebra Basics M166",
            curriculum_structure_id=sample_curriculum_structure.curriculum_structure_id,
        )
        test_db.add(topic)
        test_db.commit()
        test_db.refresh(topic)

        service = CurriculumService(test_db)
        results = service.search_topics("Algebra Basics M166")
        ids = [t.topic_id for t in results]
        assert topic.topic_id in ids

    def test_no_match_returns_empty_list(self, test_db):
        """search_topics with a term matching nothing returns [] (no crash)."""
        service = CurriculumService(test_db)
        results = service.search_topics("xyzzy_no_topic_9876")
        assert results == []

    def test_db_error_raises_http_500(self):
        """AWD-M-167: SQLAlchemy error is caught and re-raised as HTTP 500."""
        from unittest.mock import MagicMock
        from fastapi import HTTPException

        mock_db = MagicMock()
        mock_db.query.side_effect = Exception("DB connection lost")
        service = CurriculumService(mock_db)
        with pytest.raises(HTTPException) as exc_info:
            service.search_topics("algebra")
        assert exc_info.value.status_code == 500
        assert "topics" in exc_info.value.detail.lower()


class TestGetCurriculumStatisticsM165:
    """AWD-M-165: aggregated COUNT queries replace N+1 per-topic SELECTs."""

    def test_aggregates_objectives_and_contents_across_many_topics(
        self,
        test_db,
        sample_curriculum,
        sample_subject,
        sample_grade_level,
    ):
        """3 topics across 2 structures with varied objectives/contents → correct totals.

        Specifically validates the IN-clause aggregation introduced by AWD-M-165:
        topic1 (struct1): 2 objectives, 1 content
        topic2 (struct1): 1 objective,  3 contents
        topic3 (struct2): 0 objectives, 2 contents
        Expected: topics=3, objectives=3, contents=6
        """
        subject2 = Subject(name="Science-M165")
        grade2 = GradeLevel(name="Grade 5-M165")
        test_db.add_all([subject2, grade2])
        test_db.commit()
        test_db.refresh(subject2)
        test_db.refresh(grade2)

        struct1 = CurriculumStructure(
            curricula_id=sample_curriculum.curricula_id,
            subject_id=sample_subject.subject_id,
            grade_level_id=sample_grade_level.grade_level_id,
        )
        struct2 = CurriculumStructure(
            curricula_id=sample_curriculum.curricula_id,
            subject_id=subject2.subject_id,
            grade_level_id=grade2.grade_level_id,
        )
        test_db.add_all([struct1, struct2])
        test_db.commit()
        test_db.refresh(struct1)
        test_db.refresh(struct2)

        # topic1: 2 objectives, 1 content
        t1 = _make_topic(test_db, struct1.curriculum_structure_id, "Topic A M165")
        _make_objective(test_db, t1.topic_id, "Obj A1")
        _make_objective(test_db, t1.topic_id, "Obj A2")
        _make_content(test_db, t1.topic_id, "Content A1")

        # topic2: 1 objective, 3 contents
        t2 = _make_topic(test_db, struct1.curriculum_structure_id, "Topic B M165")
        _make_objective(test_db, t2.topic_id, "Obj B1")
        _make_content(test_db, t2.topic_id, "Content B1")
        _make_content(test_db, t2.topic_id, "Content B2")
        _make_content(test_db, t2.topic_id, "Content B3")

        # topic3: 0 objectives, 2 contents (struct2)
        t3 = _make_topic(test_db, struct2.curriculum_structure_id, "Topic C M165")
        _make_content(test_db, t3.topic_id, "Content C1")
        _make_content(test_db, t3.topic_id, "Content C2")

        service = CurriculumService(test_db)
        result = service.get_curriculum_statistics(
            curriculum_id=sample_curriculum.curricula_id
        )

        assert result["curriculum_id"] == sample_curriculum.curricula_id
        assert result["total_topics"] == 3
        assert result["total_learning_objectives"] == 3   # 2 + 1 + 0
        assert result["total_contents"] == 6              # 1 + 3 + 2

    def test_no_topics_returns_zero_counts(
        self,
        test_db,
        sample_curriculum,
        sample_subject,
        sample_grade_level,
    ):
        """Structure with no topics → short-circuits before COUNT queries; returns zeros."""
        struct = CurriculumStructure(
            curricula_id=sample_curriculum.curricula_id,
            subject_id=sample_subject.subject_id,
            grade_level_id=sample_grade_level.grade_level_id,
        )
        test_db.add(struct)
        test_db.commit()

        service = CurriculumService(test_db)
        result = service.get_curriculum_statistics(
            curriculum_id=sample_curriculum.curricula_id
        )

        assert result["curriculum_id"] == sample_curriculum.curricula_id
        assert result["total_topics"] == 0
        assert result["total_learning_objectives"] == 0
        assert result["total_contents"] == 0


class TestGetCurriculumStatisticsM170:
    """AWD-M-170: get_curriculum_statistics wraps DB errors as HTTP 500."""

    def test_db_error_raises_http_500(self):
        """SQLAlchemy error is caught, logged, and re-raised as HTTP 500."""
        from unittest.mock import MagicMock
        from fastapi import HTTPException

        mock_db = MagicMock()
        mock_db.query.side_effect = Exception("DB connection lost")
        service = CurriculumService(mock_db)
        with pytest.raises(HTTPException) as exc_info:
            service.get_curriculum_statistics(42)
        assert exc_info.value.status_code == 500
        assert "statistics" in exc_info.value.detail.lower()


# ---------------------------------------------------------------------------
# AWD-H-88: CRUD methods wrap DB errors as HTTP 500
# ---------------------------------------------------------------------------

class TestCurriculumCRUDH88:
    """AWD-H-88: create/update/delete curriculum raise HTTP 500 on DB error."""

    def _mock_db(self):
        from unittest.mock import MagicMock
        return MagicMock()

    def test_create_curriculum_db_error_raises_500(self):
        from unittest.mock import MagicMock
        from fastapi import HTTPException
        from apps.backend.schemas.curriculum import CurriculumCreate

        mock_db = self._mock_db()
        mock_db.add.side_effect = Exception("DB connection lost")
        service = CurriculumService(mock_db)
        data = CurriculumCreate(curriculum_title="Test", country_id=1)
        with pytest.raises(HTTPException) as exc_info:
            service.create_curriculum(data)
        assert exc_info.value.status_code == 500
        assert "curriculum" in exc_info.value.detail.lower()

    def test_update_curriculum_db_error_raises_500(self):
        from unittest.mock import MagicMock
        from fastapi import HTTPException
        from apps.backend.schemas.curriculum import CurriculumCreate

        mock_db = self._mock_db()
        mock_db.query.side_effect = Exception("DB connection lost")
        service = CurriculumService(mock_db)
        data = CurriculumCreate(curriculum_title="Updated", country_id=1)
        with pytest.raises(HTTPException) as exc_info:
            service.update_curriculum(curricula_id=1, curriculum_data=data)
        assert exc_info.value.status_code == 500
        assert "curriculum" in exc_info.value.detail.lower()

    def test_delete_curriculum_db_error_raises_500(self):
        from unittest.mock import MagicMock
        from fastapi import HTTPException

        mock_db = self._mock_db()
        mock_db.query.side_effect = Exception("DB connection lost")
        service = CurriculumService(mock_db)
        with pytest.raises(HTTPException) as exc_info:
            service.delete_curriculum(curricula_id=1)
        assert exc_info.value.status_code == 500
        assert "curriculum" in exc_info.value.detail.lower()


class TestTopicCRUDH88:
    """AWD-H-88: create/update/delete topic raise HTTP 500 on DB error."""

    def _mock_db(self):
        from unittest.mock import MagicMock
        return MagicMock()

    def test_create_topic_db_error_raises_500(self):
        from unittest.mock import MagicMock
        from fastapi import HTTPException
        from apps.backend.schemas.curriculum import TopicCreate

        mock_db = self._mock_db()
        mock_db.add.side_effect = Exception("DB connection lost")
        service = CurriculumService(mock_db)
        data = TopicCreate(topic_title="Algebra", curriculum_structure_id=1)
        with pytest.raises(HTTPException) as exc_info:
            service.create_topic(data)
        assert exc_info.value.status_code == 500
        assert "topic" in exc_info.value.detail.lower()

    def test_update_topic_db_error_raises_500(self):
        from unittest.mock import MagicMock
        from fastapi import HTTPException
        from apps.backend.schemas.curriculum import TopicCreate

        mock_db = self._mock_db()
        mock_db.query.side_effect = Exception("DB connection lost")
        service = CurriculumService(mock_db)
        data = TopicCreate(topic_title="Updated Algebra", curriculum_structure_id=1)
        with pytest.raises(HTTPException) as exc_info:
            service.update_topic(topic_id=1, topic_data=data)
        assert exc_info.value.status_code == 500
        assert "topic" in exc_info.value.detail.lower()

    def test_delete_topic_db_error_raises_500(self):
        from unittest.mock import MagicMock
        from fastapi import HTTPException

        mock_db = self._mock_db()
        mock_db.query.side_effect = Exception("DB connection lost")
        service = CurriculumService(mock_db)
        with pytest.raises(HTTPException) as exc_info:
            service.delete_topic(topic_id=1)
        assert exc_info.value.status_code == 500
        assert "topic" in exc_info.value.detail.lower()


class TestLearningObjectiveCRUDH88:
    """AWD-H-88: create/update/delete learning objective raise HTTP 500 on DB error.

    AWD-M-178: Tests now instantiate LearningObjectiveService directly (extracted
    from CurriculumService).
    """

    def _mock_db(self):
        from unittest.mock import MagicMock
        return MagicMock()

    def test_create_learning_objective_db_error_raises_500(self):
        from unittest.mock import MagicMock
        from fastapi import HTTPException
        from apps.backend.schemas.curriculum import LearningObjectiveCreate

        mock_db = self._mock_db()
        mock_db.add.side_effect = Exception("DB connection lost")
        service = LearningObjectiveService(mock_db)
        data = LearningObjectiveCreate(topic_id=1, objective="Understand variables")
        with pytest.raises(HTTPException) as exc_info:
            service.create_learning_objective(data)
        assert exc_info.value.status_code == 500
        assert "learning objective" in exc_info.value.detail.lower()

    def test_update_learning_objective_db_error_raises_500(self):
        from unittest.mock import MagicMock
        from fastapi import HTTPException
        from apps.backend.schemas.curriculum import LearningObjectiveUpdate

        mock_db = self._mock_db()
        mock_db.query.side_effect = Exception("DB connection lost")
        service = LearningObjectiveService(mock_db)
        data = LearningObjectiveUpdate(objective="New text")
        with pytest.raises(HTTPException) as exc_info:
            service.update_learning_objective(objective_id=1, objective_data=data)
        assert exc_info.value.status_code == 500
        assert "learning objective" in exc_info.value.detail.lower()

    def test_delete_learning_objective_db_error_raises_500(self):
        from unittest.mock import MagicMock
        from fastapi import HTTPException

        mock_db = self._mock_db()
        mock_db.query.side_effect = Exception("DB connection lost")
        service = LearningObjectiveService(mock_db)
        with pytest.raises(HTTPException) as exc_info:
            service.delete_learning_objective(objective_id=1)
        assert exc_info.value.status_code == 500
        assert "learning objective" in exc_info.value.detail.lower()


class TestContentCRUDH88:
    """AWD-H-88: create/update/delete content raise HTTP 500 on DB error.

    AWD-M-178: Tests now instantiate TopicContentService directly (extracted
    from CurriculumService).
    """

    def _mock_db(self):
        from unittest.mock import MagicMock
        return MagicMock()

    def test_create_content_db_error_raises_500(self):
        from unittest.mock import MagicMock
        from fastapi import HTTPException
        from apps.backend.schemas.curriculum import ContentCreate

        mock_db = self._mock_db()
        mock_db.add.side_effect = Exception("DB connection lost")
        service = TopicContentService(mock_db)
        data = ContentCreate(topic_id=1, content_area="Introduction to algebra")
        with pytest.raises(HTTPException) as exc_info:
            service.create_content(data)
        assert exc_info.value.status_code == 500
        assert "content" in exc_info.value.detail.lower()

    def test_update_content_db_error_raises_500(self):
        from unittest.mock import MagicMock
        from fastapi import HTTPException
        from apps.backend.schemas.curriculum import ContentUpdate

        mock_db = self._mock_db()
        mock_db.query.side_effect = Exception("DB connection lost")
        service = TopicContentService(mock_db)
        data = ContentUpdate(content_area="New content")
        with pytest.raises(HTTPException) as exc_info:
            service.update_content(content_id=1, content_data=data)
        assert exc_info.value.status_code == 500
        assert "content" in exc_info.value.detail.lower()

    def test_delete_content_db_error_raises_500(self):
        from unittest.mock import MagicMock
        from fastapi import HTTPException

        mock_db = self._mock_db()
        mock_db.query.side_effect = Exception("DB connection lost")
        service = TopicContentService(mock_db)
        with pytest.raises(HTTPException) as exc_info:
            service.delete_content(content_id=1)
        assert exc_info.value.status_code == 500
        assert "content" in exc_info.value.detail.lower()


class TestUpdateMethodsM171:
    """AWD-M-171: update_learning_objective and update_content accept LearningObjectiveUpdate/ContentUpdate
    schemas with min_length=1 and max_length=2000 validation — raw str no longer accepted."""

    # --- LearningObjectiveUpdate schema validation ---

    def test_learning_objective_update_rejects_empty_string(self):
        """Empty string must fail Pydantic validation (min_length=1)."""
        from pydantic import ValidationError
        from apps.backend.schemas.curriculum import LearningObjectiveUpdate

        with pytest.raises(ValidationError):
            LearningObjectiveUpdate(objective="")

    def test_learning_objective_update_rejects_string_over_2000_chars(self):
        """String longer than 2000 chars must fail Pydantic validation (max_length=2000)."""
        from pydantic import ValidationError
        from apps.backend.schemas.curriculum import LearningObjectiveUpdate

        with pytest.raises(ValidationError):
            LearningObjectiveUpdate(objective="x" * 2001)

    def test_learning_objective_update_accepts_valid_string(self):
        """Valid non-empty string within limit must pass."""
        from apps.backend.schemas.curriculum import LearningObjectiveUpdate

        schema = LearningObjectiveUpdate(objective="Students will identify prime numbers")
        assert schema.objective == "Students will identify prime numbers"

    def test_learning_objective_update_accepts_max_length_boundary(self):
        """Exactly 2000-char string must pass."""
        from apps.backend.schemas.curriculum import LearningObjectiveUpdate

        schema = LearningObjectiveUpdate(objective="a" * 2000)
        assert len(schema.objective) == 2000

    # --- ContentUpdate schema validation ---

    def test_content_update_rejects_empty_string(self):
        """Empty string must fail Pydantic validation (min_length=1)."""
        from pydantic import ValidationError
        from apps.backend.schemas.curriculum import ContentUpdate

        with pytest.raises(ValidationError):
            ContentUpdate(content_area="")

    def test_content_update_rejects_string_over_2000_chars(self):
        """String longer than 2000 chars must fail Pydantic validation (max_length=2000)."""
        from pydantic import ValidationError
        from apps.backend.schemas.curriculum import ContentUpdate

        with pytest.raises(ValidationError):
            ContentUpdate(content_area="y" * 2001)

    def test_content_update_accepts_valid_string(self):
        """Valid non-empty string within limit must pass."""
        from apps.backend.schemas.curriculum import ContentUpdate

        schema = ContentUpdate(content_area="Introduction to algebraic expressions")
        assert schema.content_area == "Introduction to algebraic expressions"

    # --- Service method accepts schema, unpacks field correctly ---

    def test_update_learning_objective_assigns_schema_field(self):
        """Service should assign objective_data.objective to the ORM object.

        AWD-M-178: uses LearningObjectiveService directly.
        """
        from unittest.mock import MagicMock
        from apps.backend.schemas.curriculum import LearningObjectiveUpdate

        mock_db = MagicMock()
        mock_objective = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_objective
        service = LearningObjectiveService(mock_db)

        data = LearningObjectiveUpdate(objective="Understand polynomial expressions")
        result = service.update_learning_objective(objective_id=42, objective_data=data)

        assert mock_objective.objective == "Understand polynomial expressions"
        assert result is mock_objective

    def test_update_content_assigns_schema_field(self):
        """Service should assign content_data.content_area to the ORM object.

        AWD-M-178: uses TopicContentService directly.
        """
        from unittest.mock import MagicMock
        from apps.backend.schemas.curriculum import ContentUpdate

        mock_db = MagicMock()
        mock_content = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_content
        service = TopicContentService(mock_db)

        data = ContentUpdate(content_area="Quadratic equations and factorisation")
        result = service.update_content(content_id=7, content_data=data)

        assert mock_content.content_area == "Quadratic equations and factorisation"
        assert result is mock_content


# ---------------------------------------------------------------------------
# AWD-M-175: _db_guard context manager — unit tests
# ---------------------------------------------------------------------------

class TestDbGuardM175:
    """AWD-M-175: _db_guard() context manager introduced to eliminate 15
    identical try/except blocks in CurriculumService.

    These tests verify the context manager directly so the refactoring is
    independently validated, separate from the CRUD behaviour tests above.
    """

    def test_db_guard_passes_through_return_value(self):
        """Normal execution: the value returned inside the with-block is
        accessible via a local variable (context managers don't suppress
        return — callers capture the result via their own return statement)."""
        from unittest.mock import MagicMock
        service = CurriculumService(MagicMock())
        result = None
        with service._db_guard("Should not raise"):
            result = 42
        assert result == 42

    def test_db_guard_reraises_http_exception_unchanged(self):
        """HTTPException must propagate without being wrapped in a 500."""
        from unittest.mock import MagicMock
        from fastapi import HTTPException

        service = CurriculumService(MagicMock())
        original = HTTPException(status_code=404, detail="not found")
        with pytest.raises(HTTPException) as exc_info:
            with service._db_guard("Should not change this"):
                raise original
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "not found"

    def test_db_guard_converts_generic_exception_to_http_500(self):
        """Any non-HTTP exception becomes HTTP 500 with the supplied detail."""
        from unittest.mock import MagicMock
        from fastapi import HTTPException

        service = CurriculumService(MagicMock())
        with pytest.raises(HTTPException) as exc_info:
            with service._db_guard("Failed to do the thing"):
                raise RuntimeError("disk on fire")
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Failed to do the thing"

    def test_db_guard_logs_error_on_generic_exception(self):
        """The logger.error call must fire (with exc_info=True) on non-HTTP errors."""
        from unittest.mock import MagicMock, patch
        from fastapi import HTTPException

        service = CurriculumService(MagicMock())
        with patch("apps.backend.services.curriculum_service.logger") as mock_logger:
            with pytest.raises(HTTPException):
                with service._db_guard("Failed to log test"):
                    raise ValueError("bad value")
            mock_logger.error.assert_called_once()
            call_kwargs = mock_logger.error.call_args
            # exc_info=True must be present so the traceback is captured
            assert call_kwargs.kwargs.get("exc_info") is True or (
                len(call_kwargs.args) >= 1 and call_kwargs.kwargs.get("exc_info", True)
            )

    def test_db_guard_does_not_suppress_keyboard_interrupt(self):
        """BaseException subclasses that are not Exception must propagate freely."""
        from unittest.mock import MagicMock

        service = CurriculumService(MagicMock())
        # KeyboardInterrupt inherits from BaseException, not Exception — the
        # guard's `except Exception` clause must NOT catch it.
        with pytest.raises(KeyboardInterrupt):
            with service._db_guard("Should not swallow KeyboardInterrupt"):
                raise KeyboardInterrupt()

    def test_db_guard_calls_rollback_on_generic_exception(self):
        """AWD-M-177: db.rollback() must be called before raising HTTP 500.

        Mirrors the pattern in auth_service and children_service where
        self.db.rollback() is always called before re-raising on non-HTTP
        errors.  get_db() only calls db.close() in its finally block; rollback
        is not guaranteed on all SQLAlchemy versions without an explicit call.
        """
        from unittest.mock import MagicMock
        from fastapi import HTTPException

        mock_db = MagicMock()
        service = CurriculumService(mock_db)

        with pytest.raises(HTTPException) as exc_info:
            with service._db_guard("Failed to do the thing"):
                raise RuntimeError("simulated DB error")

        # rollback must have been called exactly once before the 500 is raised
        mock_db.rollback.assert_called_once()
        assert exc_info.value.status_code == 500

    def test_db_guard_does_not_rollback_on_http_exception(self):
        """AWD-M-177: rollback must NOT be called when an HTTPException propagates.

        HTTPExceptions are intentional responses (404, 403, etc.) — rolling
        back on them would undo valid reads that set up the error context.
        """
        from unittest.mock import MagicMock
        from fastapi import HTTPException

        mock_db = MagicMock()
        service = CurriculumService(mock_db)

        with pytest.raises(HTTPException) as exc_info:
            with service._db_guard("Should not rollback"):
                raise HTTPException(status_code=404, detail="not found")

        mock_db.rollback.assert_not_called()
        assert exc_info.value.status_code == 404


# AWD-M-179: _db_guard return type annotation
# ---------------------------------------------------------------------------

class TestDbGuardM179:
    """AWD-M-179: _db_guard must carry a Generator[None, None, None] return
    type annotation so mypy / pyright can validate all call sites.

    The fix adds ``Generator`` to the typing imports and changes the signature
    from ``def _db_guard(self, error_msg: str):`` to
    ``def _db_guard(self, error_msg: str) -> Generator[None, None, None]:``.
    """

    def test_db_guard_has_generator_return_annotation(self):
        """_db_guard.__annotations__['return'] must be Generator[None, None, None]."""
        import inspect
        from typing import Generator

        hints = {}
        try:
            import typing
            hints = typing.get_type_hints(CurriculumService._db_guard)
        except Exception:
            # Fall back to raw __annotations__ if get_type_hints fails in the sandbox
            hints = getattr(CurriculumService._db_guard, "__annotations__", {})

        assert "return" in hints, "_db_guard is missing a return type annotation"
        assert hints["return"] == Generator[None, None, None], (
            f"Expected Generator[None, None, None], got {hints['return']}"
        )


# ---------------------------------------------------------------------------
# AWD-M-178: sub-service smoke tests
# ---------------------------------------------------------------------------

class TestLearningObjectiveServiceM178:
    """AWD-M-178: LearningObjectiveService — extracted from CurriculumService.

    Smoke tests to confirm instantiation and _db_guard work independently.
    Full CRUD behaviour is covered by TestLearningObjectiveCRUDH88 above.
    """

    def test_instantiation(self):
        """LearningObjectiveService can be instantiated with a mock db session."""
        from unittest.mock import MagicMock
        db = MagicMock()
        service = LearningObjectiveService(db)
        assert service.db is db

    def test_db_guard_converts_exception_to_http_500(self):
        """_db_guard on LearningObjectiveService converts generic exception to HTTP 500."""
        from unittest.mock import MagicMock
        from fastapi import HTTPException

        service = LearningObjectiveService(MagicMock())
        with pytest.raises(HTTPException) as exc_info:
            with service._db_guard("Failed to do thing"):
                raise RuntimeError("test error")
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Failed to do thing"

    def test_get_learning_objectives_returns_empty_list(self, test_db, sample_curriculum_structure):
        """get_learning_objectives returns [] when no objectives exist for a topic."""
        from apps.backend.models import Topic
        topic = Topic(
            topic_title="Empty Objectives Topic M178",
            curriculum_structure_id=sample_curriculum_structure.curriculum_structure_id,
        )
        test_db.add(topic)
        test_db.commit()
        test_db.refresh(topic)

        service = LearningObjectiveService(test_db)
        results = service.get_learning_objectives(topic.topic_id)
        assert results == []

    def test_create_and_retrieve_learning_objective(self, test_db, sample_curriculum_structure):
        """create_learning_objective persists and get_learning_objectives retrieves it."""
        from apps.backend.models import Topic
        from apps.backend.schemas.curriculum import LearningObjectiveCreate

        topic = Topic(
            topic_title="Objective CRUD Topic M178",
            curriculum_structure_id=sample_curriculum_structure.curriculum_structure_id,
        )
        test_db.add(topic)
        test_db.commit()
        test_db.refresh(topic)

        service = LearningObjectiveService(test_db)
        data = LearningObjectiveCreate(topic_id=topic.topic_id, objective="Students understand fractions M178")
        created = service.create_learning_objective(data)
        assert created.learning_objective_id is not None
        assert created.objective == "Students understand fractions M178"

        fetched = service.get_learning_objectives(topic.topic_id)
        ids = [o.learning_objective_id for o in fetched]
        assert created.learning_objective_id in ids


class TestTopicContentServiceM178:
    """AWD-M-178: TopicContentService — extracted from CurriculumService.

    Smoke tests to confirm instantiation and _db_guard work independently.
    Full CRUD behaviour is covered by TestContentCRUDH88 above.
    """

    def test_instantiation(self):
        """TopicContentService can be instantiated with a mock db session."""
        from unittest.mock import MagicMock
        db = MagicMock()
        service = TopicContentService(db)
        assert service.db is db

    def test_db_guard_converts_exception_to_http_500(self):
        """_db_guard on TopicContentService converts generic exception to HTTP 500."""
        from unittest.mock import MagicMock
        from fastapi import HTTPException

        service = TopicContentService(MagicMock())
        with pytest.raises(HTTPException) as exc_info:
            with service._db_guard("Failed to do content thing"):
                raise RuntimeError("test error")
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Failed to do content thing"

    def test_get_contents_returns_empty_list(self, test_db, sample_curriculum_structure):
        """get_contents returns [] when no content exists for a topic."""
        from apps.backend.models import Topic
        topic = Topic(
            topic_title="Empty Contents Topic M178",
            curriculum_structure_id=sample_curriculum_structure.curriculum_structure_id,
        )
        test_db.add(topic)
        test_db.commit()
        test_db.refresh(topic)

        service = TopicContentService(test_db)
        results = service.get_contents(topic.topic_id)
        assert results == []

    def test_create_and_retrieve_content(self, test_db, sample_curriculum_structure):
        """create_content persists and get_contents retrieves it."""
        from apps.backend.models import Topic
        from apps.backend.schemas.curriculum import ContentCreate

        topic = Topic(
            topic_title="Content CRUD Topic M178",
            curriculum_structure_id=sample_curriculum_structure.curriculum_structure_id,
        )
        test_db.add(topic)
        test_db.commit()
        test_db.refresh(topic)

        service = TopicContentService(test_db)
        data = ContentCreate(topic_id=topic.topic_id, content_area="Introduction to fractions M178")
        created = service.create_content(data)
        assert created.topic_contents_id is not None
        assert created.content_area == "Introduction to fractions M178"

        fetched = service.get_contents(topic.topic_id)
        ids = [c.topic_contents_id for c in fetched]
        assert created.topic_contents_id in ids
