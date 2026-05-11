from ui.tabs.workspace import extract_clean_output


def test_extract_clean_output_removes_internal_sections():
    raw = """**PART 1: System Prompt**\nYou are a highly advanced Analytical Assistant\n**PART 2:**\n# Output\n<quality-bar>90</quality-bar>\n<constraints>x</constraints>\nSystem Prompt: REFINED_PROMPT: You are a staff product manager. Build a launch checklist.\n{"score": 90, "critique": "ok"}
"""
    cleaned = extract_clean_output(raw)
    assert "PART 1" not in cleaned
    assert "System Prompt" not in cleaned
    assert "<" not in cleaned
    assert cleaned == "You are a staff product manager. Build a launch checklist."
