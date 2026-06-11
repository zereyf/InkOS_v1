"""
security/token.py — JWT Minting and Verification
==================================================
Signs tokens with a dedicated JWT_SECRET environment variable.

JWT_SECRET must be separate from SUPABASE_KEY: compromising one must
not compromise the other.

Startup behaviour:
  - Development (ENVIRONMENT=development): missing JWT_SECRET logs a
    warning and uses a local-only fallback. Tokens signed this way are
    invalid in any other environment.
  - Production (default): missing JWT_SECRET raises RuntimeError at
    import time, crashing the process before it accepts any requests.
"""

import os
import warnings

import jwt
from datetime import datetime, timedelta, timezone

# ── ALGORITHM ────────────────────────────────────────────────────────────────

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24-hour sessions

# ── SECRET RESOLUTION ─────────────────────────────────────────────────────────

_ENVIRONMENT = os.environ.get("ENVIRONMENT", "production").strip().lower()
_IS_DEV      = _ENVIRONMENT == "development"

_JWT_SECRET  = os.environ.get("JWT_SECRET", "").strip()

if not _JWT_SECRET:
    if _IS_DEV:
        _JWT_SECRET = "inkos-dev-only-jwt-secret-not-for-production"
        warnings.warn(
            "JWT_SECRET is not set. Using an insecure development fallback. "
            "Tokens signed here are invalid in any other environment. "
            "Set JWT_SECRET before deploying.",
            RuntimeWarning,
            stacklevel=1,
        )
    else:
        raise RuntimeError(
            "JWT_SECRET environment variable is not set. "
            "InkOS cannot start without a dedicated signing secret. "
            "Add JWT_SECRET to your environment or secrets manager."
        )

# Explicit check: make sure nobody accidentally pointed JWT_SECRET at SUPABASE_KEY
_SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "").strip()
if _SUPABASE_KEY and _JWT_SECRET == _SUPABASE_KEY:
    raise RuntimeError(
        "JWT_SECRET must not be the same value as SUPABASE_KEY. "
        "Use a separate randomly-generated secret for JWT signing."
    )


# ── PUBLIC API ────────────────────────────────────────────────────────────────

def create_access_token(user_hash: str, is_admin: bool) -> str:
    """Mint a signed JWT for the given user."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub":      user_hash,
        "is_admin": is_admin,
        "exp":      expire,
    }
    return jwt.encode(payload, _JWT_SECRET, algorithm=ALGORITHM)


def verify_token(token: str) -> dict | None:
    """
    Decode and verify a JWT. Returns the payload dict on success, None on
    any failure (expired, invalid signature, malformed).
    """
    if not token:
        return None
    try:
        return jwt.decode(token, _JWT_SECRET, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None