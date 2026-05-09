"""
ui/tabs/vault.py — Prompt Memory Vault Tab
============================================
v8.7: Master Sync — The Athar Protocol.
      - FIXED: Temporal Paradox (StreamlitAPIException) via Callback Protocol.
      - Hardened against Null-returns (TypeError Fix).
      - Atomic HTML Rendering (Prevents card fracture).
      - Forensic String Sanitization (html.escape injection).
      - Synchronized with Workspace v31.0 HUD logic.
"""

import streamlit as st
import textwrap
import html  # Critical for leak protection
from datetime import datetime, timezone
from typing import Optional
from state import K
from vault.vault_engine import (
    search_vault,
    delete_prompt,
    get_vault_stats,
    get_all_tags,
)
from vault.supabase_client import SUPABASE_MISSING
from config import TARGET_GUIDES
from i18n.translations import t

def _score_color(score: int) -> str:
    if score >= 90: return "#C9A84C" # Gold
    if score >= 70: return "#4CAF9A" # Green
    if score >= 50: return "#7C9EBF" # Steel
    return "#E53E3E" # Danger

def _render_unavailable() -> None:
    html_code = textwrap.dedent("""
        <div style="background: rgba(229, 62, 62, 0.05); border-left: 3px solid #E53E3E; padding: 20px 24px; font-family: var(--font-m); font-size: 0.78rem; color: #E2E8F0; line-height: 1.8;">
            <strong style="color:#FC8181;letter-spacing:0.1em;font-size:0.9rem;">✦ VAULT UPLINK OFFLINE</strong><br><br>
            <span style="color:var(--text-muted);">Supabase credentials not found in environment.</span><br>
            Add <code>SUPABASE_URL</code> and <code>SUPABASE_KEY</code> to activate cloud storage.
        </div>
    """)
    st.markdown(html_code, unsafe_allow_html=True)

def _render_vault_locked() -> None:
    html_code = textwrap.dedent(f"""
        <div style="height: 60vh; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; border: 1px dashed rgba(201,168,76,0.15); border-radius: 8px; background: rgba(255,255,255,0.01);">
            <span class="status-dot" style="background:var(--gold); animation: pulse-gold 2s infinite; margin-bottom: 20px;"></span>
            <div style="font-family:var(--font-m); color:var(--gold); font-size:1rem; letter-spacing:2px; text-transform:uppercase; font-weight:600;">
                Vault Uplink Encrypted
            </div>
            <div style="font-family:var(--font-m); color:var(--text-muted); font-size:0.75rem; max-width:450px; line-height:1.7; margin-top:12px; padding: 0 20px;">
                To recover persistent assets and view stats, latch a <b>Terminal Identity</b> via the sidebar.
            </div>
        </div>
    """)
    st.markdown(html_code, unsafe_allow_html=True)

# ── 🟢 CALLBACK FUNCTION (THE FIX) ──
def _deploy_callback(content: str) -> None:
    """Safely injects memory into the Workspace widget before rendering."""
    st.session_state["ta_input_widget"] = content
    st.session_state[K.LAST_RESULT] = content
    # Note: Streamlit automatically triggers a rerun after a callback, 
    # so we don't need st.rerun() here.

