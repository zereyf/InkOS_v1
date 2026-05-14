"""
state.py — Hardened Session Contract
====================================
v22.0: Phase 1 + Phase 2 combined.

  Phase 1:
    - ADDED K.PROMPT_COUNT, K.BOOT_TIME (profile overlay crash fix)
    - CONFIRMED K.AUTO_TARGET, K.AUTO_REASON in _DEFAULTS

  Phase 2 (SEC-4):
    - get_global_memory() is now backed by a threading.Lock
    - update_global_memory(key, value) helper added for all writes
    - read_global_memory(key) helper for consistent snapshots
    - Direct dict reads still work for backward compat
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

    # Profile & Session telemetry (Phase 1 addition)
    PROMPT_COUNT    = "prompt_count"
    BOOT_TIME       = "boot_time"


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
}


# ── SEC-4: Thread-safe global memory ─────────────────────────────────────────

@st.cache_resource
def _gmem_lock() -> threading.Lock:
    """Single Lock shared across all Streamlit worker threads."""
    return threading.Lock()


@st.cache_resource
def get_global_memory() -> dict:
    """
    Shared mutable state dict — same reference for all threads.
    Read directly; write only via update_global_memory().
    """
    return {
        "broadcast":        None,
        "maintenance_mode": False,
    }


def update_global_memory(key: str, value) -> None:
    """Thread-safe write. Use this for all mutations."""
    with _gmem_lock():
        get_global_memory()[key] = value


def read_global_memory(key: str, default=None):
    """Thread-safe snapshot read."""
    with _gmem_lock():
        return get_global_memory().get(key, default)


# ── Session state ─────────────────────────────────────────────────────────────

def init_session_state() -> None:
    """Safe against Streamlit hot-reloads."""
    for key, default in _DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = deepcopy(default)

    if st.session_state.get(K.BOOT_TIME) is None:
        st.session_state[K.BOOT_TIME] = datetime.now()


def reset_session() -> None:
    """Wipes transient history, preserves latch identity and DNA."""
    preserved = {
        K.USER_HASH:      st.session_state.get(K.USER_HASH),
        K.IS_ADMIN:       st.session_state.get(K.IS_ADMIN),
        K.INK_DNA:        st.session_state.get(K.INK_DNA),
        K.INTEL_DNA:      st.session_state.get(K.INTEL_DNA),
        K.HIKMAH_DNA:     st.session_state.get(K.HIKMAH_DNA),
        K.PERSONA_LIST:   st.session_state.get(K.PERSONA_LIST),
        K.ACTIVE_PERSONA: st.session_state.get(K.ACTIVE_PERSONA),
        K.BOOT_TIME:      st.session_state.get(K.BOOT_TIME),
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
