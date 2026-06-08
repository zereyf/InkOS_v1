"""
state.py — Application Memory Core
====================================
Central registry for session state keys (K) and in-process memory stores.
Decoupled from Streamlit: safe to use in both FastAPI and Streamlit contexts.
"""

from __future__ import annotations

import threading
from datetime import datetime, timezone
from typing import Any, Optional


# ── SESSION STATE KEY REGISTRY ────────────────────────────────────────────────

class K:
    """Single source of truth for all session/state dictionary keys."""

    # Identity & Auth
    USER_HASH    = "user_hash"
    IS_ADMIN     = "is_admin"
    SHOW_PROFILE = "show_profile"
    BOOT_TIME    = "boot_time"

    # Navigation
    UI_LANG      = "ui_lang"
    DARK_MODE    = "dark_mode"

    # Workspace
    LAST_RESULT  = "last_result"
    LAST_AUDIT   = "last_audit"
    LAST_INPUT   = "last_input"
    PROMPT_COUNT = "prompt_count"
    HISTORY      = "history"

    # Routing & Model Selection
    AUTO_TARGET  = "auto_target"
    AUTO_REASON  = "auto_reason"

    # Persona & Style
    ACTIVE_PERSONA  = "active_persona"
    PERSONA_LIST    = "persona_list"
    AESTHETIC_CHOICE = "aesthetic_choice"
    HIKMAH_STYLE    = "hikmah_style"

    # DNA Blocks
    INK_DNA    = "ink_dna"
    INTEL_DNA  = "intel_dna"
    HIKMAH_DNA = "hikmah_dna"

    # Security
    SECURITY_LOG   = "security_log"
    QUARANTINE_LOG = "quarantine_log"

    # CIPHER Pattern Memory
    CIPHER_PATTERNS = "cipher_patterns"
    CIPHER_FAILURES = "cipher_failures"
    META_INSIGHTS   = "meta_insights"
    LAST_META       = "last_meta_audit"


# ── IN-PROCESS MEMORY (FastAPI / thread-safe) ─────────────────────────────────

_API_STATE: dict = {
    K.CIPHER_PATTERNS: [],
    K.CIPHER_FAILURES: [],
    K.META_INSIGHTS:   [],
    K.LAST_META:       {},
}

_GLOBAL_MEM: dict = {}

_state_lock = threading.Lock()


# ── SESSION INITIALISATION ────────────────────────────────────────────────────

def init_session_state() -> None:
    """
    Initialise all expected session state keys with safe defaults.
    Idempotent: only sets keys that are not already present.
    Designed for use in Streamlit via st.session_state.
    """
    try:
        import streamlit as st
        state = st.session_state
    except ImportError:
        return

    defaults: dict[str, Any] = {
        K.USER_HASH:      None,
        K.IS_ADMIN:       False,
        K.SHOW_PROFILE:   False,
        K.BOOT_TIME:      datetime.now(),
        K.UI_LANG:        "en",
        K.DARK_MODE:      True,
        K.LAST_RESULT:    None,
        K.LAST_AUDIT:     {},
        K.LAST_INPUT:     "",
        K.PROMPT_COUNT:   0,
        K.HISTORY:        [],
        K.AUTO_TARGET:    "ChatGPT",
        K.AUTO_REASON:    "Awaiting input...",
        K.ACTIVE_PERSONA: None,
        K.PERSONA_LIST:   [],
        K.AESTHETIC_CHOICE: "Raw (No Preset)",
        K.HIKMAH_STYLE:   "None",
        K.INK_DNA:        "",
        K.INTEL_DNA:      "",
        K.HIKMAH_DNA:     "",
        K.SECURITY_LOG:   [],
        K.QUARANTINE_LOG: [],
        K.CIPHER_PATTERNS: [],
        K.CIPHER_FAILURES: [],
        K.META_INSIGHTS:   [],
        K.LAST_META:       {},
    }

    for key, value in defaults.items():
        if key not in state:
            state[key] = value


def reset_session() -> None:
    """
    Clear volatile session keys while preserving identity and DNA.
    Equivalent to a soft reboot — user stays logged in.
    """
    try:
        import streamlit as st
    except ImportError:
        return

    volatile = [
        K.LAST_RESULT, K.LAST_AUDIT, K.LAST_INPUT,
        K.PROMPT_COUNT, K.HISTORY, K.AUTO_TARGET,
        K.AUTO_REASON, K.SECURITY_LOG, K.QUARANTINE_LOG,
        K.CIPHER_PATTERNS, K.CIPHER_FAILURES,
        K.META_INSIGHTS, K.LAST_META,
    ]
    for key in volatile:
        if key in st.session_state:
            del st.session_state[key]

    init_session_state()


# ── RATE LIMIT HELPER ─────────────────────────────────────────────────────────

def get_remaining_calls() -> int:
    """
    Returns remaining API call slots for the current Streamlit session.
    Delegates to the rate limiter; returns max if unavailable.
    """
    try:
        from config import RATE_MAX_CALLS
        from security.rate_limiter import check_rate_limit
        import streamlit as st
        user_id = st.session_state.get(K.USER_HASH, "global") or "global"
        # Peek without consuming: check if one more call would succeed
        # We approximate by reading the history length from the limiter module
        from security import rate_limiter as rl
        with rl._rate_lock:
            from datetime import timedelta
            now = datetime.now(timezone.utc)
            window_start = now - timedelta(seconds=60)
            history = rl._CLIENT_HISTORY.get(str(user_id), [])
            valid = [t for t in history if t > window_start]
            return max(0, RATE_MAX_CALLS - len(valid))
    except Exception:
        return 10


# ── GLOBAL MEMORY (admin broadcast, maintenance flags) ────────────────────────

def get_global_memory() -> dict:
    """Returns a copy of the global in-process memory dict."""
    with _state_lock:
        return dict(_GLOBAL_MEM)


def update_global_memory(key: str, value: Any) -> None:
    """Thread-safe write to the global memory dict."""
    with _state_lock:
        if value is None:
            _GLOBAL_MEM.pop(key, None)
        else:
            _GLOBAL_MEM[key] = value


# ── CIPHER PATTERN MEMORY ─────────────────────────────────────────────────────

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
            _API_STATE[K.CIPHER_PATTERNS] = sorted(
                patterns, key=lambda x: x["score"], reverse=True
            )[:20]
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


def get_best_pattern_for_target(target: str) -> Optional[dict]:
    with _state_lock:
        try:
            patterns = _API_STATE.get(K.CIPHER_PATTERNS, [])
            relevant = [p for p in patterns if p.get("target") == target]
            return max(relevant, key=lambda x: x["score"]) if relevant else None
        except Exception:
            return None