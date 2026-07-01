"""Tests for create_population_script in export_curriculum_data.py — AWD-M-309."""
import os
import re
import sys
import tempfile
import importlib

import pytest

# Resolve the backend directory so the script module can be imported without a
# live database connection (it only defines functions at module level).
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_DIR)


def _load_export_module():
    """Import export_curriculum_data without executing its __main__ block."""
    spec = importlib.util.spec_from_file_location(
        "export_curriculum_data",
        os.path.join(BACKEND_DIR, "export_curriculum_data.py"),
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestCreatePopulationScriptM309:
    """AWD-M-309: create_population_script reads populate_from_export.py, not inline template."""

    def test_generated_script_contains_populate_function(self, tmp_path, monkeypatch):
        """Output file must contain the populate_from_export function body."""
        mod = _load_export_module()
        monkeypatch.chdir(tmp_path)
        export_data = {"export_timestamp": "2099-01-01T00:00:00.000000"}

        mod.create_population_script(export_data)

        out = (tmp_path / "populate_from_export.py").read_text()
        assert "def populate_from_export" in out

    def test_generated_script_has_updated_timestamp(self, tmp_path, monkeypatch):
        """Generated: line in the docstring must carry the export_timestamp."""
        mod = _load_export_module()
        monkeypatch.chdir(tmp_path)
        ts = "2099-06-15T12:34:56.789000"
        export_data = {"export_timestamp": ts}

        mod.create_population_script(export_data)

        out = (tmp_path / "populate_from_export.py").read_text()
        assert f"Generated: {ts}" in out

    def test_no_inline_template_string_in_source(self):
        """export_curriculum_data.py must not contain the old inline function template."""
        src = open(os.path.join(BACKEND_DIR, "export_curriculum_data.py")).read()
        # The old template contained this exact escaped brace pattern inside an f-string
        assert "country_map = {{}}" not in src, (
            "Old inline template still present — duplication not resolved (AWD-M-309)"
        )
