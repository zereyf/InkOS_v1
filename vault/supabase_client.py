"""
vault/supabase_client.py — Supabase Connection Layer
"""
import streamlit as st

# 1. Pull credentials from Streamlit Secrets
_url = st.secrets.get("SUPABASE_URL", "").strip()
_key = st.secrets.get("SUPABASE_KEY", "").strip()

# 2. Connection Integrity Check
SUPABASE_MISSING = not (_url and _key)
supabase = None  # 🟢 Renamed from 'sb'

if not SUPABASE_MISSING:
    try:
        from supabase import create_client
        supabase = create_client(_url, _key) # 🟢 Renamed from 'sb'
    except Exception:
        SUPABASE_MISSING = True
        supabase = None
