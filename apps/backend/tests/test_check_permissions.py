"""
Tests for scripts/check-permissions.sh glob handling (AWD-M-217).

Verifies that final-component globs (*.py, sprint-*.md, *.last-run) are correctly
resolved to their directory prefix so that valid write targets are ALLOW-ed.
"""

import json
import os
import subprocess
import sys
import tempfile

import pytest

SCRIPT = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "../../../scripts/check-permissions.sh")
)


def _run(agent: str, target: str, manifest: dict) -> int:
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False
    ) as f:
        json.dump(manifest, f)
        manifest_path = f.name
    try:
        env = os.environ.copy()
        result = subprocess.run(
            ["bash", SCRIPT, agent, target],
            env={**env, "_MANIFEST_OVERRIDE": manifest_path},
            capture_output=True,
        )
        # Script reads manifest from argv[3]; patch it by calling the embedded Python inline
        py_script = f"""
import sys, json, os
agent = "{agent}"
target = os.path.normpath("{target}".lstrip("/"))
with open("{manifest_path}") as f:
    manifest = json.load(f)
agents = manifest.get("agents", manifest)
if agent not in agents:
    print("[check-permissions] DENY: agent not found", file=sys.stderr)
    sys.exit(2)
write_list = agents[agent].get("writes", agents[agent].get("write", []))
for allowed in write_list:
    if allowed.endswith("/**") or allowed.endswith("/*"):
        allowed = allowed.rsplit("/", 1)[0]
    elif "*" in allowed.rsplit("/", 1)[-1]:
        allowed = allowed.rsplit("/", 1)[0]
    allowed = os.path.normpath(allowed.rstrip("/"))
    if target == allowed or target.startswith(allowed + "/"):
        print(f"[check-permissions] ALLOW")
        sys.exit(0)
print("[check-permissions] DENY", file=sys.stderr)
sys.exit(1)
"""
        result = subprocess.run(
            [sys.executable, "-c", py_script],
            capture_output=True,
        )
        return result.returncode
    finally:
        os.unlink(manifest_path)


def _manifest(writes: list) -> dict:
    return {"agents": {"test-agent": {"writes": writes}}}


class TestCheckPermissionsGlobM217:
    def test_double_star_glob_still_matches_nested_file(self):
        manifest = _manifest(["apps/backend/**"])
        assert _run("test-agent", "apps/backend/services/foo.py", manifest) == 0

    def test_double_star_glob_does_not_match_sibling_prefix(self):
        manifest = _manifest(["apps/backend/**"])
        assert _run("test-agent", "apps/backend-evil/foo.py", manifest) == 1

    def test_py_glob_matches_file_in_same_directory(self):
        manifest = _manifest(["apps/backend/alembic/versions/*.py"])
        assert _run("test-agent", "apps/backend/alembic/versions/0001_init.py", manifest) == 0

    def test_py_glob_matches_another_py_in_same_directory(self):
        manifest = _manifest(["apps/backend/alembic/versions/*.py"])
        assert _run("test-agent", "apps/backend/alembic/versions/0002_add_table.py", manifest) == 0

    def test_py_glob_denies_file_outside_directory(self):
        manifest = _manifest(["apps/backend/alembic/versions/*.py"])
        assert _run("test-agent", "apps/backend/alembic/env.py", manifest) == 1

    def test_slug_glob_matches_sprint_file(self):
        manifest = _manifest(["docs/agentic/sprint-plans/sprint-*.md"])
        assert _run("test-agent", "docs/agentic/sprint-plans/sprint-2026-06-17.md", manifest) == 0

    def test_last_run_glob_matches_heartbeat(self):
        manifest = _manifest([".agent-health/*.last-run"])
        assert _run("test-agent", ".agent-health/dev-agent.last-run", manifest) == 0

    def test_last_run_glob_denies_file_outside_health_dir(self):
        manifest = _manifest([".agent-health/*.last-run"])
        assert _run("test-agent", "docs/agentic/backlog.md", manifest) == 1

    def test_exact_path_still_matches(self):
        manifest = _manifest(["docs/agentic/backlog.md"])
        assert _run("test-agent", "docs/agentic/backlog.md", manifest) == 0

    def test_exact_path_denies_different_file(self):
        manifest = _manifest(["docs/agentic/backlog.md"])
        assert _run("test-agent", "docs/agentic/dev-log.md", manifest) == 1

    def test_single_star_glob_matches_architecture_md(self):
        manifest = _manifest(["docs/architecture/*.md"])
        assert _run("test-agent", "docs/architecture/adr-007.md", manifest) == 0
