"""
AWD-H-135 — rate limit structure tests for lesson_plans.py.

Verifies that the 7 previously unprotected endpoints carry `request: Request`
(required by slowapi) and that the 3 already-limited endpoints are unchanged.
"""

import inspect
import pytest

import apps.backend.routers.lesson_plans as lesson_plans_module


class TestLessonPlanRateLimitStructure:
    """AWD-H-135 — all lesson-plan endpoints must carry request: Request for slowapi."""

    @pytest.mark.parametrize("func_name,expected_limit", [
        # Newly rate-limited (this fix)
        ("get_all_lesson_resources",   "60/minute"),
        ("get_lesson_resource",        "60/minute"),
        ("get_lesson_plans",           "60/minute"),
        ("get_lesson_plan",            "60/minute"),
        ("get_lesson_plan_resources",  "60/minute"),
        ("update_lesson_plan",         "30/minute"),
        ("delete_lesson_plan",         "30/minute"),
        # Pre-existing (regression guard)
        ("generate_lesson_plan",       "5/minute"),
        ("generate_lesson_resource",   "3/minute"),
        ("export_lesson_resource",     "10/minute"),
    ])
    def test_rate_limited_endpoint_has_request_parameter(self, func_name, expected_limit):
        """Each rate-limited endpoint must accept `request: Request` for slowapi."""
        func = getattr(lesson_plans_module, func_name)
        sig = inspect.signature(func)
        assert "request" in sig.parameters, (
            f"{func_name} is missing the `request: Request` parameter required by slowapi "
            f"(@limiter.limit({expected_limit!r}) will silently fail without it)."
        )

    def test_update_lesson_plan_body_param_renamed(self):
        """update_lesson_plan body param must NOT be named `request` (clashes with Request)."""
        sig = inspect.signature(lesson_plans_module.update_lesson_plan)
        assert "request" in sig.parameters, "request: Request must be present"
        from fastapi import Request
        annotation = sig.parameters["request"].annotation
        assert annotation is Request, (
            "The `request` param must be typed as fastapi.Request, "
            "not LessonPlanUpdate — rename the body param to `lesson_plan_data`."
        )
