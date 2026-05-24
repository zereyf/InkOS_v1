"""
security/rate_limiter.py — API Rate Limiter (FastAPI Optimized)
===============================================================
Decoupled from Streamlit. Uses in-memory thread-safe tracking per client ID.
"""

import threading
from datetime import datetime, timedelta, timezone
from config import RATE_WINDOW_SECONDS, RATE_MAX_CALLS

_rate_lock = threading.Lock()

# Dictionary to store timestamps per user/IP.
# Key: str (client_id), Value: list of datetime objects
_CLIENT_HISTORY = {}

def check_rate_limit(client_id: str = "global", consume: int = 1) -> bool:
    """
    Sliding window rate limiter for the API.
    
    Args:
        client_id: The IP address or Auth Token of the user making the request.
        consume: Number of API call slots this operation consumes.
    """
    with _rate_lock:
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(seconds=RATE_WINDOW_SECONDS)

        history = _CLIENT_HISTORY.get(client_id, [])

        # Filter valid timestamps within the 60-second window
        valid_timestamps = [t for t in history if t > window_start]

        current = len(valid_timestamps)
        
        # If adding this call exceeds the limit, reject it
        if current + consume > RATE_MAX_CALLS:
            _CLIENT_HISTORY[client_id] = valid_timestamps
            return False

        # Otherwise, log the timestamps and approve
        for _ in range(consume):
            valid_timestamps.append(now)

        _CLIENT_HISTORY[client_id] = valid_timestamps
        return True