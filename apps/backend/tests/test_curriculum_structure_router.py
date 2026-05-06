"""
Unit tests for ``apps/backend/routers/curriculum_structure.py``.

The fix in AWD-M-63 replaces three sequential ``db.query().first()`` calls in
the FK-validation block of ``create_curriculum_structure`` and
``update_curriculum_structure`` with a single ``UNION ALL`` round-trip via
``_validate_fk_targets``. These tests exercise the helper directly so they do
not need the full authenticated TestClient stack.

Author: Lead Dev Agent (AWD-M-63)
"""

import pytest
from fastapi import HTTPException

from apps.backend.routers.curriculum_structure import _validate_fk_targets


class TestValidateFkTargetsBatch:
    """``_validate_fk_targets`` — single-round-trip FK existence check."""

    def test_all_three_fks_present_does_not_raise(
        self,
        test_db,
        sample_curriculum,
        sample_grade_level,
        sample_subject,
    ):
        """When every FK exists the helper returns silently (no HTTPException)."""
        # Should not raise
        _validate_fk_targets(
            test_db,
            curricula_id=sample_curriculum.curricula_id,
            grade_level_id=sample_grade_level.grade_level_id,
            subject_id=sample_subject.subject_id,
        )

    def test_missing_curriculum_raises_404_curriculum_first(
        self,
        test_db,
        sample_grade_level,
        sample_subject,
    ):
        """Curriculum is checked first; missing curriculum yields 'Curriculum not found'."""
        with pytest.raises(HTTPException) as excinfo:
            _validate_fk_targets(
                test_db,
                curricula_id=999_999,
                grade_level_id=sample_grade_level.grade_level_id,
                subject_id=sample_subject.subject_id,
            )
        assert excinfo.value.status_code == 404
        assert excinfo.value.detail == "Curriculum not found"

    def test_missing_grade_level_raises_404(
        self,
        test_db,
        sample_curriculum,
        sample_subject,
    ):
        """Missing grade level raises a specific 'Grade level not found' 404."""
        with pytest.raises(HTTPException) as excinfo:
            _validate_fk_targets(
                test_db,
                curricula_id=sample_curriculum.curricula_id,
                grade_level_id=999_999,
                subject_id=sample_subject.subject_id,
            )
        assert excinfo.value.status_code == 404
        assert excinfo.value.detail == "Grade level not found"

    def test_missing_subject_raises_404(
        self,
        test_db,
        sample_curriculum,
        sample_grade_level,
    ):
        """Missing subject raises a specific 'Subject not found' 404."""
        with pytest.raises(HTTPException) as excinfo:
            _validate_fk_targets(
                test_db,
                curricula_id=sample_curriculum.curricula_id,
                grade_level_id=sample_grade_level.grade_level_id,
                subject_id=999_999,
            )
        assert excinfo.value.status_code == 404
        assert excinfo.value.detail == "Subject not found"

    def test_all_missing_reports_curriculum_first(self, test_db):
        """When all three are missing the helper still reports curriculum first.

        The check ordering (curriculum → grade_level → subject) matches the
        pre-AWD-M-63 sequential implementation so the public 404 behaviour is
        unchanged.
        """
        with pytest.raises(HTTPException) as excinfo:
            _validate_fk_targets(
                test_db,
                curricula_id=999_999,
                grade_level_id=999_999,
                subject_id=999_999,
            )
        assert excinfo.value.status_code == 404
        assert excinfo.value.detail == "Curriculum not found"

    def test_single_round_trip_uses_union_all(
        self,
        test_db,
        sample_curriculum,
        sample_grade_level,
        sample_subject,
    ):
        """The helper issues a single ``execute()`` call (UNION ALL), not three.

        We instrument ``Session.execute`` and ``Session.query`` and assert the
        helper does not fall back to per-table queries.
        """
        execute_calls = {"count": 0}
        query_calls = {"count": 0}
        real_execute = test_db.execute
        real_query = test_db.query

        def counting_execute(*args, **kwargs):
            execute_calls["count"] += 1
            return real_execute(*args, **kwargs)

        def counting_query(*args, **kwargs):
            query_calls["count"] += 1
            return real_query(*args, **kwargs)

        test_db.execute = counting_execute  # type: ignore[method-assign]
        test_db.query = counting_query  # type: ignore[method-assign]
        try:
            _validate_fk_targets(
                test_db,
                curricula_id=sample_curriculum.curricula_id,
                grade_level_id=sample_grade_level.grade_level_id,
                subject_id=sample_subject.subject_id,
            )
        finally:
            test_db.execute = real_execute  # type: ignore[method-assign]
            test_db.query = real_query  # type: ignore[method-assign]

        assert execute_calls["count"] == 1, (
            f"AWD-M-63 expects 1 UNION ALL execute(); got {execute_calls['count']}"
        )
        assert query_calls["count"] == 0, (
            "AWD-M-63 helper must not fall back to db.query(); "
            f"got {query_calls['count']} db.query() calls"
        )
