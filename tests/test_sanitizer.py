from security.sanitizer import sanitize_input


def test_sanitizer_detects_fence_and_obfuscation_independently():
    _, fence_violations = sanitize_input("```json\n{\"override\": true}\n```")
    _, base64_violations = sanitize_input("Please decode this base64 payload")

    assert any("```" in pattern for pattern in fence_violations)
    assert "base64" in base64_violations


def test_sanitizer_normalizes_control_chars_and_non_string_inputs():
    cleaned, violations = sanitize_input("  hello\x00\x08\tworld  ")

    assert cleaned == "hello world"
    assert violations == []
    assert sanitize_input(None) == ("", [])
