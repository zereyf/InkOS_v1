"""
ui/tabs/vault.py — Prompt Memory Vault Tab
============================================
v8.0: Privacy Shield Integration.
      Restricts database uplink to verified Terminal Identities only.
"""

import streamlit as st
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
    if score >= 90: return "#C9A84C"
    if score >= 70: return "#4CAF9A"
    if score >= 50: return "#7C9EBF"
    return "#E53E3E"


def _render_unavailable() -> None:
    st.markdown("""
    <div style="
        background: rgba(229, 62, 62, 0.05); 
        border-left: 3px solid #E53E3E; 
        border-radius: 0 4px 4px 0; 
        padding: 20px 24px; 
        font-family: var(--font-m); font-size: 0.78rem; color: #E2E8F0; line-height: 1.8;
    ">
        <strong style="color:#FC8181;letter-spacing:0.1em;font-size:0.9rem;">✦ VAULT UPLINK OFFLINE</strong><br><br>
        <span style="color:var(--text-muted);">Supabase credentials not found in environment.</span><br>
        Add the following to your <code>.env</code> or Streamlit Cloud Secrets to activate cloud storage.
    </div>
    """, unsafe_allow_html=True)


def _render_vault_locked() -> None:
    """Obsidian-style locked state for Guest sessions."""
    st.markdown(f"""
    <div style="
        height: 60vh; display: flex; flex-direction: column; align-items: center; justify-content: center;
        text-align: center; border: 1px dashed rgba(201,168,76,0.15); border-radius: 8px; background: rgba(255,255,255,0.01);
    ">
        <span class="status-dot" style="background:var(--gold); animation: pulse-gold 2s infinite; margin-bottom: 20px;"></span>
        <div style="font-family:var(--font-m); color:var(--gold); font-size:1rem; letter-spacing:2px; text-transform:uppercase; font-weight:600;">
            Vault Uplink Encrypted
        </div>
        <div style="font-family:var(--font-m); color:var(--text-muted); font-size:0.75rem; max-width:450px; line-height:1.7; margin-top:12px; padding: 0 20px;">
            To recover persistent memory assets and view your Prompt Intelligence stats, 
            you must latch a <b>Terminal Identity</b> with a valid Security PIN via the sidebar.
        </div>
        <div style="margin-top:25px; font-size:0.6rem; color:var(--text-dim); font-style:italic;">
            [ STATUS: STANDING BY FOR AUTHENTICATION ]
        </div>
    </div>
    
    <style>
        @keyframes pulse-gold {{
            0% {{ box-shadow: 0 0 0 0px rgba(201, 168, 76, 0.4); }}
            70% {{ box-shadow: 0 0 0 12px rgba(201, 168, 76, 0); }}
            100% {{ box-shadow: 0 0 0 0px rgba(201, 168, 76, 0); }}
        }}
    </style>
    """, unsafe_allow_html=True)


