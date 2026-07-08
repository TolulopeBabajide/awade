"""
AWD-M-323 regression: pdf_service.py must never call HTML() or CSS() with
presentational_hints=True.

WeasyPrint GHSA-jhhc-3hcp-qhm5 / CVE-2026-49452 allows CSS injection via
the HTML `background` attribute when presentational_hints=True is set.  The
call path resolves to url()-based outbound requests, enabling SSRF against
cloud metadata endpoints (e.g. 169.254.169.254).  WeasyPrint defaults the
kwarg to False, so the safe posture is simply never to pass it.

These tests run as pure static analysis against the module source — no live
WeasyPrint install required.
"""
import ast
from pathlib import Path

import pytest

import apps.backend.services.pdf_service as pdf_module


class TestWeasyPrintNoPresentationalHints:
    """HTML() and CSS() in pdf_service.py must never receive presentational_hints."""

    def _source(self) -> str:
        return Path(pdf_module.__file__).read_text(encoding="utf-8")

    def test_presentational_hints_absent_from_source(self):
        """The string 'presentational_hints' must not appear anywhere in pdf_service.py."""
        source = self._source()
        assert "presentational_hints" not in source, (
            "pdf_service.py contains 'presentational_hints' — ensure it is never "
            "set to True; passing it enables SSRF via CSS url() injection "
            "(GHSA-jhhc-3hcp-qhm5 / CVE-2026-49452)."
        )

    def test_html_and_css_calls_have_no_presentational_hints_kwarg(self):
        """AST walk: no HTML() or CSS() call site passes presentational_hints."""
        source = self._source()
        tree = ast.parse(source)

        violations: list[str] = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func_name: str | None = None
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                func_name = node.func.attr
            if func_name not in ("HTML", "CSS"):
                continue
            for kw in node.keywords:
                if kw.arg == "presentational_hints":
                    violations.append(
                        f"Line {node.lineno}: {func_name}(..., presentational_hints=...)"
                    )

        assert not violations, (
            "pdf_service.py passes presentational_hints to HTML() or CSS() — "
            "this enables SSRF via CSS background url() (CVE-2026-49452). "
            f"Violations found: {violations}"
        )

    def test_html_and_css_still_called(self):
        """Guard: HTML() and CSS() must remain present so the above tests are not vacuous."""
        source = self._source()
        assert "HTML(" in source, (
            "HTML() call not found in pdf_service.py — update AWD-M-323 tests if WeasyPrint "
            "usage was intentionally removed."
        )
        assert "CSS(" in source, (
            "CSS() call not found in pdf_service.py — update AWD-M-323 tests if WeasyPrint "
            "usage was intentionally removed."
        )
