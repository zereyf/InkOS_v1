"""
vault/supabase_client.py — Supabase Connection Layer (FastAPI Optimized)
========================================================================
Creates a Supabase client using standard environment variables.
Completely decoupled from Streamlit.
"""

from __future__ import annotations
import os

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "").strip()

SUPABASE_MISSING = not (SUPABASE_URL and SUPABASE_KEY)
supabase = None

if not SUPABASE_MISSING:
    try:
        from supabase import create_client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"[InkOS Vault] Supabase initialization failed: {e}")
        SUPABASE_MISSING = True
        supabase = None