def render_vault() -> None:
    """Renders Tab 5 — Prompt Memory Vault with Identity Intercept."""

    st.markdown(
        f'<div class="vc-header"><span class="status-dot" style="background:var(--gold);box-shadow:0 0-8px var(--gold);"></span>Vault Intelligence</div>',
        unsafe_allow_html=True,
    )

    if SUPABASE_MISSING:
        _render_unavailable()
        return

    # 🛡️ IDENTITY INTERCEPT
    user_hash: str = st.session_state.get(K.USER_HASH, "")
    is_guest = "GUEST_" in str(user_hash).upper()

    if not user_hash or is_guest:
        _render_vault_locked()
        return

    # ── VAULT STATS HUD ──────────────────────────────────────────────────────
    stats, err = get_vault_stats(user_hash)
    if not err and stats.get("count", 0) > 0:
        s_color = _score_color(stats["avg_score"])
        target_display = stats['top_target']
        if "Auto" in target_display: target_display = "CIPHER / AUTO"

        st.markdown(f"""
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin-bottom: 30px;">
<div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05); border-left:3px solid var(--steel); padding:12px 16px; border-radius:4px;">
<div style="font-family:var(--font-m); font-size:0.55rem; color:var(--text-muted); letter-spacing:0.1em; text-transform:uppercase;">Memory Assets</div>
<div style="font-family:var(--font-m); font-size:1.4rem; color:#E2E8F0; font-weight:600;">{stats['count']}</div>
</div>
<div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05); border-left:3px solid {s_color}; padding:12px 16px; border-radius:4px;">
<div style="font-family:var(--font-m); font-size:0.55rem; color:var(--text-muted); letter-spacing:0.1em; text-transform:uppercase;">Fleet Precision</div>
<div style="font-family:var(--font-m); font-size:1.4rem; color:{s_color}; font-weight:600;">{stats['avg_score']}<span style="font-size:0.8rem; opacity:0.6;">%</span></div>
</div>
<div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05); border-left:3px solid var(--gold); padding:12px 16px; border-radius:4px;">
<div style="font-family:var(--font-m); font-size:0.55rem; color:var(--text-muted); letter-spacing:0.1em; text-transform:uppercase;">Primary Uplink</div>
<div style="font-family:var(--font-m); font-size:0.85rem; color:var(--gold); font-weight:600; padding-top:6px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{target_display}</div>
</div>
<div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05); border-left:3px solid #7C9EBF; padding:12px 16px; border-radius:4px;">
<div style="font-family:var(--font-m); font-size:0.55rem; color:var(--text-muted); letter-spacing:0.1em; text-transform:uppercase;">Logic Domain</div>
<div style="font-family:var(--font-m); font-size:0.85rem; color:#E2E8F0; font-weight:600; padding-top:6px;">{stats['top_tag'] or 'GENERAL'}</div>
</div>
</div>
        """, unsafe_allow_html=True)

    # ── SEARCH + FILTERS ───────────────────────────────────────────────────────
    st.markdown('<div style="font-size:0.65rem;color:var(--text-muted);font-family:var(--font-m);margin-bottom:4px;">DATABASE QUERY</div>', unsafe_allow_html=True)
    sc1, sc2, sc3, sc4 = st.columns([3, 2, 2, 1])

    with sc1:
        query = st.text_input(t("search_ph"), placeholder="Search assets...", label_visibility="collapsed", key="vault_query")
    with sc2:
        all_tags = get_all_tags(user_hash)
        tag_filter = st.selectbox("Tag", [t("all_tags")] + all_tags, key="vault_tag_filter", label_visibility="collapsed")
    with sc3:
        target_filter = st.selectbox("Target", ["All"] + list(TARGET_GUIDES.keys()), key="vault_target_filter", label_visibility="collapsed")
    with sc4:
        min_score = st.number_input(t("min_score"), min_value=0, max_value=100, value=0, step=10, key="vault_min_score", label_visibility="collapsed")

    # ── FETCH RESULTS ──────────────────────────────────────────────────────────
    results, err = search_vault(
        user_hash=user_hash,
        query=query,
        tag_filter="" if tag_filter == t("all_tags") else tag_filter,
        target_filter=target_filter,
        min_score=int(min_score),
    )

    if err:
        st.error(f"Vault query failed: {err}")
        return

    if not results:
        st.markdown('<p style="font-family:var(--font-m);font-size:0.75rem;color:var(--text-muted);margin-top:10px;">No matching assets found.</p>', unsafe_allow_html=True)
        return

    st.markdown(f'<div style="font-family:var(--font-m);font-size:0.62rem;color:var(--gold);letter-spacing:0.1em;margin-top:16px;margin-bottom:12px;">✦ {len(results)} ASSET RECOVERED</div>', unsafe_allow_html=True)

    # ── RESULTS LIST ───────────────────────────────────────────────────────────
    for entry in results:
        score = entry.get("score", 0)
        score_indicator = "🟢" if score >= 90 else "🟡" if score >= 80 else "🔴"
            
        tag_chips = " ".join(f'<span style="font-family:var(--font-m);font-size:0.62rem;background:rgba(201,168,76,0.08);border:1px solid var(--gold-border);border-radius:2px;padding:2px 8px;color:var(--gold);margin-right:6px;display:inline-block;margin-bottom:4px;">{tag.strip()}</span>' for tag in entry.get("tags", "").split(",") if tag.strip())
        pattern_tag = f'<span style="font-family:var(--font-a);font-size:0.8rem;color:var(--steel);margin-left:8px;">{entry["pattern"]}</span>' if entry.get("pattern") else ""
        islamic_tag = ' <span style="color:#6ee7b7;font-size:0.7rem;">☪</span>' if entry.get("islamic") else ""

        with st.expander(f"{score_indicator} [{entry['id'][:6]}] {entry['title']} · {score}%"):
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:center; background:rgba(201,168,76,0.05); border:1px solid rgba(201,168,76,0.15); border-radius:4px; padding:10px 14px; margin-bottom:12px;">
                <div style="font-family:var(--font-m); font-size:0.65rem; color:var(--gold);">
                    <span style="margin-right:15px;"><strong>FRAMEWORK:</strong> {entry.get('framework', 'N/A')}</span>
                    <span><strong>AESTHETIC:</strong> {entry.get('aesthetic', 'Raw')}</span>
                    {pattern_tag}{islamic_tag}
                </div>
                <div style="font-family:var(--font-m); font-size:0.58rem; color:var(--text-dim);">SAVED: {entry.get('created_at','')[:10]}</div>
            </div>
            {f'<div style="margin-bottom:12px;">{tag_chips}</div>' if tag_chips else ''}
            """, unsafe_allow_html=True)

            st.code(entry["content"], language="markdown")
            a1, a2, a3 = st.columns([2, 2, 1])

            with a1:
                if st.button(t("deploy_workspace", fallback="Deploy to Workspace"), key=f"deploy_{entry['id']}", use_container_width=True):
                    st.session_state[K.LAST_RESULT] = entry["content"]
                    st.session_state["refined_output_area"] = entry["content"]
                    st.session_state[K.LAST_INPUT] = f"[LOADED FROM VAULT] {entry['title']}"
                    st.session_state[K.LAST_AUDIT] = {"score": entry["score"], "critique": "Recovered from Vault."}
                    st.session_state[K.AUTO_TARGET] = entry['target']
                    st.session_state[K.AUTO_REASON] = "Target locked from Vault."
                    st.success(f"✓ Deployed '{entry['title']}' to Workspace.")

            with a2:
                safe_target = entry['target'].lower().replace(' ', '_').replace('/', '_')
                st.download_button(t("download"), data=entry["content"], file_name=f"inkos_vault_{safe_target}_{entry['id'][:6]}.txt", key=f"dl_{entry['id']}", use_container_width=True)

            with a3:
                confirm_key = f"confirm_del_{entry['id']}"
                if st.session_state.get(confirm_key):
                    if st.button(t("confirm_delete", fallback="Confirm"), key=f"confirm_btn_{entry['id']}", use_container_width=True):
                        ok, del_err = delete_prompt(user_hash, entry["id"])
                        if ok:
                            st.session_state[confirm_key] = False
                            st.session_state[K.VAULT_STATS] = {}
                            st.rerun()
                        else: st.error(del_err)
                else:
                    if st.button(t("delete_btn", fallback="Delete"), key=f"del_{entry['id']}", use_container_width=True):
                        st.session_state[confirm_key] = True
                        st.rerun()
