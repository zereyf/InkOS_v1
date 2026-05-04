"""
vault/supabase_client.py — Supabase Connection Layer
======================================================
Fixed: removed type annotation on conditional reassignment (Python 3.9 issue).
Fixed: single source of truth — config.py no longer declares SUPABASE_MISSING.
"""

import os
from dotenv import load_dotenv

load_dotenv()

_url: str = os.getenv("SUPABASE_URL", "").strip()
_key: str = os.getenv("SUPABASE_KEY", "").strip()

SUPABASE_MISSING: bool = not (_url and _key)
sb = None

if not SUPABASE_MISSING:
    try:
        from supabase import create_client
        sb = create_client(_url, _key)
    except Exception as e:
        SUPABASE_MISSING = True
        sb = None

