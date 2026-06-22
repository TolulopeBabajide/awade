
"""Tests for structural/contract invariants of the AI injection-pattern constants.

AWD-M-267: split from test_ai_providers.py.
Covers: _SHARED_INJECTION_PATTERNS subset invariants, _PROMPT_DELIMITER_TAGS
coverage vs prompts.py.
"""

from packages.ai.gpt_service import (
    _PROMPT_DELIMITER_TAGS,
    _SHARED_INJECTION_PATTERNS,
    _INPUT_INJECTION_PATTERNS,
    _OUTPUT_INJECTION_PATTERNS,
)


class TestSharedInjectionPatterns:
    """AWD-M-158: _SHARED_INJECTION_PATTERNS must be a strict subset of both
    input and output lists so a single definition keeps both gates in sync."""

    def test_shared_patterns_present_in_input_list(self):
        """Every pattern in _SHARED_INJECTION_PATTERNS appears in _INPUT_INJECTION_PATTERNS."""
        for pattern in _SHARED_INJECTION_PATTERNS:
            assert pattern in _INPUT_INJECTION_PATTERNS, (
                f"Shared pattern missing from _INPUT_INJECTION_PATTERNS: {pattern!r}"
            )

    def test_shared_patterns_present_in_output_list(self):
        """Every pattern in _SHARED_INJECTION_PATTERNS appears in _OUTPUT_INJECTION_PATTERNS."""
        for pattern in _SHARED_INJECTION_PATTERNS:
            assert pattern in _OUTPUT_INJECTION_PATTERNS, (
                f"Shared pattern missing from _OUTPUT_INJECTION_PATTERNS: {pattern!r}"
            )

    def test_shared_patterns_non_empty(self):
        """_SHARED_INJECTION_PATTERNS must contain at least 6 entries (AWD-M-150 variants)."""
        assert len(_SHARED_INJECTION_PATTERNS) >= 6

    def test_input_and_output_cover_all_shared(self):
        """Both lists are strict supersets of _SHARED_INJECTION_PATTERNS — no shared
        pattern may be dropped from either gate without breaking this test."""
        shared_set = set(_SHARED_INJECTION_PATTERNS)
        assert shared_set.issubset(set(_INPUT_INJECTION_PATTERNS))
        assert shared_set.issubset(set(_OUTPUT_INJECTION_PATTERNS))


class TestPromptDelimiterTagsCoverage:
    """AWD-M-264: Every XML-style delimiter tag in prompts.py must be in
    _PROMPT_DELIMITER_TAGS so _sanitize_input strips it before prompt injection.
    Prevents silent bypass when a new delimiter pair is added to prompts.py
    without a matching entry in the stripping tuple."""

    def _tags_used_in_prompts(self) -> set:
        import re
        import pathlib
        prompts_path = (
            pathlib.Path(__file__).parent.parent.parent.parent / "packages" / "ai" / "prompts.py"
        )
        assert prompts_path.exists(), f"prompts.py not found at {prompts_path}"
        # Require at least one underscore so plain HTML tags (<br>, <em>, etc.)
        # in docstrings/comments don't trigger false failures (AWD-M-283).
        return set(re.findall(r"</?[a-z][a-z_]*_[a-z_]+>", prompts_path.read_text()))

    def test_all_prompt_tags_covered_by_delimiter_tuple(self):
        """Every <tag> found in prompts.py must appear in _PROMPT_DELIMITER_TAGS."""
        for tag in self._tags_used_in_prompts():
            assert tag in _PROMPT_DELIMITER_TAGS, (
                f"Tag {tag!r} used in prompts.py but missing from _PROMPT_DELIMITER_TAGS — "
                "add it so _sanitize_input strips it before prompt injection"
            )

    def test_delimiter_tuple_non_empty(self):
        """_PROMPT_DELIMITER_TAGS must contain at least 4 entries (2 pairs minimum)."""
        assert len(_PROMPT_DELIMITER_TAGS) >= 4

    def test_each_opening_tag_has_closing_counterpart(self):
        """Every opening tag in _PROMPT_DELIMITER_TAGS has a matching closing pair."""
        opening_tags = [t for t in _PROMPT_DELIMITER_TAGS if not t.startswith("</")]
        for tag in opening_tags:
            tag_name = tag[1:-1]
            closing = f"</{tag_name}>"
            assert closing in _PROMPT_DELIMITER_TAGS, (
                f"Opening tag {tag!r} in _PROMPT_DELIMITER_TAGS has no closing pair {closing!r}"
            )
