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
                 Default 1.

    Returns:
        True  — request is within limit, slots consumed.
        False — limit exceeded, no slots consumed.
    """
    now          = datetime.now(timezone.utc)
    window_start = now - timedelta(seconds=RATE_WINDOW_SECONDS)

    current_timestamps = st.session_state.get(K.TIMESTAMPS, [])

    valid_timestamps = [
        t for t in current_timestamps
        if t > window_start
    ]
    st.session_state[K.TIMESTAMPS] = valid_timestamps

    current = len(valid_timestamps)
    if current + consume > RATE_MAX_CALLS:
        return False

    for _ in range(consume):
        st.session_state[K.TIMESTAMPS].append(now)

    return True
