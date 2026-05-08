"""
ui/tabs/vault.py — Prompt Memory Vault Tab
============================================
v8.3: Master Sync — The Athar Protocol.
      Integrated Visual Decay for aging assets.
      Surfaced Hikmah (Islamic) and Aesthetic metadata tags.
"""

import streamlit as st
import textwrap
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
    html = textwrap.dedent("""
        <div style="background: rgba(229, 62, 62, 0.05); border-left: 3px solid #E53E3E; padding: 20px 24px; font-family: var(--font-m); font-size: 0.78rem; color: #E2E8F0; line-height: 1.8;">
            <strong style="color:#FC8181;letter-spacing:0.1em;font-size:0.9rem;">✦ VAULT UPLINK OFFLINE</strong><br><br>
            <span style="color:var(--text-muted);">Supabase credentials not found in environment.</span><br>
            Add <code>SUPABASE_URL</code> and <code>SUPABASE_KEY</code> to activate cloud storage.
        </div>
    """)
    st.markdown(html, unsafe_allow_html=True)

def _render_vault_locked() -> None:
    html = textwrap.dedent(f"""
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
    st.markdown(html, unsafe_allow_html=True)

def render_vault() -> None:
    st.markdown('<div class="vc-header"><span class="status-dot" style="background:var(--gold);"></span>Neural Memory Vault</div>', unsafe_allow_html=True)

    if SUPABASE_MISSING:
        _render_unavailable()
        return

    user_hash = st.session_state.get(K.USER_HASH, "")
    if not user_hash or "GUEST_" in str(user_hash).upper():
        _render_vault_locked()
        return

    # ── STATS HUD ────────────────────────────────────────────────────────────
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

    # ── SEARCH & FILTERS ─────────────────────────────────────────────────────
    sc1, sc2, sc3 = st.columns([3, 2, 2])
    with sc1: query = st.text_input("Search", placeholder="Asset title or tags...", label_visibility="collapsed")
    with sc2: tag_filter = st.selectbox("Tag", [t("all_tags")] + get_all_tags(user_hash), label_visibility="collapsed")
    with sc3: target_filter = st.selectbox("Target", ["All"] + list(TARGET_GUIDES.keys()), label_visibility="collapsed")

    results, err = search_vault(
        user_hash=user_hash,
        query=query,
        tag_filter="" if tag_filter == t("all_tags") else tag_filter,
        target_filter=target_filter
    )

    if not results:
        st.info("No memory assets found matching these parameters.")
        return

    # ── ASSET LISTING (ATHAR PROTOCOL) ───────────────────────────────────────
    now = datetime.now(timezone.utc)
    
    for entry in results:
        score = entry.get("score", 0)
        indicator = "🟢" if score >= 85 else "🟡" if score >= 50 else "🔴"
        
        # 1. Temporal Decay Calculation
        try:
            created_dt = datetime.fromisoformat(entry.get("created_at", now.isoformat()).replace('Z', '+00:00'))
            age_days = (now - created_dt).days
        except Exception:
            age_days = 0

        # 2. Archival Branding
        time_tag = ""
        opacity = "1.0"
        border_fx = "border:1px solid rgba(255,255,255,0.05);"
        
        if age_days > 30:
            time_tag = " [DEEP ARCHIVE]"
            opacity = "0.5"
            border_fx = "border:1px dashed rgba(229, 62, 62, 0.3); border-left:3px solid #E53E3E;"
        elif age_days > 7:
            time_tag = " [DECAYING]"
            opacity = "0.75"
            border_fx = "border:1px dashed rgba(124, 158, 191, 0.3);"

        # 3. Metadata Extraction
        aesthetic = entry.get("aesthetic")
        islamic = entry.get("islamic", False)
        tags = entry.get("tags", "")

        tags_html = f"<div style='margin-top:8px; font-size:0.5rem; color:var(--steel); letter-spacing:1px;'>TAGS: {tags.upper()}</div>" if tags else ""
        aesthetic_html = f"<span style='background:rgba(201,168,76,0.1); color:var(--gold); padding:2px 6px; border-radius:2px;'>AESTHETIC: {aesthetic.upper()}</span> " if aesthetic and aesthetic != "None" else ""
        islamic_html = f"<span style='background:rgba(76,175,154,0.1); color:#4CAF9A; padding:2px 6px; border-radius:2px;'>HIKMAH DNA ACTIVE</span>" if islamic else ""

        # 4. Render Expander
        with st.expander(f"{indicator} [{entry['id'][:6]}] {entry['title']} · {score}% {time_tag}"):
            
            meta_html = textwrap.dedent(f"""
                <div style="background:rgba(255,255,255,0.02); {border_fx} padding:12px; margin-bottom:12px; font-family:var(--font-m); font-size:0.55rem; color:var(--text-muted); opacity:{opacity}; transition: 0.3s;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                        <span>TARGET: <b style="color:var(--text);">{entry['target']}</b></span>
                        <span>AGE: <b style="color:var(--text);">{age_days} DAYS</b></span>
                    </div>
                    <div style="margin-bottom:6px;">
                        <span>FRAMEWORK: <b style="color:var(--text);">{entry['framework']}</b></span>
                    </div>
                    <div style="display:flex; gap:8px; margin-top:8px;">
                        {aesthetic_html}
                        {islamic_html}
                    </div>
                    {tags_html}
                </div>
            """)
            st.markdown(meta_html, unsafe_allow_html=True)
            
            # The prompt payload
            st.code(entry["content"], language="markdown")
            
            # Actions
            a1, a2 = st.columns(2)
            with a1:
                if st.button("⚡ Deploy to Workspace", key=f"dep_{entry['id']}", use_container_width=True):
                    st.session_state[K.LAST_RESULT] = entry["content"]
                    st.session_state[K.LAST_INPUT] = f"[VAULT MEMORY] {entry['title']}"
                    st.session_state[K.AUTO_TARGET] = entry.get("target", "Unknown")
                    st.session_state[K.AUTO_REASON] = "Asset recovered from Vault."
                    # Mock a perfect audit for deployed assets
                    st.session_state[K.LAST_AUDIT] = {"score": score, "precision": 40, "alignment": 40, "efficiency": 20, "critique": "Asset deployed from Neural Vault."}
                    st.toast("Asset deployed to workspace.")
            with a2:
                if st.button("🗑 Delete", key=f"del_{entry['id']}", use_container_width=True):
                    ok, _ = delete_prompt(user_hash, entry["id"])
                    if ok: st.rerun()
