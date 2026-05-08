"""
ui/tabs/vault.py — Prompt Memory Vault Tab
============================================
v8.5: Hardened Structural Build.
      - Collapsed HTML Segments (Prevents Template Fracture/Leak).
      - Absolute Sanitization (html.escape).
      - Forensic Designation Latch (Upper-case).
"""

import streamlit as st
import textwrap
import html 
from datetime import datetime, timezone
from state import K
from vault.vault_engine import search_vault, delete_prompt, get_vault_stats, get_all_tags
from vault.supabase_client import SUPABASE_MISSING
from config import TARGET_GUIDES
from i18n.translations import t

def _score_color(score: int) -> str:
    if score >= 90: return "#C9A84C"
    if score >= 70: return "#4CAF9A"
    if score >= 50: return "#7C9EBF"
    return "#E53E3E"

def render_vault() -> None:
    st.markdown('<div class="vc-header"><span class="status-dot" style="background:var(--gold);"></span>Neural Memory Vault</div>', unsafe_allow_html=True)

    if SUPABASE_MISSING or not st.session_state.get(K.USER_HASH) or "GUEST_" in str(st.session_state.get(K.USER_HASH)).upper():
        st.warning("Vault Uplink Encrypted. Latch Identity to continue.")
        return

    user_hash = st.session_state[K.USER_HASH]
    
    # ── 1. SEARCH BAR ──
    sc1, sc2, sc3 = st.columns([3, 2, 2])
    with sc1: query = st.text_input("Search", placeholder=t("vault_search", fallback="NEURAL_HASH OR DESIGNATION..."), label_visibility="collapsed", key="v_search")
    with sc2: tag_filter = st.selectbox("Tag", [t("all_tags", fallback="All Tags")] + get_all_tags(user_hash), label_visibility="collapsed")
    with sc3: target_filter = st.selectbox("Target", ["All"] + list(TARGET_GUIDES.keys()), label_visibility="collapsed")

    results, _ = search_vault(user_hash, query, "" if tag_filter == t("all_tags", fallback="All Tags") else tag_filter, target_filter)

    if not results:
        st.caption("No matching assets in local or cloud storage.")
        return

    # ── 2. ASSET LISTING ──
    now = datetime.now(timezone.utc)
    for entry in results:
        score = entry.get("score", 0)
        indicator = "🟢" if score >= 85 else "🟡" if score >= 50 else "🔴"
        safe_title = html.escape(entry.get("title", "UNTITLED")).upper()
        safe_intent = html.escape(entry.get("intent", "No original intent recorded."))
        
        try:
            age_days = (now - datetime.fromisoformat(entry.get("created_at", now.isoformat()).replace('Z', '+00:00'))).days
        except: age_days = 0

        # Card Attributes
        border = "border:1px solid rgba(255,255,255,0.05);"
        if age_days > 7: border = "border:1px dashed rgba(124, 158, 191, 0.4);"

        with st.expander(f"{indicator} [{entry['id'][:6]}] {safe_title} · {score}%"):
            # 🟢 CRITICAL: Collapse HTML to single line to prevent Streamlit rendering leaks
            card_html = (
                f'<div style="background:rgba(255,255,255,0.02); {border} padding:15px; border-radius:3px; margin-bottom:12px; font-family:var(--font-m); font-size:0.55rem; color:var(--text-muted);">'
                f'<div style="display:flex; justify-content:space-between; margin-bottom:8px; border-bottom:1px solid rgba(255,255,255,0.05); padding-bottom:5px;">'
                f'<span>TARGET: <b style="color:var(--text);">{entry["target"].upper()}</b></span>'
                f'<span>AGE: <b style="color:var(--text);">{age_days} DAYS</b></span></div>'
                f'<div style="background:rgba(201,168,76,0.05); padding:8px; border-radius:2px; margin-bottom:10px; color:var(--text-dim); font-style:italic;">"{safe_intent}"</div>'
                f'<div style="font-size:0.5rem; color:var(--steel); letter-spacing:1px;">TAGS: {html.escape(entry.get("tags", "")).upper()}</div>'
                f'</div>'
            ).replace("\n", "") # Absolute protection against leaked tags
            
            st.markdown(card_html, unsafe_allow_html=True)
            st.code(entry["content"], language="markdown")
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("⚡ DEPLOY", key=f"v_dep_{entry['id']}", use_container_width=True):
                    st.session_state["ta_input_widget"] = entry["content"]
                    st.toast("Asset Deployed.")
                    st.rerun()
            with c2:
                if st.button("🗑 DELETE", key=f"v_del_{entry['id']}", use_container_width=True):
                    ok, _ = delete_prompt(user_hash, entry["id"])
                    if ok: st.rerun()
