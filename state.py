"""
state.py — Hardened Session Contract
====================================
v23.0: Intelligence Layer Upgrade.

  Added:
    - K.CIPHER_PATTERNS  — high-score prompt patterns stored per target
    - K.CIPHER_FAILURES  — failed refinements stored for analysis
    - K.META_INSIGHTS    — meta-auditor evolution recommendations
    - K.LAST_META        — last meta-audit result

  All existing keys and logic preserved.
"""

import threading
import streamlit as st
from copy import deepcopy
from datetime import datetime, timedelta, timezone


class K:
    # Logic & History
    HISTORY         = "prompt_history"
    SECURITY_LOG    = "security_log"

    # Identity & DNA
    USER_HASH       = "user_hash"
    IS_ADMIN        = "is_admin"
    INK_DNA         = "ink_dna"
    INTEL_DNA       = "intel_dna"
    HIKMAH_DNA      = "hikmah_dna"
    PERSONA_LIST    = "persona_list"
    ACTIVE_PERSONA  = "active_persona"

    # UI & HUD
    LAST_INPUT       = "last_input"
    LAST_RESULT      = "last_result"
    LAST_AUDIT       = "last_audit"
    LAST_SAVED       = "last_saved"
    AUTO_TARGET      = "auto_target"
    AUTO_REASON      = "auto_reason"
    UI_LANG          = "ui_lang"
    TIMESTAMPS       = "call_timestamps"
    AESTHETIC_CHOICE = "sb_aesthetic"
    HIKMAH_STYLE     = "sb_hikmah_style"
    SHOW_PROFILE     = "show_profile"

    # Profile & Session telemetry
    PROMPT_COUNT    = "prompt_count"
    BOOT_TIME       = "boot_time"

    # ── INTELLIGENCE LAYER (v23.0) ────────────────────────────────────────────
    CIPHER_PATTERNS = "cipher_patterns"
    CIPHER_FAILURES = "cipher_failures"
    META_INSIGHTS   = "meta_insights"
    LAST_META       = "last_meta_audit"


_DEFAULTS = {
    K.HISTORY:         [],
    K.SECURITY_LOG:    [],
    K.USER_HASH:       None,
    K.IS_ADMIN:        False,
    K.INK_DNA:         "Default",
    K.INTEL_DNA:       "Default",
    K.HIKMAH_DNA:      "Default",
    K.PERSONA_LIST:    [],
    K.ACTIVE_PERSONA:  None,
    K.LAST_INPUT:      "",
    K.LAST_RESULT:     None,
    K.LAST_AUDIT:      {},
    K.LAST_SAVED:      "Never",
    K.AUTO_TARGET:     "ChatGPT",
    K.AUTO_REASON:     "Awaiting Uplink...",
    K.UI_LANG:         "en",
    K.TIMESTAMPS:      [],
    K.AESTHETIC_CHOICE:"Default",
    K.HIKMAH_STYLE:    "None",
    K.SHOW_PROFILE:    False,
    K.PROMPT_COUNT:    0,
    K.BOOT_TIME:       None,
    K.CIPHER_PATTERNS: [],
    K.CIPHER_FAILURES: [],
    K.META_INSIGHTS:   [],
    K.LAST_META:       {},
}


@st.cache_resource
def _gmem_lock() -> threading.Lock:
    return threading.Lock()


@st.cache_resource
def get_global_memory() -> dict:
    return {
        "broadcast":        None,
        "maintenance_mode": False,
    }


def update_global_memory(key: str, value) -> None:
    with _gmem_lock():
        get_global_memory()[key] = value


def read_global_memory(key: str, default=None):
    with _gmem_lock():
        return get_global_memory().get(key, default)


def init_session_state() -> None:
    for key, default in _DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = deepcopy(default)
    if st.session_state.get(K.BOOT_TIME) is None:
        st.session_state[K.BOOT_TIME] = datetime.now()


def reset_session() -> None:
    preserved = {
        K.USER_HASH:       st.session_state.get(K.USER_HASH),
        K.IS_ADMIN:        st.session_state.get(K.IS_ADMIN),
        K.INK_DNA:         st.session_state.get(K.INK_DNA),
        K.INTEL_DNA:       st.session_state.get(K.INTEL_DNA),
        K.HIKMAH_DNA:      st.session_state.get(K.HIKMAH_DNA),
        K.PERSONA_LIST:    st.session_state.get(K.PERSONA_LIST),
        K.ACTIVE_PERSONA:  st.session_state.get(K.ACTIVE_PERSONA),
        K.BOOT_TIME:       st.session_state.get(K.BOOT_TIME),
        K.CIPHER_PATTERNS: st.session_state.get(K.CIPHER_PATTERNS, []),
        K.META_INSIGHTS:   st.session_state.get(K.META_INSIGHTS, []),
    }
    st.session_state.clear()
    init_session_state()
    for k, v in preserved.items():
        if v is not None:
            st.session_state[k] = v


def get_remaining_calls(window: int = 60, max_calls: int = 10) -> int:
    try:
        now = datetime.now(timezone.utc)
        st.session_state[K.TIMESTAMPS] = [
            t for t in st.session_state.get(K.TIMESTAMPS, [])
            if t > now - timedelta(seconds=window)
        ]
        return max(0, max_calls - len(st.session_state[K.TIMESTAMPS]))
    except Exception:
        return 0


def store_cipher_pattern(target: str, framework: str, score: int, key_instruction: str) -> None:
    try:
        patterns = st.session_state.get(K.CIPHER_PATTERNS, [])
        patterns.append({
            "target":          target,
            "framework":       framework,
            "score":           score,
            "key_instruction": key_instruction[:500],
            "timestamp":       datetime.now(timezone.utc).isoformat(),
        })
        patterns = sorted(patterns, key=lambda x: x["score"], reverse=True)[:20]
        st.session_state[K.CIPHER_PATTERNS] = patterns
    except Exception:
        pass


def store_cipher_failure(target: str, critique: str, score: int) -> None:
    try:
        failures = st.session_state.get(K.CIPHER_FAILURES, [])
        failures.append({
            "target":    target,
            "critique":  critique[:300],
            "score":     score,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        st.session_state[K.CIPHER_FAILURES] = failures[-10:]
    except Exception:
        pass


def store_meta_insight(insight: dict) -> None:
    try:
        insights = st.session_state.get(K.META_INSIGHTS, [])
        insights.append({
            **insight,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        st.session_state[K.META_INSIGHTS] = insights[-20:]
        st.session_state[K.LAST_META] = insight
    except Exception:
        pass


def get_best_pattern_for_target(target: str) -> dict | None:
    try:
        patterns = st.session_state.get(K.CIPHER_PATTERNS, [])
        relevant = [p for p in patterns if p.get("target") == target]
        if not relevant:
            return None
        return max(relevant, key=lambda x: x["score"])
    except Exception:
        return None
