"""
vault/supabase_client.py — Supabase Connection Layer
======================================================
Creates a Supabase client when credentials are present without requiring
Streamlit secrets to exist in non-Streamlit contexts such as tests and scripts.
"""

from __future__ import annotations

import os

import streamlit as st


def _get_secret_or_env(name: str) -> str:
    try:
        value = st.secrets.get(name, "")
    except Exception:
        value = ""
    return str(value or os.getenv(name, "")).strip()


_url = _get_secret_or_env("SUPABASE_URL")
_key = _get_secret_or_env("SUPABASE_KEY")

SUPABASE_MISSING = not (_url and _key)
supabase = None

if not SUPABASE_MISSING:
    try:
        from supabase import create_client

        supabase = create_client(_url, _key)
    except Exception:
        SUPABASE_MISSING = True
        supabase = None
