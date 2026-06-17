"""
Tests for LessonResourceService.generate_lesson_resource — AWD-M-259 split.

Split from test_lesson_resource_service.py (575 lines) into focused modules.
Covers:
- generate_lesson_resource (403 wrong user, SUPER_ADMIN bypass)
- DB query count assertion (AWD-H-94: exactly 3 queries — LessonPlan, Topic, Context)
- 404 when lesson plan not found
"""

import asyncio
import pytest
import sys
import os
from unittest.mock import MagicMock
from fastapi import HTTPException

# --------------------------------------------------------------------------
# Path fixups for sandbox + CI
# --------------------------------------------------------------------------
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
root_dir = os.path.abspath(os.path.join(backend_dir, "../.."))
sys.path.insert(0, root_dir)
sys.path.insert(0, backend_dir)

# Sandbox compat shim: datetime.UTC added in Python 3.11
import datetime as _dt
if not hasattr(_dt, "UTC"):
    _dt.UTC = _dt.timezone.utc

from apps.backend.schemas.lesson_plans import LessonResourceCreate
from apps.backend.services.lesson_resource_service import LessonResourceService
from lesson_resource_factories import (
    _educator, _super_admin,
    _make_lesson_plan,
)

# ==========================================================================
# TestGenerateLessonResource
# ==========================================================================

class TestGenerateLessonResource:
    """generate_lesson_resource — 403 wrong user, SUPER_ADMIN bypass."""

    def _db_for_generate(self, plan_obj) -> MagicMock:
        """DB mock that drives the full generate_lesson_resource query sequence.

        Query order inside generate_lesson_resource (AWD-H-94: dead CS/Subject/GradeLevel
        queries removed — sequence is now 3 queries instead of 6):
          1. LessonPlan  .filter().first()
          2. Topic       .filter().first()
          3. Context     .filter().all()
        Then: db.add / db.commit / db.refresh
        """
        db = MagicMock()
        call_count = [0]

        topic = MagicMock()
        topic.topic_id = 1
        topic.learning_objectives = []
        topic.topic_contents = []

        def query_side(_model):
            q = MagicMock()
            call_count[0] += 1
            query_num = call_count[0]
            if query_num == 1:
                q.filter.return_value.first.return_value = plan_obj
            elif query_num == 2:
                q.filter.return_value.first.return_value = topic
            else:
                q.filter.return_value.all.return_value = []
            return q

        db.query.side_effect = query_side

        def _refresh(obj):
            obj.lesson_resources_id = 99

        db.refresh.side_effect = _refresh
        return db

    def test_wrong_user_raises_403(self):
        user = _educator(user_id=2)
        lp = _make_lesson_plan(plan_id=1, user_id=1)  # owned by user 1
        lp.topic_id = 1
        db = self._db_for_generate(lp)
        svc = LessonResourceService(db=db)
        data = LessonResourceCreate(lesson_plan_id=1)
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(svc.generate_lesson_resource(lesson_id=1, data=data, current_user=user))
        assert exc_info.value.status_code == 403

    def test_super_admin_can_generate_resource(self):
        """AWD-H-62: SUPER_ADMIN must bypass ownership check in generate_lesson_resource."""
        super_admin = _super_admin(user_id=100)
        lp = _make_lesson_plan(plan_id=1, user_id=1)  # owned by user 1, not super_admin
        lp.topic_id = 1
        db = self._db_for_generate(lp)
        svc = LessonResourceService(db=db)
        data = LessonResourceCreate(lesson_plan_id=1)
        result = asyncio.run(
            svc.generate_lesson_resource(lesson_id=1, data=data, current_user=super_admin)
        )
        assert result.status == "processing"

    def test_only_three_db_queries_made(self):
        """AWD-H-94: generate_lesson_resource must make exactly 3 DB queries.

        Before the fix, 6 queries were issued (LessonPlan, Topic, CurriculumStructure,
        Subject, GradeLevel, Context). The CS/Subject/GradeLevel results were fetched
        but never used — only resource_id flows to the Redis worker. This test
        asserts the dead queries are gone.
        """
        super_admin = _super_admin(user_id=100)
        lp = _make_lesson_plan(plan_id=1, user_id=1)
        lp.topic_id = 1
        db = self._db_for_generate(lp)
        svc = LessonResourceService(db=db)
        data = LessonResourceCreate(lesson_plan_id=1)
        asyncio.run(
            svc.generate_lesson_resource(lesson_id=1, data=data, current_user=super_admin)
        )
        assert db.query.call_count == 3, (
            f"Expected 3 DB queries (LessonPlan, Topic, Context) but got "
            f"{db.query.call_count}. Stale CurriculumStructure/Subject/GradeLevel "
            f"queries may have been re-introduced."
        )

    def test_lesson_plan_not_found_raises_404(self):
        """AWD-H-94: 404 raised when lesson plan does not exist."""
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None
        svc = LessonResourceService(db=db)
        data = LessonResourceCreate(lesson_plan_id=99)
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(
                svc.generate_lesson_resource(lesson_id=99, data=data, current_user=_educator(user_id=1))
            )
        assert exc_info.value.status_code == 404
        assert "Lesson plan not found" in exc_info.value.detail
