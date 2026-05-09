# config/thresholds.py

# ── ENGINE CONSTRAINTS (LAUNCH TIER - 8B SPEED) ──────────────────────────────
RETRY_THRESHOLD:      int   = 80    # Lowered from 85 for faster acceptance rates
MAX_RETRIES:          int   = 1     # Reduced from 2. One chance to fix structural errors, then ship.
EVAL_TEMPERATURE:     float = 0.1   # Keep evaluation strictly logical
RATE_WINDOW_SECONDS:  int   = 60
RATE_MAX_CALLS:       int   = 10
INPUT_MAX_CHARS:      int   = 2000
INPUT_WARN_THRESHOLD: int   = 1800
