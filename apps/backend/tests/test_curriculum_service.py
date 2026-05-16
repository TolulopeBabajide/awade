"""
Unit tests for CurriculumService — AWD-M-163.

Covers:
- get_curriculum_statistics: happy path (one structure, topics, objectives, contents)
- get_curriculum_statistics: multiple structures aggregated correctly
- get_curriculum_statistics: curriculum not found returns empty dict
- get_curriculum_statistics: curriculum with no structures returns zero counts
- get_curriculum_statistics: curriculum with structures but no topics returns zero counts
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
from apps.backend.models import (
    Curriculum, CurriculumStructure, Topic, LearningObjective, TopicContent, Country
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
    curriculum = Curriculum(curricula_title=title, country_id=country_id)
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
