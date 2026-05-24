"""
security/token.py — JWT Minting and Verification
================================================
"""
import os
import jwt
from datetime import datetime, timedelta, timezone

# We use your Supabase key as the secret signing string.
# If an attacker doesn't have this exact string, they cannot forge a token.
SECRET_KEY = os.environ.get("SUPABASE_KEY", "fallback_secret_do_not_use_in_prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 24 hour session

def create_access_token(user_hash: str, is_admin: bool) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": user_hash,
        "is_admin": is_admin,
        "exp": expire
    }
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None