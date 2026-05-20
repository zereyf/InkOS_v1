"""
tests/test_workspace_output.py — v2.0
=======================================
CLEAN-1: Claude XML output must be preserved intact, not stripped.
CLEAN-2: JSON audit block must be stripped reliably, including when the
         critique string contains } characters.
"""

from ui.tabs.workspace import extract_clean_output, _strip_audit_json


# ── CLEAN-2: JSON stripping ───────────────────────────────────────────────────

def test_strip_audit_json_basic():
    raw = 'You are a helpful assistant.\n{"score": 90, "critique": "ok"}'
    result = _strip_audit_json(raw)
    assert "score" not in result
    assert "You are a helpful assistant." in result


def test_strip_audit_json_critique_contains_braces():
    """
    The non-greedy regex r'\\{\\s*"score"\\s*:[\\s\\S]*?\\}\\s*$'
    would terminate at the first } inside the critique string.
    The balanced-brace scanner must handle this correctly.
    """
    raw = (
        "You are a senior engineer.\n"
        '{"score": 82, "precision": 33, "alignment": 38, "efficiency": 11, '
        '"critique": "Add edge case handling for {empty} and {null} inputs."}'
    )
    result = _strip_audit_json(raw)
    assert "score" not in result
    assert "You are a senior engineer." in result


def test_strip_audit_json_critique_contains_nested_json():
    raw = (
        "Write a blog post.\n"
        '{"score": 75, "precision": 28, "alignment": 35, "efficiency": 12, '
        '"critique": "Include an example like {\\"key\\": \\"value\\"} for clarity."}'
    )
    result = _strip_audit_json(raw)
    assert "score" not in result
    assert "Write a blog post." in result


def test_strip_audit_json_no_json_returns_unchanged():
    raw = "You are a helpful assistant. Just text, no JSON."
    result = _strip_audit_json(raw)
    assert result == raw


def test_strip_audit_json_multiline_prompt():
    raw = (
        "<role>\nYou are an expert.\n</role>\n"
        "<task>\nWrite something.\n</task>\n"
        '{"score": 88, "precision": 36, "alignment": 40, "efficiency": 12, '
        '"critique": "The prompt is strong."}'
    )
    result = _strip_audit_json(raw)
    assert "score" not in result
    assert "<role>" in result
    assert "<task>" in result


# ── CLEAN-1: Claude XML preservation ─────────────────────────────────────────

def test_extract_clean_output_preserves_claude_xml():
    """
    Claude XML structure must be returned intact — not stripped.
    Previously <role>, <task>, <constraints> content was removed entirely.
    """
    raw = (
        "<role>\n"
        "You are a senior content strategist with 10 years at The New York Times.\n"
        "</role>\n"
        "<task>\n"
        "Write a 200-word blog post with 2 sections.\n"
        "</task>\n"
        "<constraints>\n"
        "Do not use hedging language. Do not fabricate statistics.\n"
        "</constraints>\n"
        "<edge_cases>\n"
        "If topic is technical, provide context for general audience.\n"
        "</edge_cases>\n"
        "<output_format>\n"
        "Exactly 2 sections, 100 words each. H2 only.\n"
        "</output_format>\n"
        "<quality_bar>\n"
        "A content editor at Medium would approve without revision.\n"
        "</quality_bar>\n"
        '{"score": 85, "precision": 35, "alignment": 40, "efficiency": 10, '
        '"critique": "Add tone guidance."}'
    )
    result = extract_clean_output(raw)

    # XML structure must be present
    assert "<role>" in result
    assert "<task>" in result
    assert "<constraints>" in result
    assert "<edge_cases>" in result
    assert "<output_format>" in result
    assert "<quality_bar>" in result

    # Content must be present
    assert "senior content strategist" in result
    assert "200-word blog post" in result
    assert "Do not use hedging language" in result
    assert "Medium" in result

    # JSON must be stripped
    assert "score" not in result
    assert "critique" not in result


def test_extract_clean_output_claude_xml_with_braces_in_critique():
    """
    Regression: critique with {} must not break JSON stripping
    leaving partial JSON in the Claude XML output.
    """
    raw = (
        "<role>You are an expert.</role>\n"
        "<task>Write a report.</task>\n"
        "<constraints>No hedging.</constraints>\n"
        "<edge_cases>Handle {empty} inputs.</edge_cases>\n"
        "<output_format>500 words.</output_format>\n"
        "<quality_bar>Editor approves.</quality_bar>\n"
        '{"score": 80, "precision": 32, "alignment": 38, "efficiency": 10, '
        '"critique": "Add handling for {empty} and {null} cases."}'
    )
    result = extract_clean_output(raw)

    assert "<role>" in result
    assert "score" not in result
    assert "{empty}" not in result.split("<quality_bar>")[-1]


def test_extract_clean_output_strips_json_from_non_claude_output():
    """Non-Claude outputs must also have their JSON audit stripped."""
    raw = (
        "You are a senior marketing specialist at a Series B SaaS company. "
        "Your task is to write compelling ad copy.\n"
        '{"score": 78, "precision": 30, "alignment": 36, "efficiency": 12, '
        '"critique": "Add specific target audience details."}'
    )
    result = extract_clean_output(raw)

    assert "senior marketing specialist" in result
    assert "score" not in result
    assert "critique" not in result


def test_extract_clean_output_removes_part_headers():
    raw = (
        "**PART 1: System Prompt**\n"
        "You are a staff product manager.\n"
        "**PART 2:**\n"
        '{"score": 90, "critique": "ok"}'
    )
    result = extract_clean_output(raw)
    assert "PART 1" not in result
    assert "PART 2" not in result
    assert "staff product manager" in result
    assert "score" not in result


def test_extract_clean_output_empty_input():
    assert extract_clean_output("") == ""
    assert extract_clean_output(None) == ""
