"""
Tests for _init_sentry() in apps/backend/main.py.

Covers the three safe-no-op branches:
  (a) SENTRY_DSN blank → returns early, no sentry_sdk.init call
  (b) ENVIRONMENT=testing → returns early, no sentry_sdk.init call
  (c) ImportError on sentry_sdk import → logs warning, no crash

And the happy path:
  (d) Valid DSN + non-testing environment → sentry_sdk.init called with correct args

Author: Awade Lead Dev Agent — AWD-M-26
"""

import importlib
import logging
from unittest.mock import MagicMock, patch, call

import pytest


# ---------------------------------------------------------------------------
# Helper: re-execute _init_sentry() in isolation via direct import of main
# ---------------------------------------------------------------------------

def _run_init_sentry(monkeypatch, env_vars: dict) -> None:
    """
    Patch os.getenv to return the given env_vars mapping, then call
    the already-imported _init_sentry function directly from main.
    """
    import apps.backend.main as main_module

    original_getenv = __import__("os").getenv

    def fake_getenv(key, default=""):
        return env_vars.get(key, default)

    monkeypatch.setattr("apps.backend.main.os.getenv", fake_getenv)
    main_module._init_sentry()


# ---------------------------------------------------------------------------
# Branch (a): SENTRY_DSN blank → early return
# ---------------------------------------------------------------------------

class TestSentryInitNoDSN:
    """_init_sentry returns early when SENTRY_DSN is blank or missing."""

    def test_returns_early_when_dsn_empty(self, monkeypatch, caplog):
        """No sentry_sdk.init called when DSN is empty string."""
        with patch("apps.backend.main.os.getenv", side_effect=lambda k, d="": "" if k == "SENTRY_DSN" else d):
            mock_sentry = MagicMock()
            with patch.dict("sys.modules", {"sentry_sdk": mock_sentry}):
                import apps.backend.main as main_module
                with caplog.at_level(logging.INFO, logger="apps.backend.main"):
                    main_module._init_sentry()
                mock_sentry.init.assert_not_called()

    def test_logs_info_when_dsn_missing(self, monkeypatch, caplog):
        """Logs an informational message when DSN is not set."""
        with patch("apps.backend.main.os.getenv", side_effect=lambda k, d="": "" if k == "SENTRY_DSN" else d):
            import apps.backend.main as main_module
            with caplog.at_level(logging.INFO, logger="apps.backend.main"):
                main_module._init_sentry()
            assert any("not set" in r.message or "disabled" in r.message for r in caplog.records)


# ---------------------------------------------------------------------------
# Branch (b): ENVIRONMENT=testing → early return
# ---------------------------------------------------------------------------

class TestSentryInitTestingEnv:
    """_init_sentry returns early when ENVIRONMENT is 'testing'."""

    def test_returns_early_in_testing_env(self, monkeypatch, caplog):
        """No sentry_sdk.init called when ENVIRONMENT=testing, even with a DSN."""
        def fake_getenv(key, default=""):
            return {
                "SENTRY_DSN": "https://fake@sentry.io/123",
                "ENVIRONMENT": "testing",
            }.get(key, default)

        with patch("apps.backend.main.os.getenv", side_effect=fake_getenv):
            mock_sentry = MagicMock()
            with patch.dict("sys.modules", {"sentry_sdk": mock_sentry}):
                import apps.backend.main as main_module
                main_module._init_sentry()
                mock_sentry.init.assert_not_called()

    def test_logs_info_in_testing_env(self, monkeypatch, caplog):
        """Logs an informational message when disabled in testing."""
        def fake_getenv(key, default=""):
            return {
                "SENTRY_DSN": "https://fake@sentry.io/123",
                "ENVIRONMENT": "testing",
            }.get(key, default)

        with patch("apps.backend.main.os.getenv", side_effect=fake_getenv):
            import apps.backend.main as main_module
            with caplog.at_level(logging.INFO, logger="apps.backend.main"):
                main_module._init_sentry()
            assert any(
                "testing" in r.message.lower() or "disabled" in r.message.lower()
                for r in caplog.records
            )


# ---------------------------------------------------------------------------
# Branch (c): ImportError → logs warning, no crash
# ---------------------------------------------------------------------------

