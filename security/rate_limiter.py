"""
security/rate_limiter.py — Sliding Window Rate Limiter
========================================================
v4.0: UTC Timezone enforcement and memory-safe initialization.
Decoupled from UI. Reads/writes session state via K keys from state.py.
consume parameter makes multi-call operations declare their true cost.
"""

import streamlit as st
from datetime import datetime, timedelta, timezone
from state import K
from config import RATE_WINDOW_SECONDS, RATE_MAX_CALLS


def check_rate_limit(consume: int = 1) -> bool:
    """
    Sliding window rate limiter.

    Args:
        consume: Number of API call slots this operation consumes.
                 Default 1 — VelvetCodex v7 uses single combined calls.
                 Set to 2 if a future operation fires two separate requests.

    Returns:
        True  — request is within limit, slots consumed.
        False — limit exceeded, no slots consumed.

    WHY consume parameter:
        Without it, the UI must know implementation details about how many
        API calls each engine function makes. consume externalizes that
        contract cleanly.
    """
    # STRICT UTC ENFORCEMENT
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(seconds=RATE_WINDOW_SECONDS)

    # Safe array retrieval to prevent KeyErrors during hot-reloads
    current_timestamps = st.session_state.get(K.TIMESTAMPS, [])
    
    # Purge expired timestamps
    valid_timestamps = [
        t for t in current_timestamps
        if t > window_start
    ]
    st.session_state[K.TIMESTAMPS] = valid_timestamps

    current = len(valid_timestamps)
    if current + consume > RATE_MAX_CALLS:
        return False

    # Consume slots atomically
    for _ in range(consume):
        st.session_state[K.TIMESTAMPS].append(now)

    return True
