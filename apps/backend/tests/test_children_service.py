"""
AWD-M-182: This file has been split into focused test files.

The original 1,309-line file exceeded the 400-line threshold and has been
split following the pattern from AWD-M-116 (test_children_router.py split).

Replacement files:
  - apps/backend/tests/children_service_factories.py  (shared factories)
  - apps/backend/tests/test_children_service_role.py  (TestRoleGating, TestOwnership)
  - apps/backend/tests/test_children_service_crud.py  (TestCreateChildFKValidation,
      TestListChildrenIsolation, TestDeleteChild, TestGetChildTopics,
      TestUpdateChildSubjectValidation)
  - apps/backend/tests/test_children_service_guides.py (TestGenerateGuideIdempotency,
      TestGenerateGuideAIValidation, TestListGuides, TestGetGuide, TestToggleBookmark)
  - apps/backend/tests/test_children_service_db_errors.py (TestChildrenServiceDBErrors)

This file is kept as a stub because the sandbox cannot delete files (AWD-H-78 pattern).
Tolu: run `git rm apps/backend/tests/test_children_service.py` on your dev machine
after CI is green.
"""

import pytest


@pytest.mark.skip(
    reason="AWD-M-182: file split into test_children_service_role/crud/guides/db_errors.py"
)
class TestChildrenServiceStub:
    def test_placeholder(self):
        pass