def render_vault() -> None:
    st.markdown('<div class="vc-header"><span class="status-dot" style="background:var(--gold);"></span>Neural Memory Vault</div>', unsafe_allow_html=True)

    if SUPABASE_MISSING:
        _render_unavailable()
        return

    user_hash = st.session_state.get(K.USER_HASH, "")
    if not user_hash or "GUEST_" in str(user_hash).upper():
        _render_vault_locked()
        return

    # ── 1. STATS HUD ────────────────────────────────────────────────────────────
    stats, err = get_vault_stats(user_hash)
    if not err and stats.get("count", 0) > 0:
        s_color = _score_color(stats["avg_score"])
        stats_html = textwrap.dedent(f"""
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin-bottom: 30px;">
                <div style="background:var(--bg-card); border:1px solid rgba(255,255,255,0.05); border-left:3px solid var(--steel); padding:12px 16px; border-radius:3px;">
                    <div style="font-size:0.55rem; color:var(--text-muted); letter-spacing:0.1em; font-family:var(--font-m);">MEMORY ASSETS</div>
                    <div style="font-size:1.4rem; color:#E2E8F0; font-family:var(--font-d); margin-top:4px;">{stats['count']}</div>
                </div>
                <div style="background:var(--bg-card); border:1px solid rgba(255,255,255,0.05); border-left:3px solid {s_color}; padding:12px 16px; border-radius:3px;">
                    <div style="font-size:0.55rem; color:var(--text-muted); letter-spacing:0.1em; font-family:var(--font-m);">AVG PRECISION</div>
                    <div style="font-size:1.4rem; color:{s_color}; font-family:var(--font-d); margin-top:4px;">{stats['avg_score']}%</div>
                </div>
                <div style="background:var(--bg-card); border:1px solid rgba(255,255,255,0.05); border-left:3px solid var(--gold); padding:12px 16px; border-radius:3px;">
                    <div style="font-size:0.55rem; color:var(--text-muted); letter-spacing:0.1em; font-family:var(--font-m);">TOP TARGET</div>
                    <div style="font-size:0.85rem; color:var(--gold); font-weight:600; padding-top:6px;">{stats['top_target']}</div>
                </div>
            </div>
        """)
        st.markdown(stats_html, unsafe_allow_html=True)

    # ── 2. SEARCH & FILTERS (HARDENED) ──────────────────────────────────────────
    sc1, sc2, sc3 = st.columns([3, 2, 2])
    with sc1: 
        query = st.text_input(
            "Search", 
            placeholder=t("vault_search_placeholder", fallback="NEURAL_HASH OR DESIGNATION..."), 
            label_visibility="collapsed",
            key="vault_search_input"
        )
    with sc2: 
        tag_filter = st.selectbox("Tag", [t("all_tags", fallback="All Tags")] + get_all_tags(user_hash), label_visibility="collapsed")
    with sc3: 
        target_filter = st.selectbox("Target", ["All"] + list(TARGET_GUIDES.keys()), label_visibility="collapsed")

    # 🟢 FIXED: Null-safe search call to prevent TypeError on unpacking
    vault_response = search_vault(
        user_hash=user_hash,
        query=query,
        tag_filter="" if tag_filter == t("all_tags", fallback="All Tags") else tag_filter,
        target_filter=target_filter
    )

    if vault_response is None:
        st.error("Vault Uplink Interrupted: Database returned Null.")
        return

    results, err = vault_response if isinstance(vault_response, tuple) else (vault_response, None)

    if err:
        st.error(f"Neural Vault Error: {err}")
        return

    if not results:
        st.caption("No matching assets in local or cloud storage.")
        return

    # ── 3. ASSET LISTING (ATHAR PROTOCOL) ───────────────────────────────────────
    now = datetime.now(timezone.utc)
    
    for entry in results:
        score = entry.get("score", 0)
        indicator = "🟢" if score >= 85 else "🟡" if score >= 50 else "🔴"
        
        # 🟢 SAFETY: Escape strings to prevent layout fracturing
        safe_title  = html.escape(entry.get("title", "UNTITLED_CONSTRUCT")).upper()
        safe_tags   = html.escape(entry.get("tags", ""))
        safe_intent = html.escape(entry.get("intent", "No original intent recorded."))
        
        # Temporal Decay Calculation
        try:
            created_dt = datetime.fromisoformat(entry.get("created_at", now.isoformat()).replace('Z', '+00:00'))
            age_days = (now - created_dt).days
        except Exception:
            age_days = 0

        # Archival Branding & Decay FX
        time_tag, opacity, border_fx = "", "1.0", "border:1px solid rgba(255,255,255,0.05);"
        if age_days > 30:
            time_tag, opacity, border_fx = " [DEEP ARCHIVE]", "0.6", "border:1px dashed #E53E3E; border-left:3px solid #E53E3E;"
        elif age_days > 7:
            time_tag, opacity, border_fx = " [DECAYING]", "0.8", "border:1px dashed rgba(124, 158, 191, 0.4);"

        # Render Expander
        with st.expander(f"{indicator} [{entry['id'][:6]}] {safe_title} · {score}% {time_tag}"):
            
            # Metadata Extraction
            aesthetic = entry.get("aesthetic")
            islamic = entry.get("islamic", False)

            aesthetic_badge = f"<span style='background:rgba(201,168,76,0.1); color:var(--gold); padding:2px 6px; border-radius:2px; margin-right:5px;'>{aesthetic.upper() if aesthetic else 'DEFAULT'}</span>"
            islamic_badge = f"<span style='background:rgba(76,175,154,0.1); color:#4CAF9A; padding:2px 6px; border-radius:2px;'>HIKMAH DNA</span>" if islamic else ""

            # 🟢 ATOMIC RENDERING: HTML collapsed to prevent Streamlit tag leaking
            meta_html = (
                f'<div style="background:rgba(255,255,255,0.02); {border_fx} padding:15px; border-radius:3px; margin-bottom:12px; font-family:var(--font-m); font-size:0.55rem; color:var(--text-muted); opacity:{opacity};">'
                f'<div style="display:flex; justify-content:space-between; margin-bottom:8px; border-bottom:1px solid rgba(255,255,255,0.05); padding-bottom:5px;">'
                f'<span>TARGET: <b style="color:var(--text);">{entry.get("target", "GPT").upper()}</b></span>'
                f'<span>AGE: <b style="color:var(--text);">{age_days} DAYS</b></span></div>'
                f'<div style="margin-bottom:10px;"><span>FRAMEWORK: <b style="color:var(--text);">{entry.get("framework", "RACE").upper()}</b></span></div>'
                f'<div style="background:rgba(201,168,76,0.05); padding:8px; border-radius:2px; margin-bottom:10px; color:var(--text-dim); font-style:italic; line-height:1.4;">"{safe_intent}"</div>'
                f'<div style="display:flex; gap:5px; flex-wrap:wrap;">{aesthetic_badge} {islamic_badge}</div>'
                f'<div style="margin-top:10px; font-size:0.5rem; color:var(--steel); letter-spacing:1px;">TAGS: {safe_tags.upper()}</div>'
                f'</div>'
            ).replace("\n", "")
            
            st.markdown(meta_html, unsafe_allow_html=True)
            
            # Content & Actions
            st.code(entry["content"], language="markdown")
            
            a1, a2 = st.columns(2)
            with a1:
                # 🟢 THE CALLBACK INJECTION (Replaces the broken 'if' block)
                st.button(
                    "⚡ DEPLOY TO WORKSPACE", 
                    key=f"dep_{entry['id']}", 
                    use_container_width=True,
                    on_click=_deploy_callback,
                    args=(entry["content"],)
                )
            with a2:
                if st.button("🗑 DELETE", key=f"del_{entry['id']}", use_container_width=True):
                    ok, _ = delete_prompt(user_hash, entry["id"])
                    if ok: 
                        st.toast("Memory Asset Purged.")
                        st.rerun()
