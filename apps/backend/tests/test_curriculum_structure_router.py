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
from sqlalchemy import event as sa_event

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
        """The helper issues a single SQL UNION ALL statement, not three.

        Uses ``before_cursor_execute`` engine events to count actual SQL
        statements sent to the DB driver — correctly ignoring session-level
        housekeeping (autobegin, SAVEPOINT, PRAGMA) that inflated the count
        when patching ``Session.execute`` directly (AWD-M-229).
        """
        engine = test_db.get_bind()
        statements: list[str] = []

        def _record(conn, cursor, statement, parameters, context, executemany):
            statements.append(statement)

        sa_event.listen(engine, "before_cursor_execute", _record)
        try:
            _validate_fk_targets(
                test_db,
                curricula_id=sample_curriculum.curricula_id,
                grade_level_id=sample_grade_level.grade_level_id,
                subject_id=sample_subject.subject_id,
            )
        finally:
            sa_event.remove(engine, "before_cursor_execute", _record)

        # Exclude transaction-management statements from the count.
        _TXN_PREFIXES = ("BEGIN", "SAVEPOINT", "RELEASE", "ROLLBACK", "PRAGMA", "COMMIT")
        data_stmts = [
            s for s in statements
            if not s.strip().upper().startswith(_TXN_PREFIXES)
        ]
        assert len(data_stmts) == 1, (
            f"AWD-M-63 expects 1 UNION ALL execute(); got {len(data_stmts)}: {data_stmts}"
        )
        assert "UNION ALL" in data_stmts[0].upper(), (
            f"AWD-M-63 expects a UNION ALL query; got: {data_stmts[0]}"
        )
