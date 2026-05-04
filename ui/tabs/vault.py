"""
ui/tabs/vault.py — Prompt Memory Vault Tab
============================================
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
    return "#B07C9E"


def _render_unavailable() -> None:
    st.markdown("""
    <div style="background: rgba(169,50,38,0.08);border: 1px solid rgba(169,50,38,0.3);border-radius: 4px;padding: 20px 24px;font-family: var(--font-m);font-size: 0.78rem;color: #FC8181;line-height: 1.8;">
        <strong style="color:#FC8181;letter-spacing:0.1em;">{t("vault_offline")}</strong><br><br>
        Supabase credentials not found.<br>
        Add to your <code>.env</code> and Streamlit Cloud Secrets:<br><br>
        <code>SUPABASE_URL = "your_project_url"</code><br>
        <code>SUPABASE_KEY = "your_anon_key"</code><br><br>
        See setup instructions in the session that introduced this feature.
    </div>
    """, unsafe_allow_html=True)


def render_vault() -> None:
    """Renders Tab 5 — Prompt Memory Vault."""

    st.markdown(
        f'<div class="vc-header"><span class="status-dot"></span>{t("vault_header")}</div>',
        unsafe_allow_html=True,
    )

    if SUPABASE_MISSING:
        _render_unavailable()
        return

    user_hash: str = st.session_state.get(K.USER_HASH, "")
    if not user_hash:
        st.warning("Session not initialized. Refresh the page.")
        return

    # ── VAULT STATS BAR ────────────────────────────────────────────────────────
    stats, err = get_vault_stats(user_hash)
    if not err and stats.get("count", 0) > 0:
        s_color = _score_color(stats["avg_score"])
        # DEV FIX: Added word-break and overflow wrapping to score-num classes to prevent mobile vertical stretching
        st.markdown(f"""
        <div style="display:flex;gap:12px;margin-bottom:18px;flex-wrap:wrap;">
            <div class="score-block" style="flex:1;min-width:100px;padding:12px 16px;margin:0;overflow:hidden;">
                <div class="score-num" style="font-size:1.8rem;word-wrap:break-word;word-break:break-word;">{stats['count']}</div>
                <div class="score-lbl">Saved Prompts</div>
            </div>
            <div class="score-block" style="flex:1;min-width:100px;padding:12px 16px;margin:0;overflow:hidden;">
                <div class="score-num" style="font-size:1.8rem;color:{s_color};word-wrap:break-word;word-break:break-word;">{stats['avg_score']}<span>%</span></div>
                <div class="score-lbl">Avg Score</div>
            </div>
            <div class="score-block" style="flex:1;min-width:100px;padding:12px 16px;margin:0;overflow:hidden;">
                <div class="score-num" style="font-size:0.9rem;line-height:1.2;color:var(--steel);padding-top:6px;word-wrap:break-word;word-break:break-word;">{stats['top_target']}</div>
                <div class="score-lbl">Top Target</div>
            </div>
            <div class="score-block" style="flex:1;min-width:100px;padding:12px 16px;margin:0;overflow:hidden;">
                <div class="score-num" style="font-size:1rem;color:var(--gold);padding-top:6px;word-wrap:break-word;word-break:break-word;">{stats['top_tag'] or '—'}</div>
                <div class="score-lbl">Top Tag</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── SEARCH + FILTERS ───────────────────────────────────────────────────────
    st.markdown(
        f'<div class="vc-header" style="font-size:0.62rem;">{t("search_label")}</div>',
        unsafe_allow_html=True,
    )

    sc1, sc2, sc3, sc4 = st.columns([3, 2, 2, 1])

    with sc1:
        query = st.text_input(
            t("search_ph"),
            placeholder="Search title, tags, or content...",
            label_visibility="collapsed",
            key="vault_query",
        )
    with sc2:
        all_tags  = get_all_tags(user_hash)
        tag_filter = st.selectbox(
            "Tag",
            [t("all_tags")] + all_tags,
            key="vault_tag_filter",
            label_visibility="collapsed",
        )
    with sc3:
        target_filter = st.selectbox(
            "Target",
            ["All"] + list(TARGET_GUIDES.keys()),
            key="vault_target_filter",
            label_visibility="collapsed",
        )
    with sc4:
        min_score = st.number_input(
            t("min_score"),
            min_value=0,
            max_value=100,
            value=0,
            step=10,
            key="vault_min_score",
            label_visibility="collapsed",
        )

    # ── FETCH RESULTS ──────────────────────────────────────────────────────────
    results, err = search_vault(
        user_hash     = user_hash,
        query         = query,
        tag_filter    = "" if tag_filter == t("all_tags") else tag_filter,
        target_filter = target_filter,
        min_score     = int(min_score),
    )

    if err:
        st.error(f"Vault error: {err}")
        return

    if not results:
        st.markdown(
            '<p style="font-family:var(--font-m);font-size:0.75rem;color:var(--text-muted);">'
            'No prompts found. Execute a refinement and save it to populate your vault.</p>',
            unsafe_allow_html=True,
        )
        return

    st.markdown(
        f'<p style="font-family:var(--font-m);font-size:0.62rem;color:var(--text-muted);letter-spacing:0.1em;margin-bottom:12px;">'
        f'{len(results)} PROMPT{"S" if len(results) != 1 else ""} FOUND</p>',
        unsafe_allow_html=True,
    )

    # ── RESULTS LIST ───────────────────────────────────────────────────────────
    for entry in results:
        score      = entry.get("score", 0)
        s_color    = _score_color(score)
        tags_raw   = entry.get("tags", "")
        tag_chips  = " ".join(
            f'<span style="font-family:var(--font-m);font-size:0.62rem;background:rgba(201,168,76,0.08);border:1px solid var(--gold-border);border-radius:2px;padding:1px 7px;color:var(--gold);margin:1px;">{t.strip()}</span>'
            for t in tags_raw.split(",") if t.strip()
        )
        pattern_tag = (
            f'<span style="font-family:var(--font-a);font-size:0.8rem;color:var(--steel);margin-left:8px;">{entry["pattern"]}</span>'
            if entry.get("pattern") else ""
        )
        islamic_tag = ' <span style="color:#6ee7b7;font-size:0.7rem;">☪</span>' if entry.get("islamic") else ""

        with st.expander(
            f"[{entry['id']}]  {entry['title']}  ·  {score}%  ·  {entry['target']}"
        ):
            # Header row
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;margin-bottom:12px;">
                <div>
                    <span style="font-family:var(--font-d);font-size:1.1rem;color:{s_color};">{score}%</span>
                    {pattern_tag}{islamic_tag}
                </div>
                <div style="text-align:right;">
                    <span style="font-family:var(--font-m);font-size:0.62rem;color:var(--text-muted);">{entry['target']} · {entry['framework']}</span><br>
                    <span style="font-family:var(--font-m);font-size:0.58rem;color:var(--text-dim);">{entry.get('created_at','')[:10]}</span>
                </div>
            </div>
            {f'<div style="margin-bottom:10px;">{tag_chips}</div>' if tag_chips else ''}
            """, unsafe_allow_html=True)

            # Prompt content
            st.code(entry["content"], language="markdown")

            # Action buttons
            a1, a2, a3 = st.columns([2, 2, 1])

            with a1:
                # Deploy: load back into workspace state
                if st.button(
                    t("deploy_workspace"),
                    key=f"deploy_{entry['id']}",
                    use_container_width=True,
                ):
                    st.session_state[K.LAST_RESULT]  = entry["content"]
                    st.session_state[K.LAST_INPUT]   = f"[Loaded from Vault: {entry['title']}]"
                    st.session_state[K.LAST_AUDIT]   = {
                        "score":     entry["score"],
                        "critique":  "Loaded from Vault.",
                        "precision": 0,
                        "alignment": 0,
                        "efficiency":0,
                    }
                    st.session_state[K.LAST_PATTERN] = None
                    st.success(t('deployed_success', title=entry['title']))

            with a2:
                st.download_button(
                    t("download"),
                    data=entry["content"],
                    file_name=f"vault_{entry['id']}.txt",
                    key=f"dl_{entry['id']}",
                    use_container_width=True,
                )

            with a3:
                # Delete with double-confirm via session state flag
                confirm_key = f"confirm_del_{entry['id']}"
                if st.session_state.get(confirm_key):
                    if st.button(
                        t("confirm_delete"),
                        key=f"confirm_btn_{entry['id']}",
                        use_container_width=True,
                    ):
                        ok, del_err = delete_prompt(user_hash, entry["id"])
                        if ok:
                            st.session_state[confirm_key] = False
                            st.session_state[K.VAULT_STATS] = {}  # invalidate cache
                            st.rerun()
                        else:
                            st.error(del_err)
                else:
                    if st.button(
                        t("delete_btn"),
                        key=f"del_{entry['id']}",
                        use_container_width=True,
                    ):
                        st.session_state[confirm_key] = True
                        st.rerun()
