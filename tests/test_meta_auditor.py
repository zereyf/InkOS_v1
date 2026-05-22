import json
import pytest
from unittest.mock import patch, MagicMock
from engine.meta_auditor import run_meta_audit, format_insight_for_display

@pytest.fixture
def mock_openai_client():
    with patch("engine.meta_auditor.client") as mock_client:
        yield mock_client

def test_ceiling_quality_bypass(mock_openai_client):
    """Ensure scores >= 95 skip the API call and return the default ceiling insight."""
    result = run_meta_audit(
        intent="Draw a cyberpunk city",
        target="Midjourney",
        refined=":: cyberpunk city :: hyper realistic --v 6.0",
        score=96,
        critique="Perfect formatting."
    )
    
    # Verify API was NOT called
    mock_openai_client.chat.completions.create.assert_not_called()
    
    # Verify exact static payload
    assert result is not None
    assert result["score"] == 96
    assert result["pattern_tag"] == "CEILING_QUALITY"
    assert result["weakness"] == "None detected at this score level."

def test_successful_meta_audit(mock_openai_client):
    """Ensure a standard API response parses correctly and merges the score."""
    mock_response = MagicMock()
    mock_response.choices[0].message.content = json.dumps({
        "weakness": "Vague lighting parameters.",
        "new_rule": "RULE: [Midjourney] -> [Specify Kelvin values]",
        "ideal_direction": "Include volumetric lighting at 3200K.",
        "pattern_tag": "PALETTE_AMBIGUITY"
    })
    mock_openai_client.chat.completions.create.return_value = mock_response

    result = run_meta_audit(
        intent="Original raw intent",
        target="FLUX",
        refined="A compiled prompt",
        score=75,
        critique="Lacking depth."
    )

    # Verify the API was called correctly
    mock_openai_client.chat.completions.create.assert_called_once()
    
    # Verify payload integrity
    assert result is not None
    assert result["score"] == 75
    assert result["pattern_tag"] == "PALETTE_AMBIGUITY"
    assert result["weakness"] == "Vague lighting parameters."

def test_invalid_json_handling(mock_openai_client):
    """Ensure malformed JSON from the LLM returns None without crashing."""
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "This is not valid JSON."
    mock_openai_client.chat.completions.create.return_value = mock_response

    result = run_meta_audit("intent", "target", "refined", 80, "critique")
    
    assert result is None

def test_api_exception_handling(mock_openai_client):
    """Ensure API timeouts or connection drops are caught and return None."""
    mock_openai_client.chat.completions.create.side_effect = Exception("API Timeout")

    result = run_meta_audit("intent", "target", "refined", 80, "critique")
    
    assert result is None

def test_format_insight_for_display():
    """Verify the string representation formats exactly as expected for the Security Log."""
    insight = {
        "score": 82,
        "pattern_tag": "FORMAT_MISMATCH",
        "weakness": "Used tags instead of prose.",
        "new_rule": "RULE: [DALL-E] -> [Use prose paragraphs]",
        "ideal_direction": "Format as a single cohesive narrative block."
    }
    
    formatted = format_insight_for_display(insight)
    
    assert "[ PATTERN: FORMAT_MISMATCH | SCORE: 82 ]" in formatted
    assert "WEAKNESS: Used tags instead of prose." in formatted
    assert "NEW_RULE: RULE: [DALL-E] -> [Use prose paragraphs]" in formatted
    assert "IDEAL:    Format as a single cohesive narrative block." in formatted

def test_format_insight_empty():
    """Verify empty or None inputs return an empty string safely."""
    assert format_insight_for_display(None) == ""
    assert format_insight_for_display({}) == ""
