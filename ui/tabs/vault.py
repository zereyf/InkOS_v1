"""
ui/tabs/vault.py — Prompt Memory Vault Tab
============================================
v9.1: Zenith Edition — Patch 1 (Toast Dispatcher).
      - FIXED: Rehydration toast now fires correctly via render-loop listener.
      - RETAINED: Deep Rehydration, Chronos Sort, and Forensic UI.
"""

import streamlit as st
import textwrap
import html
from datetime import datetime, timezone
from typing import Optional, List
from state import K
from vault.vault_engine import (
    search_vault,
    delete_prompt,
    get_vault_stats,
    get_all_tags,
)
from vault.supabase_client import SUPABASE_MISSING
LOCAL_VAULT_KEY = "local_vault_items"
from config import TARGET_GUIDES, LOGIC_FRAMEWORKS, AESTHETIC_PRESETS
from i18n.translations import t

# ── 🟢 DYNAMIC UI HELPERS ───────────────────────────────────────────────────

def _score_color(score: int) -> str:
    if score >= 90: return "var(--gold)"
    if score >= 75: return "#4CAF9A"
    if score >= 50: return "#7C9EBF"
    return "#E53E3E"

def _render_vault_locked() -> None:
    st.markdown(textwrap.dedent(f"""
        <div style="height: 60vh; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; border: 1px dashed rgba(201,168,76,0.15); border-radius: 4px; background: rgba(0,0,0,0.2);">
            <div class="status-dot" style="background:var(--gold); animation: pulse-gold 2s infinite; margin-bottom: 20px;"></div>
            <div style="font-family:var(--font-m); color:var(--gold); font-size:0.8rem; letter-spacing:4px; text-transform:uppercase; font-weight:bold;">
                VAULT_UPLINK_ENCRYPTED
            </div>
            <div style="font-family:var(--font-m); color:var(--text-dim); font-size:0.6rem; max-width:350px; line-height:1.8; margin-top:15px; letter-spacing:1px;">
                IDENTITY NOT LATCHED. PLEASE VERIFY TERMINAL CREDENTIALS IN THE SIDEBAR TO ACCESS THE NEURAL ARCHIVE.
            </div>
        </div>
    """), unsafe_allow_html=True)

# ── 🟢 DEEP REHYDRATION CALLBACK ──────────────────────────────────────────

# NEW — fixed
def _vault_rehydrate_callback(content: str, target: str, framework: str, aesthetic: str, title: str) -> None:
    """Teleports saved mission settings back into the primary UI state."""
    st.session_state["workspace_text"] = content   # FIX: was "ta_input_widget"
    st.session_state[K.LAST_RESULT] = None         # clear so output panel doesn't show vault content
    st.session_state[K.LAST_AUDIT] = {}
    st.session_state["sb_target"] = target
    st.session_state["sb_framework"] = framework
    st.session_state["sb_aesthetic"] = aesthetic
    st.session_state["rehydrate_msg"] = f"VAULT_REHYDRATION: {title[:20]}..."
    st.session_state["_archive_cache_dirty"] = True
    st.session_state["active_tab"] = "WORKSPACE"   # navigate user to workspace

# ── 🟢 MAIN RENDERER ──────────────────────────────────────────────────────────

