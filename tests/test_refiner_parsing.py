from engine.refiner import _extract_json, _parse_output, _validate_structure


def test_extract_json_ignores_braces_inside_strings():
    raw = 'PROMPT: keep this prompt. {"score": 91, "critique": "uses {literal} braces", "precision": 41}'

    extracted = _extract_json(raw)
    refined, audit = _parse_output(raw)

    assert extracted == '{"score": 91, "critique": "uses {literal} braces", "precision": 41}'
    assert refined == "keep this prompt."
    assert audit["score"] == 91
    assert audit["precision"] == 40


def test_extract_json_prefers_appended_audit_block():
    raw = (
        'Prompt includes an example {"score": 10, "critique": "example"} before the final audit. '
        '{"score": 88, "critique": "final", "alignment": 39}'
    )

    refined, audit = _parse_output(raw)

    assert 'example' in refined
    assert audit["score"] == 88
    assert audit["alignment"] == 39


def test_parse_output_reports_missing_audit_contract():
    refined, audit = _parse_output("You are a helpful production prompt.")

    assert refined == "You are a helpful production prompt."
    assert audit["score"] == 0
    assert "failed to append" in audit["critique"]


def test_validate_structure_handles_missing_target_and_claude_xml():
    assert _validate_structure("x" * 120, None) == (True, "")
    passed, reason = _validate_structure("x" * 120, "Claude")

    assert not passed
    assert "XML" in reason
