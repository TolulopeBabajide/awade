"""
Tests for AWD-GRC-09: Admin audit log actor_id nullable with SET NULL on user deletion.

Covers:
- AdminAuditLog can be created with actor_id=None (nullable column)
- AdminAuditLog.actor_id accepts a valid integer (existing behaviour preserved)
- log_admin_action helper still works with a real actor_id
- Audit log row persists after its actor user is deleted (SET NULL semantics)
  verified at ORM level using SQLite in-process DB
"""

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from apps.backend.models import Base, AdminAuditLog, User, UserRole
from apps.backend.utils.admin_logs import log_admin_action


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_engine():
    """In-process SQLite engine — no filesystem required.

    Registers a per-engine ``connect`` listener that runs ``PRAGMA foreign_keys=ON``
    so SQLite enforces the FK constraints declared in models.py — without it,
    the GRC-09 ``ondelete='SET NULL'`` clause on ``admin_audit_logs.actor_id``
    would not actually fire when the parent ``User`` row is deleted, and the
    compliance guarantee would be unverified at the test layer (AWD-L-08).
    """
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})

    @event.listens_for(engine, "connect")
    def _enable_sqlite_fks(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=engine)
    return engine


def _session(engine):
    Session = sessionmaker(bind=engine)
    return Session()


def _make_user(db, email="admin@example.com", role=UserRole.ADMIN):
    user = User(
        email=email,
        password_hash="hashed",
        full_name="Admin User",
        role=role,
        is_suspended=0,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestAuditLogActorIdNullable:
    """actor_id column accepts NULL after GRC-09 migration."""

    def test_audit_log_can_be_created_with_null_actor(self):
        """ORM should accept actor_id=None (nullable column change in GRC-09)."""
        engine = _make_engine()
        db = _session(engine)
        try:
            log = AdminAuditLog(
                actor_id=None,
                action="system_action",
                target_type="user",
                target_id=42,
                ip_address="127.0.0.1",
            )
            db.add(log)
            db.commit()
            db.refresh(log)

            assert log.log_id is not None
            assert log.actor_id is None
            assert log.action == "system_action"
        finally:
            db.close()

    def test_audit_log_actor_id_still_accepts_integer(self):
        """Existing integer actor_id path must still work after the nullable change."""
        engine = _make_engine()
        db = _session(engine)
        try:
            user = _make_user(db)
            log = AdminAuditLog(
                actor_id=user.user_id,
                action="suspend_user",
                target_type="user",
                target_id=99,
                ip_address="10.0.0.1",
            )
            db.add(log)
            db.commit()
            db.refresh(log)

            assert log.actor_id == user.user_id
        finally:
            db.close()

    def test_audit_log_persists_after_actor_user_deleted(self):
        """
        When the admin user who created an audit log is deleted, the log row
        must remain with actor_id SET NULL (GDPR / NDPR / POPIA audit trail
        preservation requirement in GRC-09).
        """
        engine = _make_engine()
        db = _session(engine)
        try:
            user = _make_user(db, email="deleteme@example.com")
            uid = user.user_id

            log = AdminAuditLog(
                actor_id=uid,
                action="change_role",
                target_type="user",
                target_id=7,
                ip_address="192.168.1.1",
            )
            db.add(log)
            db.commit()
            log_id = log.log_id

            # Delete the admin user — FK is SET NULL, so the audit log should survive
            db.delete(user)
            db.commit()

            surviving_log = db.query(AdminAuditLog).filter_by(log_id=log_id).first()
            assert surviving_log is not None, "Audit log row must not be deleted when actor is removed"
            # _make_engine enables PRAGMA foreign_keys=ON, so SQLite executes the
            # FK ``ondelete='SET NULL'`` action declared on ``admin_audit_logs.actor_id``
            # when the parent ``User`` row is deleted. This is the GRC-09 compliance
            # guarantee — the audit trail row persists with actor_id=NULL.
            assert surviving_log.actor_id is None, (
                "actor_id must be NULL after parent user deletion (GRC-09 SET NULL semantics)"
            )
            assert surviving_log.action == "change_role"
            assert surviving_log.target_id == 7
        finally:
            db.close()


class TestLogAdminActionHelper:
    """log_admin_action helper continues to work correctly."""

    def test_log_admin_action_creates_entry(self):
        """Helper must commit an AdminAuditLog row with the correct fields."""
        engine = _make_engine()
        db = _session(engine)
        try:
            user = _make_user(db)

            log_admin_action(
                db=db,
                actor_id=user.user_id,
                action="update_curriculum",
                target_type="curriculum",
                target_id=5,
                metadata={"old_name": "Math", "new_name": "Mathematics"},
                request=None,
            )

            entry = db.query(AdminAuditLog).filter_by(actor_id=user.user_id).first()
            assert entry is not None
            assert entry.action == "update_curriculum"
            assert entry.target_type == "curriculum"
            assert entry.target_id == 5
            assert entry.ip_address is None  # request=None → no IP
            assert '"old_name": "Math"' in entry.metadata_json
        finally:
            db.close()
