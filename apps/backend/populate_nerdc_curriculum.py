#!/usr/bin/env python3
"""
Generalized NERDC e-Curriculum importer (JSS 1 - JSS 3, all subjects).

Parses every ``docs/curriculum/NERDC_*.md`` file and idempotently upserts the
full curriculum hierarchy:

    Country -> Curriculum -> CurriculumStructure (grade + subject)
            -> Theme -> Topic
                     -> LearningObjective       (performance_objectives)
                     -> TopicContent            (contents)
                     -> TeacherActivity         (teachers_activities)
                     -> StudentActivity         (students_activities)
                     -> TeachingLearningMaterial (teaching_learning_materials)
                     -> EvaluationGuide         (evaluation_guide)

Unlike ``populate_jss1_math.py`` (hard-coded for one subject) this reads the
JSON block embedded in each markdown file, so it covers all 48 files at once
and captures the four pedagogy collections that the legacy script discarded.

Design notes
------------
* Subject names are *canonicalised* (e.g. "Civic Education (Basic)" ->
  "Civic Education") so the three grades share one ``subjects`` row per subject.
  ``Subject.name`` is unique, so without this the import would create duplicate
  rows or collide.
* Re-running is safe: existing structures/themes/topics are reused. A topic that
  already exists is left untouched (its child rows are not re-created), matching
  the behaviour of ``populate_jss1_math.py``.
* The ``database`` import is deferred into ``main()`` so the module can be
  imported (and unit-tested against an in-memory SQLite session) without a
  configured ``DATABASE_URL``.

Usage:
    python populate_nerdc_curriculum.py
"""

import os
import re
import sys
import json
import glob
from typing import Optional

# Make sibling modules (models, database) importable when run as a script.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import (  # noqa: E402  (path tweak must precede import)
    Country, Curriculum, GradeLevel, Subject, CurriculumStructure,
    Theme, Topic, LearningObjective, TopicContent,
    TeacherActivity, StudentActivity, TeachingLearningMaterial, EvaluationGuide,
)

# Reuses the Curriculum row created by populate_jss1_math.py so the NERDC
# import and the legacy JSS1-Math seed live under the same curriculum.
CURRICULUM_TITLE = "Nigerian Basic Education Curriculum"
COUNTRY_NAME = "Nigeria"
COUNTRY_ISO = "NG"
COUNTRY_REGION = "West Africa"

# Default location of the markdown corpus, relative to the repo root.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_CURRICULUM_DIR = os.path.join(_REPO_ROOT, "docs", "curriculum")

# Maps each NERDC JSON array key to (relationship attr, model, field name).
PEDAGOGY_MAP = [
    ("performance_objectives", "learning_objectives", LearningObjective, "objective"),
    ("contents", "topic_contents", TopicContent, "content_area"),
    ("teachers_activities", "teacher_activities", TeacherActivity, "activity"),
    ("students_activities", "student_activities", StudentActivity, "activity"),
    ("teaching_learning_materials", "teaching_learning_materials", TeachingLearningMaterial, "material"),
    ("evaluation_guide", "evaluation_guides", EvaluationGuide, "guide_item"),
]


# Connector words are lowercased mid-title so that casing variants of the same
# subject collapse to one row (e.g. "Cultural And Creative Arts" vs
# "Cultural and Creative Arts"). Significant words keep their source casing.
_CONNECTOR_WORDS = {"and", "of", "the", "for", "in", "to", "a", "an"}


def canon_subject(name: str) -> str:
    """Canonicalise a subject name for use as the unique ``Subject.name``.

    Drops parenthetical qualifiers, normalises ``&`` to ``and``, lowercases
    mid-title connector words, and collapses whitespace. Examples::

        "Civic Education (Basic)"       -> "Civic Education"
        "Information Technology (IT)"   -> "Information Technology"
        "Physical & Health Education"   -> "Physical and Health Education"
        "Cultural And Creative Arts"    -> "Cultural and Creative Arts"
    """
    name = re.sub(r"\s*\([^)]*\)", "", name)        # strip "(...)" qualifiers
    name = name.replace("&", "and")
    words = name.split()
    out = []
    for i, word in enumerate(words):
        if i > 0 and word.lower() in _CONNECTOR_WORDS:
            out.append(word.lower())
        else:
            out.append(word)
    return " ".join(out).strip()


def parse_curriculum_file(path: str) -> dict:
    """Extract and parse the fenced ```json block from a NERDC markdown file."""
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    match = re.search(r"```json\s*(.*?)```", text, re.S)
    if not match:
        raise ValueError(f"No JSON block found in {os.path.basename(path)}")
    return json.loads(match.group(1))


