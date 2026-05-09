"""
vault/supabase_client.py — Supabase Connection Layer
======================================================
v2.1: Master Sync — Telemetry Alignment.
       - FIXED: Object renamed from 'sb' to 'supabase' to match logic/admin_telemetry.py.
       - UPDATED: Switched to st.secrets for professional cloud security.
"""

import streamlit as st

# 1. Pull credentials from the same vault as your Groq/Master IDs
_url = st.secrets.get("SUPABASE_URL", "").strip()
_key = st.secrets.get("SUPABASE_KEY", "").strip()

# 2. Connection Integrity Check
SUPABASE_MISSING = not (_url and _key)
supabase = None # 🟢 Renamed to match Overwatch telemetry requirements

if not SUPABASE_MISSING:
    try:
        from supabase import create_client
        supabase = create_client(_url, _key)
    except Exception:
        # If the library or connection fails, the app stays stable
        SUPABASE_MISSING = True
        supabase = None
