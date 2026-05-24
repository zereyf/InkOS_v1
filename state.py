"""
state.py — API Memory Core (FastAPI Optimized)
==============================================
Rebuilt to use standard Python memory dictionaries instead of Streamlit state.
"""

import threading
from datetime import datetime, timezone

class K:
    CIPHER_PATTERNS = "cipher_patterns"
    CIPHER_FAILURES = "cipher_failures"
    META_INSIGHTS   = "meta_insights"
    LAST_META       = "last_meta_audit"

# Replace st.session_state with a thread-safe global dictionary
_API_STATE = {
    K.CIPHER_PATTERNS: [],
    K.CIPHER_FAILURES: [],
    K.META_INSIGHTS:   [],
    K.LAST_META:       {},
}

_state_lock = threading.Lock()

def store_cipher_pattern(target: str, framework: str, score: int, key_instruction: str) -> None:
    with _state_lock:
        try:
            patterns = _API_STATE.get(K.CIPHER_PATTERNS, [])
            patterns.append({
                "target":          target,
                "framework":       framework,
                "score":           score,
                "key_instruction": key_instruction[:500],
                "timestamp":       datetime.now(timezone.utc).isoformat(),
            })
            patterns = sorted(patterns, key=lambda x: x["score"], reverse=True)[:20]
            _API_STATE[K.CIPHER_PATTERNS] = patterns
        except Exception:
            pass

def store_cipher_failure(target: str, critique: str, score: int) -> None:
    with _state_lock:
        try:
            failures = _API_STATE.get(K.CIPHER_FAILURES, [])
            failures.append({
                "target":    target,
                "critique":  critique[:300],
                "score":     score,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            _API_STATE[K.CIPHER_FAILURES] = failures[-10:]
        except Exception:
            pass

def store_meta_insight(insight: dict) -> None:
    with _state_lock:
        try:
            insights = _API_STATE.get(K.META_INSIGHTS, [])
            insights.append({
                **insight,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            _API_STATE[K.META_INSIGHTS] = insights[-20:]
            _API_STATE[K.LAST_META] = insight
        except Exception:
            pass

def get_best_pattern_for_target(target: str) -> dict | None:
    with _state_lock:
        try:
            patterns = _API_STATE.get(K.CIPHER_PATTERNS, [])
            relevant = [p for p in patterns if p.get("target") == target]
            if not relevant:
                return None
            return max(relevant, key=lambda x: x["score"])
        except Exception:
            return None