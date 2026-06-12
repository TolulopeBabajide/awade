"""
Tests for the generalized NERDC curriculum importer (populate_nerdc_curriculum.py)
and the themes/pedagogy schema added for full-curriculum capture.

Covers:
- subject-name canonicalization (dedupes the casing/qualifier variants present
  in the real corpus)
- full hierarchy creation including Theme and the four pedagogy child tables
- idempotency (re-running the import creates no duplicate rows)
- integration sweep over the real docs/curriculum corpus when present
"""

import json
import os
import textwrap

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import (
    Base, Subject, GradeLevel, CurriculumStructure, Theme, Topic,
    LearningObjective, TopicContent, TeacherActivity, StudentActivity,
    TeachingLearningMaterial, EvaluationGuide,
)
from populate_nerdc_curriculum import canon_subject, import_all

REAL_CORPUS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
    "docs", "curriculum",
)


@pytest.fixture()
def db(tmp_path):
    """Isolated SQLite session with the full schema created."""
    engine = create_engine(f"sqlite:///{tmp_path / 'importer.db'}")
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


def _write_nerdc_file(directory, grade, subject, themes):
    """Write a minimal-but-valid NERDC markdown file with embedded JSON."""
    data = {"class_level": grade, "subject": subject, "themes": themes}
    n_topics = sum(len(t["topics"]) for t in themes)
    body = textwrap.dedent(f"""\
        # NERDC e-Curriculum Extract

        **Class Level:** {grade}
        **Subject:** {subject}
        **Source:** NERDC e-Curriculum Portal (nerdc.org.ng)
        **Themes:** {len(themes)} | **Topics:** {n_topics}

        ---

        ```json
        {json.dumps(data, indent=2)}
        ```
        """)
    slug = subject.replace(" ", "_").replace("&", "and")
    path = directory / f"NERDC_{grade.replace(' ', '')}_{slug}.md"
    path.write_text(body, encoding="utf-8")
    return path


def _sample_theme():
    return {
        "theme_number": 1,
        "theme": "Test Theme 01",
        "topics": [
            {
                "topic": "Test Topic 01",
                "performance_objectives": ["objective one", "objective two"],
                "contents": ["content area one"],
                "teachers_activities": ["teacher does a thing"],
                "students_activities": ["student does a thing", "student does another"],
                "teaching_learning_materials": ["chart", "counters"],
                "evaluation_guide": ["ask the student to explain"],
            }
        ],
    }


class TestCanonSubject:
    @pytest.mark.parametrize("raw,expected", [
        ("Civic Education (Basic)", "Civic Education"),
        ("Information Technology (IT)", "Information Technology"),
        ("Physical & Health Education", "Physical and Health Education"),
        ("Cultural And Creative Arts", "Cultural and Creative Arts"),
        ("General Mathematics", "General Mathematics"),
        ("  English   Language ", "English Language"),
    ])
    def test_variants_collapse_to_canonical(self, raw, expected):
        assert canon_subject(raw) == expected


class TestImportHierarchy:
    def test_creates_full_hierarchy(self, db, tmp_path):
        _write_nerdc_file(tmp_path, "JSS 1", "Basic Science", [_sample_theme()])

        stats = import_all(db, str(tmp_path))

        assert stats["files"] == 1
        assert db.query(GradeLevel).filter_by(name="JSS 1").count() == 1
        assert db.query(Subject).filter_by(name="Basic Science").count() == 1
        assert db.query(CurriculumStructure).count() == 1

        theme = db.query(Theme).one()
        assert theme.theme_number == 1
        assert theme.theme_title == "Test Theme 01"

        topic = db.query(Topic).one()
        assert topic.topic_title == "Test Topic 01"
        assert topic.theme_id == theme.theme_id

        assert db.query(LearningObjective).count() == 2
        assert db.query(TopicContent).count() == 1
        assert db.query(TeacherActivity).count() == 1
        assert db.query(StudentActivity).count() == 2
        assert db.query(TeachingLearningMaterial).count() == 2
        assert db.query(EvaluationGuide).count() == 1

        # Relationship round-trip (used by children_service payload builder)
        assert [a.activity for a in topic.student_activities] == [
            "student does a thing", "student does another",
        ]
        assert [m.material for m in topic.teaching_learning_materials] == ["chart", "counters"]
        assert [e.guide_item for e in topic.evaluation_guides] == ["ask the student to explain"]

    def test_empty_pedagogy_arrays_create_no_rows(self, db, tmp_path):
        theme = _sample_theme()
        theme["topics"][0]["teaching_learning_materials"] = []
        theme["topics"][0]["evaluation_guide"] = []
        _write_nerdc_file(tmp_path, "JSS 2", "Basic Science", [theme])

        import_all(db, str(tmp_path))

        assert db.query(TeachingLearningMaterial).count() == 0
        assert db.query(EvaluationGuide).count() == 0
        assert db.query(Topic).count() == 1  # topic itself still imported

    def test_subject_variants_share_one_row(self, db, tmp_path):
        _write_nerdc_file(tmp_path, "JSS 1", "Cultural and Creative Arts", [_sample_theme()])
        _write_nerdc_file(tmp_path, "JSS 2", "Cultural And Creative Arts", [_sample_theme()])

        import_all(db, str(tmp_path))

        subjects = db.query(Subject).all()
        assert len(subjects) == 1
        assert subjects[0].name == "Cultural and Creative Arts"
        # but two structures (one per grade) hang off the single subject
        assert db.query(CurriculumStructure).count() == 2

    def test_import_is_idempotent(self, db, tmp_path):
        _write_nerdc_file(tmp_path, "JSS 1", "Basic Science", [_sample_theme()])

        first = import_all(db, str(tmp_path))
        second = import_all(db, str(tmp_path))

        assert first["topics"] == 1
        assert second["topics"] == 0
        assert second["topics_skipped"] == 1
        assert db.query(Topic).count() == 1
        assert db.query(LearningObjective).count() == 2  # children not duplicated
        assert db.query(Theme).count() == 1

    def test_missing_directory_raises(self, db, tmp_path):
        with pytest.raises(FileNotFoundError):
            import_all(db, str(tmp_path / "nope"))


@pytest.mark.integration
@pytest.mark.skipif(
    not os.path.isdir(REAL_CORPUS_DIR) or not os.listdir(REAL_CORPUS_DIR),
    reason="docs/curriculum corpus not present",
)
class TestRealCorpus:
    def test_full_corpus_imports(self, db):
        stats = import_all(db, REAL_CORPUS_DIR)

        assert stats["files"] == 48
        assert db.query(GradeLevel).count() == 3
        # 15 subjects shared across grades + French (JSS1) + Hausa (JSS2/3)
        assert db.query(Subject).count() == 17
        assert db.query(CurriculumStructure).count() == 48
        assert db.query(Theme).count() == 156
        assert db.query(Topic).count() == 543
        assert db.query(LearningObjective).count() == 1980
        assert db.query(TopicContent).count() == 1744
        assert db.query(TeacherActivity).count() == 2170
        assert db.query(StudentActivity).count() == 2013
        assert db.query(TeachingLearningMaterial).count() == 1876
        assert db.query(EvaluationGuide).count() == 1998

        # every topic belongs to a theme
        assert db.query(Topic).filter(Topic.theme_id.is_(None)).count() == 0
