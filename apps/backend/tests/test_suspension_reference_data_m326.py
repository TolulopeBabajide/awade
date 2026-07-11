"""
Regression tests for AWD-M-326.

Verifies that every GET endpoint on the five reference-data routers
(curriculum, country, grade_level, subject, curriculum_structure) uses
get_current_active_user — not the bare get_current_user that skips the
suspension check (OWASP A01).
"""

import inspect
import pytest
from fastapi import Depends

from apps.backend.dependencies import get_current_active_user
import apps.backend.routers.curriculum as curriculum_module
import apps.backend.routers.country as country_module
import apps.backend.routers.grade_level as grade_level_module
import apps.backend.routers.subject as subject_module
import apps.backend.routers.curriculum_structure as cs_module


def _get_module_functions(module):
    return {name: obj for name, obj in inspect.getmembers(module, inspect.isfunction)}


def _depends_on_active_user(fn) -> bool:
    """Return True if fn has a parameter whose default is Depends(get_current_active_user)."""
    sig = inspect.signature(fn)
    for param in sig.parameters.values():
        default = param.default
        if (
            isinstance(default, type(Depends(get_current_active_user)))
            and hasattr(default, "dependency")
            and default.dependency is get_current_active_user
        ):
            return True
    return False


class TestCurriculumRouterSuspensionCheckM326:
    """GET endpoints in curriculum.py must use get_current_active_user."""

    @pytest.mark.parametrize("fn_name", [
        "get_curriculums",
        "get_topics",
        "get_topic",
        "get_learning_objectives",
        "get_contents",
        "get_curriculum",
    ])
    def test_handler_uses_get_current_active_user(self, fn_name):
        fns = _get_module_functions(curriculum_module)
        assert fn_name in fns, f"Expected function {fn_name!r} in curriculum router"
        assert _depends_on_active_user(fns[fn_name]), (
            f"{fn_name} must Depends(get_current_active_user) — "
            "suspended users must be blocked (AWD-M-326)"
        )


class TestCountryRouterSuspensionCheckM326:
    """GET endpoints in country.py must use get_current_active_user."""

    @pytest.mark.parametrize("fn_name", [
        "list_countries",
        "search_countries",
        "get_countries_by_region",
        "get_country",
    ])
    def test_handler_uses_get_current_active_user(self, fn_name):
        fns = _get_module_functions(country_module)
        assert fn_name in fns, f"Expected function {fn_name!r} in country router"
        assert _depends_on_active_user(fns[fn_name]), (
            f"{fn_name} must Depends(get_current_active_user) — "
            "suspended users must be blocked (AWD-M-326)"
        )


class TestGradeLevelRouterSuspensionCheckM326:
    """GET endpoints in grade_level.py must use get_current_active_user."""

    @pytest.mark.parametrize("fn_name", [
        "list_grade_levels",
        "search_grade_levels",
        "get_grade_levels_by_curriculum",
        "get_grade_levels_by_subject",
        "get_grade_level",
    ])
    def test_handler_uses_get_current_active_user(self, fn_name):
        fns = _get_module_functions(grade_level_module)
        assert fn_name in fns, f"Expected function {fn_name!r} in grade_level router"
        assert _depends_on_active_user(fns[fn_name]), (
            f"{fn_name} must Depends(get_current_active_user) — "
            "suspended users must be blocked (AWD-M-326)"
        )


class TestSubjectRouterSuspensionCheckM326:
    """GET endpoints in subject.py must use get_current_active_user."""

    @pytest.mark.parametrize("fn_name", [
        "list_subjects",
        "search_subjects",
        "get_subjects_by_curriculum",
        "get_subject",
    ])
    def test_handler_uses_get_current_active_user(self, fn_name):
        fns = _get_module_functions(subject_module)
        assert fn_name in fns, f"Expected function {fn_name!r} in subject router"
        assert _depends_on_active_user(fns[fn_name]), (
            f"{fn_name} must Depends(get_current_active_user) — "
            "suspended users must be blocked (AWD-M-326)"
        )


class TestCurriculumStructureRouterSuspensionCheckM326:
    """GET endpoints in curriculum_structure.py must use get_current_active_user."""

    @pytest.mark.parametrize("fn_name", [
        "list_curriculum_structures",
        "get_curriculum_structure",
    ])
    def test_handler_uses_get_current_active_user(self, fn_name):
        fns = _get_module_functions(cs_module)
        assert fn_name in fns, f"Expected function {fn_name!r} in curriculum_structure router"
        assert _depends_on_active_user(fns[fn_name]), (
            f"{fn_name} must Depends(get_current_active_user) — "
            "suspended users must be blocked (AWD-M-326)"
        )
