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
from populate_nerdc_curriculum import (
    canon_subject, import_all, _import_theme, _import_topic_children,
)

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


class TestImportTopicChildren:
    def test_inserts_all_pedagogy_rows(self, db, tmp_path):
        """_import_topic_children creates one row per non-empty pedagogy item."""
        _write_nerdc_file(tmp_path, "JSS 1", "Basic Science", [_sample_theme()])
        import_all(db, str(tmp_path))
        topic = db.query(Topic).one()
        stats = {k: 0 for k in ("performance_objectives", "contents", "teachers_activities",
                                 "students_activities", "teaching_learning_materials", "evaluation_guide")}
        topic_data = {
            "performance_objectives": ["obj A"],
            "contents": ["c1", "c2"],
            "teachers_activities": [],
            "students_activities": ["s1"],
            "teaching_learning_materials": ["m1"],
            "evaluation_guide": ["e1", "e2", "e3"],
        }
        _import_topic_children(db, topic, topic_data, stats)
        db.flush()
        assert stats["performance_objectives"] == 1
        assert stats["contents"] == 2
        assert stats["teachers_activities"] == 0
        assert stats["students_activities"] == 1
        assert stats["teaching_learning_materials"] == 1
        assert stats["evaluation_guide"] == 3

    def test_skips_blank_items(self, db, tmp_path):
        """_import_topic_children ignores empty-string and whitespace-only items."""
        _write_nerdc_file(tmp_path, "JSS 1", "Basic Science", [_sample_theme()])
        import_all(db, str(tmp_path))
        topic = db.query(Topic).one()
        stats = {k: 0 for k in ("performance_objectives", "contents", "teachers_activities",
                                 "students_activities", "teaching_learning_materials", "evaluation_guide")}
        _import_topic_children(db, topic, {"performance_objectives": ["", "  ", "real"]}, stats)
        db.flush()
        assert stats["performance_objectives"] == 1


class TestImportTheme:
    def test_creates_theme_and_topics(self, db, tmp_path):
        """_import_theme upserts a theme row and its topic children."""
        from populate_nerdc_curriculum import _get_or_create, CURRICULUM_TITLE, COUNTRY_NAME, COUNTRY_ISO, COUNTRY_REGION
        from models import Country, Curriculum, CurriculumStructure, GradeLevel, Subject
        country, _ = _get_or_create(db, Country, defaults={"iso_code": COUNTRY_ISO, "region": COUNTRY_REGION}, country_name=COUNTRY_NAME)
        curriculum, _ = _get_or_create(db, Curriculum, defaults={"country_id": country.country_id}, curricula_title=CURRICULUM_TITLE)
        grade, _ = _get_or_create(db, GradeLevel, name="JSS 1")
        subject, _ = _get_or_create(db, Subject, name="Basic Science")
        structure, _ = _get_or_create(db, CurriculumStructure,
                                       curricula_id=curriculum.curricula_id,
                                       grade_level_id=grade.grade_level_id,
                                       subject_id=subject.subject_id)
        db.flush()
        stats = {"themes": 0, "topics": 0, "topics_skipped": 0,
                 "performance_objectives": 0, "contents": 0, "teachers_activities": 0,
                 "students_activities": 0, "teaching_learning_materials": 0, "evaluation_guide": 0}
        _import_theme(db, _sample_theme(), structure, stats)
        db.flush()
        assert stats["themes"] == 1
        assert stats["topics"] == 1
        assert db.query(Theme).count() == 1
        assert db.query(Topic).count() == 1

    def test_idempotent_theme_skips_existing_topic(self, db, tmp_path):
        """_import_theme called twice creates the topic only once."""
        from populate_nerdc_curriculum import _get_or_create, CURRICULUM_TITLE, COUNTRY_NAME, COUNTRY_ISO, COUNTRY_REGION
        from models import Country, Curriculum, CurriculumStructure, GradeLevel, Subject
        country, _ = _get_or_create(db, Country, defaults={"iso_code": COUNTRY_ISO, "region": COUNTRY_REGION}, country_name=COUNTRY_NAME)
        curriculum, _ = _get_or_create(db, Curriculum, defaults={"country_id": country.country_id}, curricula_title=CURRICULUM_TITLE)
        grade, _ = _get_or_create(db, GradeLevel, name="JSS 1")
        subject, _ = _get_or_create(db, Subject, name="Basic Science")
        structure, _ = _get_or_create(db, CurriculumStructure,
                                       curricula_id=curriculum.curricula_id,
                                       grade_level_id=grade.grade_level_id,
                                       subject_id=subject.subject_id)
        db.flush()
        stats = {"themes": 0, "topics": 0, "topics_skipped": 0,
                 "performance_objectives": 0, "contents": 0, "teachers_activities": 0,
                 "students_activities": 0, "teaching_learning_materials": 0, "evaluation_guide": 0}
        _import_theme(db, _sample_theme(), structure, stats)
        db.flush()
        _import_theme(db, _sample_theme(), structure, stats)
        db.flush()
        assert db.query(Topic).count() == 1
        assert stats["topics"] == 1
        assert stats["topics_skipped"] == 1

    def test_skips_topics_with_empty_title(self, db, tmp_path):
        """_import_theme ignores topic entries with blank titles."""
        from populate_nerdc_curriculum import _get_or_create, CURRICULUM_TITLE, COUNTRY_NAME, COUNTRY_ISO, COUNTRY_REGION
        from models import Country, Curriculum, CurriculumStructure, GradeLevel, Subject
        country, _ = _get_or_create(db, Country, defaults={"iso_code": COUNTRY_ISO, "region": COUNTRY_REGION}, country_name=COUNTRY_NAME)
        curriculum, _ = _get_or_create(db, Curriculum, defaults={"country_id": country.country_id}, curricula_title=CURRICULUM_TITLE)
        grade, _ = _get_or_create(db, GradeLevel, name="JSS 1")
        subject, _ = _get_or_create(db, Subject, name="Basic Science")
        structure, _ = _get_or_create(db, CurriculumStructure,
                                       curricula_id=curriculum.curricula_id,
                                       grade_level_id=grade.grade_level_id,
                                       subject_id=subject.subject_id)
        db.flush()
        stats = {"themes": 0, "topics": 0, "topics_skipped": 0,
                 "performance_objectives": 0, "contents": 0, "teachers_activities": 0,
                 "students_activities": 0, "teaching_learning_materials": 0, "evaluation_guide": 0}
        theme_data = {"theme_number": 1, "theme": "Empty Topics", "topics": [{"topic": "  ", "performance_objectives": []}]}
        _import_theme(db, theme_data, structure, stats)
        db.flush()
        assert db.query(Topic).count() == 0
        assert stats["topics"] == 0


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