def render_vault() -> None:
    # ── 🟢 TOAST DISPATCHER (Listener) ──
    if st.session_state.get("rehydrate_msg"):
        st.toast(st.session_state["rehydrate_msg"], icon="⚡")
        st.session_state["rehydrate_msg"] = None # Clear after firing

    st.markdown('<div class="vc-header"><span class="status-dot" style="background:var(--gold);"></span>NEURAL_MEMORY_VAULT</div>', unsafe_allow_html=True)

    if st.session_state.get("vault_local_banner"):
        st.warning("Saving locally — Vault connection unavailable")

    user_hash = st.session_state.get(K.USER_HASH, "")

    if SUPABASE_MISSING:
        local = [x for x in st.session_state.get(LOCAL_VAULT_KEY, []) if x.get("user_hash") == user_hash]
        if not local:
            st.info("Your refined prompt will appear here\n\nستظهر نتيجتك هنا")
            return
        results, search_err = local, None
    else:
        results, search_err = None, None

    if not user_hash or "GUEST_" in str(user_hash).upper():
        _render_vault_locked()
        return

    # ── 1. STATS HUD ──
    stats, err = get_vault_stats(user_hash)
    if not err and stats.get("count", 0) > 0:
        s_color = _score_color(stats["avg_score"])
        st.markdown(f"""
            <div style="display: grid; grid-template-columns: 1fr 1fr 1.5fr; gap: 10px; margin-bottom: 25px;">
                <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05); border-left:2px solid var(--steel); padding:15px; border-radius:2px;">
                    <div style="font-size:0.45rem; color:var(--text-dim); letter-spacing:2px; font-family:var(--font-m);">ASSETS</div>
                    <div style="font-size:1.4rem; color:var(--text); font-family:var(--font-d);">{stats['count']}</div>
                </div>
                <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05); border-left:2px solid {s_color}; padding:15px; border-radius:2px;">
                    <div style="font-size:0.45rem; color:var(--text-dim); letter-spacing:2px; font-family:var(--font-m);">PRECISION</div>
                    <div style="font-size:1.4rem; color:{s_color}; font-family:var(--font-d);">{stats['avg_score']}%</div>
                </div>
                <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05); border-left:2px solid var(--gold); padding:15px; border-radius:2px;">
                    <div style="font-size:0.45rem; color:var(--text-dim); letter-spacing:2px; font-family:var(--font-m);">TOP_TARGET</div>
                    <div style="font-size:0.75rem; color:var(--gold); font-family:var(--font-m); padding-top:8px; font-weight:bold; letter-spacing:1px;">{stats['top_target'].upper()}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # ── 2. FORENSIC SEARCH MATRIX ──
    sc1, sc2, sc3, sc4 = st.columns([2.5, 1.5, 1.5, 1.5])
    with sc1: 
        query = st.text_input("Search", placeholder="NEURAL_HASH OR DESIGNATION...", label_visibility="collapsed", key="v_search")
    with sc2: 
        tag_filter = st.selectbox("Tag", ["All Tags"] + get_all_tags(user_hash), label_visibility="collapsed")
    with sc3: 
        target_filter = st.selectbox("Target", ["All Targets"] + list(TARGET_GUIDES.keys()), label_visibility="collapsed")
    with sc4:
        sort_order = st.selectbox("Chronos", ["Newest", "Oldest", "Highest Score", "Lowest Score"], label_visibility="collapsed")

    if results is None:
        results, search_err = search_vault(
            user_hash=user_hash, query=query,
            tag_filter="" if tag_filter == "All Tags" else tag_filter,
            target_filter="" if target_filter == "All Targets" else target_filter
        )

    if search_err:
        st.error(f"VAULT_SEARCH_FAILED: {search_err}")
        return

    if not results:
        st.markdown('<div style="text-align:center; padding: 40px; opacity:0.5; font-size:0.7rem;">[ ⨂ ] NO MATCHING ASSETS FOUND.</div>', unsafe_allow_html=True)
        return

    # ── Chronos Sort ──
    if sort_order == "Highest Score":
        results = sorted(results, key=lambda x: x.get('score', 0), reverse=True)
    elif sort_order == "Lowest Score":
        results = sorted(results, key=lambda x: x.get('score', 0))
    elif sort_order == "Oldest":
        results = sorted(results, key=lambda x: x.get('created_at', ''))
    else: # Newest
        results = sorted(results, key=lambda x: x.get('created_at', ''), reverse=True)

    # ── 3. ASSET LISTING ──
    now = datetime.now(timezone.utc)
    for entry in results:
        score = entry.get("score", 0)
        s_color = _score_color(score)
        safe_title = html.escape(entry.get("title", "UNTITLED_CONSTRUCT")).upper()
        safe_intent = html.escape(entry.get("intent", "No original intent recorded."))
        
        try:
            created_dt = datetime.fromisoformat(entry.get("created_at", now.isoformat()).replace('Z', '+00:00'))
            age_days = (now - created_dt).days
        except: age_days = 0

        border_fx = f"border:1px solid rgba(255,255,255,0.05); border-left:3px solid {s_color};"
        label = f"[{score}%] {safe_title} // ID:{entry['id'][:6]}"

        with st.expander(label):
            aesthetic = entry.get("aesthetic", "Default")
            framework = entry.get("framework", "RACE")
            target = entry.get("target", "ChatGPT")

            meta_html = textwrap.dedent(f"""
                <div style="background:rgba(10,12,16,0.6); {border_fx} padding:15px; border-radius:2px; margin-bottom:12px; font-family:var(--font-m); position:relative; overflow:hidden;">
                    <div style="position:absolute; top:0; left:0; width:100%; height:100%; background: repeating-linear-gradient(0deg, transparent, transparent 1px, rgba(255,255,255,0.01) 1px, rgba(255,255,255,0.01) 2px); pointer-events:none;"></div>
                    <div style="display:flex; justify-content:space-between; margin-bottom:10px; font-size:0.5rem; color:var(--text-dim); letter-spacing:1px; border-bottom:1px solid rgba(255,255,255,0.05); padding-bottom:5px;">
                        <span>UPLINK: {target.upper()}</span>
                        <span>AGE: {age_days}D</span>
                    </div>
                    <div style="font-size:0.65rem; color:var(--text); line-height:1.5; margin-bottom:12px; font-style:italic; opacity:0.8;">"{safe_intent}"</div>
                    <div style="display:flex; gap:8px;">
                        <span style="background:rgba(201,168,76,0.1); color:var(--gold); padding:2px 6px; border-radius:2px; font-size:0.5rem;">{aesthetic.upper()}</span>
                        <span style="background:rgba(255,255,255,0.05); color:var(--text-dim); padding:2px 6px; border-radius:2px; font-size:0.5rem;">{framework.upper()}</span>
                    </div>
                </div>
            """).replace("\n", "")
            
            st.markdown(meta_html, unsafe_allow_html=True)
            st.code(entry["content"], language="markdown")
            
            a1, a2 = st.columns(2)
            with a1:
                st.button(
                    "⚡ REHYDRATE STATE", key=f"dep_{entry['id']}", 
                    use_container_width=True, type="primary",
                    on_click=_vault_rehydrate_callback,
                    args=(entry["content"], target, framework, aesthetic, safe_title)
                )
            with a2:
                if st.button("🗑 PURGE", key=f"del_{entry['id']}", use_container_width=True):
                    ok, delete_err = delete_prompt(user_hash, entry["id"])
                    if ok: 
                        st.session_state["_archive_cache_dirty"] = True
                        st.toast("ASSET PURGED.")
                        st.rerun()
                    else:
                        st.error(f"VAULT_PURGE_FAILED: {delete_err or 'Unknown error.'}")
