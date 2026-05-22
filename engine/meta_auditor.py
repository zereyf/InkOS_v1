"""
engine/meta_auditor.py — CIPHER Self-Improvement Engine
=========================================================
v1.0: Adversarial meta-analysis loop.
"""

from __future__ import annotations

import json
import sys
from typing import Optional

from config.api import client, MODEL_ID, EVAL_TEMPERATURE, REQUEST_TIMEOUT_SECONDS


META_AUDIT_PROMPT = """
You are a meta-level prompt engineering analyst. Your job is not to score — it is to find
failure modes and generate improvement rules.

You will receive:
- INTENT: what the user wanted
- TARGET: which AI model the prompt is for
- COMPILED: the prompt that was produced (first 800 chars)
- SCORE: the quality score (0-100)
- CRITIQUE: what the evaluator flagged

Answer these four questions precisely:

1. WEAKEST_DECISION — the single weakest architectural decision (be specific)
2. NEW_RULE — write as: "RULE: [target context] → [specific instruction]"
3. IDEAL_DIRECTION — one sentence on what a score-100 version would have done differently
4. PATTERN_TAG — one word: ROLE_VAGUENESS, MISSING_PROHIBITION, ZONE_COLLAPSE,
   PALETTE_AMBIGUITY, FORMAT_MISMATCH, CONTRADICTION_UNRESOLVED, etc.

Respond ONLY with valid JSON. No preamble. No markdown.
{
  "weakness": "...",
  "new_rule": "...",
  "ideal_direction": "...",
  "pattern_tag": "...",
  "score": <int>
}
""".strip()


def run_meta_audit(
    intent:   str,
    target:   str,
    refined:  str,
    score:    int,
    critique: str,
) -> Optional[dict]:
    """
    Run adversarial meta-analysis on a completed refinement.
    Returns insight dict or None on failure. Never raises.
    """
    if not client:
        return None

    if score >= 95:
        return {
            "weakness":        "None detected at this score level.",
            "new_rule":        "No new rule required.",
            "ideal_direction": "Output is at or near ceiling quality.",
            "pattern_tag":     "CEILING_QUALITY",
            "score":           score,
        }

    user_content = (
        f"INTENT: {intent[:300]}\n"
        f"TARGET: {target}\n"
        f"SCORE: {score}\n"
        f"CRITIQUE: {critique[:200]}\n\n"
        f"COMPILED PROMPT (first 800 chars):\n{refined[:800]}"
    )

    try:
        completion = client.chat.completions.create(
            model    = MODEL_ID,
            messages = [
                {"role": "system", "content": META_AUDIT_PROMPT},
                {"role": "user",   "content": user_content},
            ],
            response_format = {"type": "json_object"},
            temperature     = EVAL_TEMPERATURE,
            max_tokens      = 400,
            timeout         = REQUEST_TIMEOUT_SECONDS,
        )
        raw = completion.choices[0].message.content
        result = json.loads(raw)
        result["score"] = score
        return result
    except json.JSONDecodeError as e:
        print(f"[meta_auditor] JSON parse error: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"[meta_auditor] Audit failed: {e}", file=sys.stderr)
        return None


def format_insight_for_display(insight: dict) -> str:
    if not insight:
        return ""
    return "\n".join([
        f"[ PATTERN: {insight.get('pattern_tag', 'UNKNOWN')} | SCORE: {insight.get('score', 0)} ]",
        f"WEAKNESS: {insight.get('weakness', '—')}",
        f"NEW_RULE: {insight.get('new_rule', '—')}",
        f"IDEAL:    {insight.get('ideal_direction', '—')}",
    ])