def _get_or_create(db, model, defaults: Optional[dict] = None, **filters):
    """Fetch a row matching ``filters`` or create it. Returns (instance, created)."""
    instance = db.query(model).filter_by(**filters).first()
    if instance is not None:
        return instance, False
    params = dict(filters)
    if defaults:
        params.update(defaults)
    instance = model(**params)
    db.add(instance)
    db.flush()
    return instance, True


def _import_topic_children(db, topic, topic_data: dict, stats: dict) -> None:
    """Upsert pedagogy child rows (objectives, contents, activities, etc.) for a topic."""
    for json_key, _attr, child_model, field in PEDAGOGY_MAP:
        for item in topic_data.get(json_key, []) or []:
            text = str(item).strip()
            if not text:
                continue
            db.add(child_model(topic_id=topic.topic_id, **{field: text}))
            stats[json_key] += 1


def _import_theme(db, theme_data: dict, structure, stats: dict) -> None:
    """Upsert a theme and all its topics (with pedagogy children) under a structure."""
    theme, created = _get_or_create(
        db, Theme,
        defaults={"theme_title": theme_data.get("theme", "")},
        curriculum_structure_id=structure.curriculum_structure_id,
        theme_number=theme_data.get("theme_number"),
    )
    stats["themes"] += int(created)

    for topic_data in theme_data.get("topics", []):
        title = (topic_data.get("topic") or "").strip()
        if not title:
            continue
        existing = db.query(Topic).filter_by(
            curriculum_structure_id=structure.curriculum_structure_id,
            topic_title=title,
        ).first()
        if existing is not None:
            # Backfill the theme link on a legacy topic that lacked one.
            if existing.theme_id is None:
                existing.theme_id = theme.theme_id
            stats["topics_skipped"] += 1
            continue

        topic = Topic(
            curriculum_structure_id=structure.curriculum_structure_id,
            theme_id=theme.theme_id,
            topic_title=title,
        )
        db.add(topic)
        db.flush()
        stats["topics"] += 1
        _import_topic_children(db, topic, topic_data, stats)


def import_file(db, data: dict, stats: dict) -> None:
    """Idempotently import a single parsed curriculum document."""
    class_level = str(data["class_level"]).strip()
    subject_name = canon_subject(str(data["subject"]))

    country, _ = _get_or_create(
        db, Country,
        defaults={"iso_code": COUNTRY_ISO, "region": COUNTRY_REGION},
        country_name=COUNTRY_NAME,
    )
    curriculum, _ = _get_or_create(
        db, Curriculum,
        defaults={"country_id": country.country_id},
        curriculum_title=CURRICULUM_TITLE,
    )
    grade, created = _get_or_create(db, GradeLevel, name=class_level)
    stats["grade_levels"] += int(created)
    subject, created = _get_or_create(db, Subject, name=subject_name)
    stats["subjects"] += int(created)

    structure, created = _get_or_create(
        db, CurriculumStructure,
        curricula_id=curriculum.curricula_id,
        grade_level_id=grade.grade_level_id,
        subject_id=subject.subject_id,
    )
    stats["structures"] += int(created)

    for theme_data in data.get("themes", []):
        _import_theme(db, theme_data, structure, stats)


def import_all(db, directory: str = DEFAULT_CURRICULUM_DIR) -> dict:
    """Import every ``NERDC_*.md`` file under ``directory``. Returns stats dict.

    The caller owns the transaction: this flushes but does not commit, so tests
    can roll back and the CLI wrapper commits once at the end.
    """
    stats = {
        "files": 0, "grade_levels": 0, "subjects": 0, "structures": 0,
        "themes": 0, "topics": 0, "topics_skipped": 0,
        "performance_objectives": 0, "contents": 0, "teachers_activities": 0,
        "students_activities": 0, "teaching_learning_materials": 0,
        "evaluation_guide": 0,
    }
    paths = sorted(glob.glob(os.path.join(directory, "NERDC_*.md")))
    if not paths:
        raise FileNotFoundError(f"No NERDC_*.md files found in {directory}")
    for path in paths:
        data = parse_curriculum_file(path)
        import_file(db, data, stats)
        stats["files"] += 1
    return stats


def main() -> None:
    from database import SessionLocal  # deferred: requires DATABASE_URL

    db = SessionLocal()
    try:
        print("Importing NERDC curriculum from", DEFAULT_CURRICULUM_DIR)
        stats = import_all(db)
        db.commit()
        print("Import complete:")
        for key, value in stats.items():
            print(f"  {key:28} {value}")
    except Exception as exc:  # pragma: no cover - CLI safety net
        db.rollback()
        print(f"Import failed, rolled back: {exc}", file=sys.stderr)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