class TestSentryInitImportError:
    """_init_sentry handles missing sentry_sdk gracefully."""

    def test_no_crash_on_import_error(self, monkeypatch, caplog):
        """Function returns without raising when sentry_sdk import fails."""
        def fake_getenv(key, default=""):
            return {
                "SENTRY_DSN": "https://fake@sentry.io/123",
                "ENVIRONMENT": "production",
            }.get(key, default)

        import sys

        with patch("apps.backend.main.os.getenv", side_effect=fake_getenv):
            # Remove sentry_sdk from sys.modules so the import inside _init_sentry raises ImportError
            with patch.dict("sys.modules", {"sentry_sdk": None}):
                import apps.backend.main as main_module
                # Should not raise
                main_module._init_sentry()

    def test_logs_warning_on_import_error(self, monkeypatch, caplog):
        """Logs a warning when sentry_sdk is not installed."""
        def fake_getenv(key, default=""):
            return {
                "SENTRY_DSN": "https://fake@sentry.io/123",
                "ENVIRONMENT": "production",
            }.get(key, default)

        with patch("apps.backend.main.os.getenv", side_effect=fake_getenv):
            with patch.dict("sys.modules", {"sentry_sdk": None}):
                import apps.backend.main as main_module
                with caplog.at_level(logging.WARNING, logger="apps.backend.main"):
                    main_module._init_sentry()
                assert any(
                    "not installed" in r.message or "disabled" in r.message
                    for r in caplog.records
                )


# ---------------------------------------------------------------------------
# Branch (d): Happy path — sentry_sdk.init called with correct args
# ---------------------------------------------------------------------------

class TestSentryInitHappyPath:
    """_init_sentry calls sentry_sdk.init with expected arguments on success."""

    def test_sentry_init_called_with_dsn(self, monkeypatch, caplog):
        """sentry_sdk.init is called with the configured DSN."""
        fake_dsn = "https://abc123@o0.ingest.sentry.io/0"

        def fake_getenv(key, default=""):
            return {
                "SENTRY_DSN": fake_dsn,
                "ENVIRONMENT": "production",
                "SENTRY_TRACES_SAMPLE_RATE": "0.1",
            }.get(key, default)

        mock_sentry = MagicMock()
        mock_sentry.integrations = MagicMock()

        with patch("apps.backend.main.os.getenv", side_effect=fake_getenv):
            with patch.dict("sys.modules", {
                "sentry_sdk": mock_sentry,
                "sentry_sdk.integrations.fastapi": MagicMock(),
                "sentry_sdk.integrations.sqlalchemy": MagicMock(),
                "sentry_sdk.integrations.logging": MagicMock(),
            }):
                import apps.backend.main as main_module
                main_module._init_sentry()

        mock_sentry.init.assert_called_once()
        call_kwargs = mock_sentry.init.call_args[1]
        assert call_kwargs["dsn"] == fake_dsn
        assert call_kwargs["environment"] == "production"
        assert call_kwargs["send_default_pii"] is False

    def test_send_default_pii_is_false(self, monkeypatch):
        """send_default_pii is always False (COPPA / GDPR requirement)."""
        fake_dsn = "https://abc123@o0.ingest.sentry.io/0"

        def fake_getenv(key, default=""):
            return {
                "SENTRY_DSN": fake_dsn,
                "ENVIRONMENT": "staging",
                "SENTRY_TRACES_SAMPLE_RATE": "0.1",
            }.get(key, default)

        mock_sentry = MagicMock()

        with patch("apps.backend.main.os.getenv", side_effect=fake_getenv):
            with patch.dict("sys.modules", {
                "sentry_sdk": mock_sentry,
                "sentry_sdk.integrations.fastapi": MagicMock(),
                "sentry_sdk.integrations.sqlalchemy": MagicMock(),
                "sentry_sdk.integrations.logging": MagicMock(),
            }):
                import apps.backend.main as main_module
                main_module._init_sentry()

        call_kwargs = mock_sentry.init.call_args[1]
        assert call_kwargs.get("send_default_pii") is False, (
            "send_default_pii must be False — COPPA/GDPR requirement"
        )

    def test_generic_exception_logged_not_raised(self, monkeypatch, caplog):
        """A generic exception during sentry_sdk.init is caught and logged, not re-raised."""
        fake_dsn = "https://abc123@o0.ingest.sentry.io/0"

        def fake_getenv(key, default=""):
            return {
                "SENTRY_DSN": fake_dsn,
                "ENVIRONMENT": "production",
                "SENTRY_TRACES_SAMPLE_RATE": "0.1",
            }.get(key, default)

        mock_sentry = MagicMock()
        mock_sentry.init.side_effect = RuntimeError("unexpected sentry failure")

        with patch("apps.backend.main.os.getenv", side_effect=fake_getenv):
            with patch.dict("sys.modules", {
                "sentry_sdk": mock_sentry,
                "sentry_sdk.integrations.fastapi": MagicMock(),
                "sentry_sdk.integrations.sqlalchemy": MagicMock(),
                "sentry_sdk.integrations.logging": MagicMock(),
            }):
                import apps.backend.main as main_module
                with caplog.at_level(logging.WARNING, logger="apps.backend.main"):
                    main_module._init_sentry()  # must not raise

        assert any("failed" in r.message.lower() or "initialisation" in r.message.lower()
                   for r in caplog.records)
