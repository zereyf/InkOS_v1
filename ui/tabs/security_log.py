"""
ui/tabs/security_log.py — Security & Forensic Ledger Tab
==========================================================
v9.0: CIPHER Evolution Recommendations panel added.

CHANGES FROM v8.0:
  - Third tab added: CIPHER EVOLUTION
    Displays meta-auditor insights — the system's self-generated
    improvement recommendations. Each insight shows:
      - Pattern tag (failure type)
      - The weakest decision in the compilation
      - The new rule that would prevent it
      - The ideal direction for a score-100 version
    This is the living record of how CIPHER should evolve.

  - All v8.0 Neural Audit Trail and Threat Intrusions logic preserved.
"""

import json
import textwrap
import streamlit as st
from datetime import datetime, timezone
from state import K


def render_security_log() -> None:
    st.markdown(
        '<div class="vc-header"><span class="status-dot" style="background:var(--steel);"></span>Forensic Black Box</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div style="font-family:var(--font-m); font-size:0.6rem; color:var(--text-muted); '
        'margin-bottom:20px; letter-spacing:1px; text-transform:uppercase;">'
        'Terminal Audit Trail · Intrusion Ledger · CIPHER Evolution'
        '</div>',
        unsafe_allow_html=True,
    )

    tab_audit, tab_threats, tab_evolution = st.tabs([
        "Neural Audit Trail",
        "Threat Intrusions",
        "◈ CIPHER Evolution",
    ])

    # ── TAB 1: NEURAL AUDIT TRAIL ─────────────────────────────────────────────
    with tab_audit:
        history = st.session_state.get(K.HISTORY, [])

        if not history:
            st.markdown(
                '<div style="background:rgba(255,255,255,0.02); border:1px dashed rgba(255,255,255,0.1); '
                'padding:20px; text-align:center; border-radius:3px;">'
                '<span style="font-family:var(--font-m); font-size:0.65rem; color:var(--text-dim);">'
                'AWAITING INITIAL NEURAL UPLINK...</span></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div style="font-family:var(--font-m); font-size:0.6rem; color:var(--steel); '
                f'margin-bottom:15px; letter-spacing:1px;">✦ {len(history)} UPLINK(S) RECORDED</div>',
                unsafe_allow_html=True,
            )

            for idx, run in enumerate(reversed(history)):
                score     = run.get("score", 0)
                dt_str    = run.get("timestamp", "UNKNOWN")
                try:
                    dt_obj       = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
                    time_display = dt_obj.strftime("%H:%M:%S")
                except Exception:
                    time_display = dt_str[:8]

                target      = run.get("target", "UNKNOWN")
                intent      = run.get("intent", "")
                short_intent = intent[:90] + "..." if len(intent) > 90 else intent
                divergence  = 100 - score
                div_color   = "var(--danger)" if divergence > 40 else "var(--gold)" if divergence > 15 else "#4CAF9A"

                audit_html = textwrap.dedent(f"""
                    <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05);
                                border-left:2px solid var(--steel); padding:10px 14px;
                                font-family:var(--font-m); margin-bottom:8px;">
                        <div style="display:flex; justify-content:space-between; font-size:0.55rem;
                                    color:var(--text-muted); margin-bottom:6px;">
                            <span>[{time_display}] // CIPHER: <b style="color:var(--text);">{target.upper()}</b></span>
                            <span>FIDELITY: <b style="color:var(--text);">{score}%</b>
                                  &nbsp;|&nbsp; DIVERGENCE: <b style="color:{div_color};">{divergence}%</b></span>
                        </div>
                        <div style="font-size:0.65rem; color:var(--text-dim);
                                    border-left:1px solid rgba(255,255,255,0.1);
                                    padding-left:8px; line-height:1.4;">
                            <span style="color:var(--steel);">INTENT:</span>
                            <span style="color:var(--text);">{short_intent}</span>
                        </div>
                    </div>
                """)

                with st.expander(f"[{time_display}] Run {len(history)-idx} — {target} · {score}%"):
                    st.markdown(audit_html, unsafe_allow_html=True)
                    st.markdown(
                        "<div style='font-size:0.55rem; color:var(--gold); margin-bottom:4px; "
                        "font-family:var(--font-m); letter-spacing:1px;'>[ REFINED_ASSET ]</div>",
                        unsafe_allow_html=True,
                    )
                    st.code(run.get("asset", ""), language="markdown")

        st.markdown("<hr style='opacity:0.1'>", unsafe_allow_html=True)
        if "hist_export_filename" not in st.session_state:
            st.session_state["hist_export_filename"] = (
                f"inkos_audit_trail_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M')}.json"
            )

        st.download_button(
            "💾 Download Audit Trail",
            data      = json.dumps(history, ensure_ascii=False, indent=2),
            file_name = st.session_state["hist_export_filename"],
            mime      = "application/json",
            use_container_width = True,
            disabled  = (len(history) == 0),
        )

    # ── TAB 2: THREAT INTRUSIONS ──────────────────────────────────────────────
    with tab_threats:
        log = st.session_state.get(K.SECURITY_LOG, [])

        if not log:
            st.markdown(
                '<div style="background:rgba(39,174,96,0.05); border:1px solid rgba(39,174,96,0.25); '
                'border-radius:3px; padding:16px; text-align:center; font-family:var(--font-m); '
                'font-size:0.7rem; color:#27AE60;">SYSTEM SECURE. ZERO INTRUSIONS DETECTED.</div>',
                unsafe_allow_html=True,
            )
        else:
            count = len(log)
            st.markdown(
                f'<div style="font-family:var(--font-m); font-size:0.65rem; color:#FC8181; '
                f'letter-spacing:1px; margin-bottom:16px;">✦ {count} HOSTILE ATTEMPT'
                f'{"S" if count > 1 else ""} INTERCEPTED</div>',
                unsafe_allow_html=True,
            )

            for entry in reversed(log):
                patterns_html = "".join([
                    f"<code style='color:#FC8181; background:rgba(252,129,129,0.1); "
                    f"margin-right:6px; padding:3px 6px; border-radius:2px; "
                    f"display:inline-block; margin-bottom:4px; font-size:0.6rem;'>"
                    f"{p}</code>"
                    for p in entry.get("patterns", [])
                ])

                st.markdown(f"""
                <div style="background:rgba(229,62,62,0.05); border-left:2px solid #E53E3E;
                            padding:12px; margin-bottom:12px; border-radius:0 3px 3px 0;">
                    <div style="font-family:var(--font-m); font-size:0.6rem; color:var(--text-muted);
                                margin-bottom:8px; display:flex; justify-content:space-between;">
                        <span><b style="color:#E53E3E;">[{entry["time"]}]</b></span>
                        <span>TARGET HASH: <code style="color:var(--gold); background:transparent;
                              padding:0;">{entry["hash"]}</code></span>
                    </div>
                    <div style="font-family:var(--font-m); font-size:0.7rem;">
                        <div style="font-size:0.55rem; color:var(--text-muted); margin-bottom:6px;
                                    letter-spacing:1px;">VIOLATION SIGNATURE(S):</div>
                        <div>{patterns_html}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<hr style='opacity:0.1'>", unsafe_allow_html=True)
        if "sec_export_filename" not in st.session_state:
            st.session_state["sec_export_filename"] = (
                f"inkos_threat_report_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M')}.json"
            )

        st.download_button(
            "🚨 Export Threat Report",
            data      = json.dumps(log, ensure_ascii=False, indent=2),
            file_name = st.session_state["sec_export_filename"],
            mime      = "application/json",
            key       = "btn_export_sec",
            use_container_width = True,
            disabled  = (len(log) == 0),
        )

    # ── TAB 3: CIPHER EVOLUTION ───────────────────────────────────────────────
    with tab_evolution:
        insights = st.session_state.get(K.META_INSIGHTS, [])
        patterns = st.session_state.get(K.CIPHER_PATTERNS, [])
        failures = st.session_state.get(K.CIPHER_FAILURES, [])

        st.markdown(
            '<div style="font-family:var(--font-m); font-size:0.6rem; color:var(--gold); '
            'letter-spacing:2px; margin-bottom:6px; text-transform:uppercase;">CIPHER Self-Improvement Record</div>'
            '<div style="font-family:var(--font-m); font-size:0.65rem; color:var(--text-muted); '
            'line-height:1.7; margin-bottom:20px;">'
            'Every refinement generates a meta-audit. This tab shows what CIPHER has learned '
            'about its own failure modes and what rules would make it stronger.'
            '</div>',
            unsafe_allow_html=True,
        )

        # ── Stats HUD ─────────────────────────────────────────────────────────
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.markdown(
                f'<div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05); '
                f'border-left:2px solid #4CAF9A; padding:12px; border-radius:2px;">'
                f'<div style="font-family:var(--font-m); font-size:0.45rem; color:var(--text-dim); '
                f'letter-spacing:2px;">HIGH PATTERNS</div>'
                f'<div style="font-family:var(--font-d); font-size:1.6rem; color:#4CAF9A;">'
                f'{len(patterns)}</div></div>',
                unsafe_allow_html=True,
            )
        with col_b:
            st.markdown(
                f'<div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05); '
                f'border-left:2px solid var(--danger); padding:12px; border-radius:2px;">'
                f'<div style="font-family:var(--font-m); font-size:0.45rem; color:var(--text-dim); '
                f'letter-spacing:2px;">FAILURES LOGGED</div>'
                f'<div style="font-family:var(--font-d); font-size:1.6rem; color:var(--danger);">'
                f'{len(failures)}</div></div>',
                unsafe_allow_html=True,
            )
        with col_c:
            st.markdown(
                f'<div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05); '
                f'border-left:2px solid var(--gold); padding:12px; border-radius:2px;">'
                f'<div style="font-family:var(--font-m); font-size:0.45rem; color:var(--text-dim); '
                f'letter-spacing:2px;">INSIGHTS</div>'
                f'<div style="font-family:var(--font-d); font-size:1.6rem; color:var(--gold);">'
                f'{len(insights)}</div></div>',
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        # ── Evolution insights ─────────────────────────────────────────────────
        if not insights:
            st.markdown(
                '<div style="border:1px dashed rgba(255,255,255,0.06); border-radius:4px; '
                'padding:30px; text-align:center;">'
                '<div style="font-family:var(--font-m); font-size:0.65rem; color:var(--text-dim);">'
                '[ ◈ ] No evolution data yet. Run refinements to generate insights.'
                '</div></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div style="font-family:var(--font-m); font-size:0.55rem; color:var(--text-dim); '
                'letter-spacing:2px; margin-bottom:12px;">EVOLUTION LOG — MOST RECENT FIRST</div>',
                unsafe_allow_html=True,
            )
            for i, insight in enumerate(reversed(insights)):
                tag       = insight.get("pattern_tag", "UNKNOWN")
                score     = insight.get("score", 0)
                weakness  = insight.get("weakness", "—")
                new_rule  = insight.get("new_rule", "—")
                ideal     = insight.get("ideal_direction", "—")
                timestamp = insight.get("timestamp", "")

                try:
                    ts_fmt = datetime.fromisoformat(timestamp).strftime("%H:%M:%S")
                except Exception:
                    ts_fmt = "—"

                tag_color = "#E57373" if score < 60 else "var(--gold)" if score < 85 else "#4CAF9A"

                with st.expander(f"[{ts_fmt}] {tag} · score {score}"):
                    st.markdown(f"""
                    <div style="font-family:var(--font-m); font-size:0.7rem; line-height:1.8;">
                        <div style="display:inline-flex; align-items:center; gap:6px; padding:2px 8px;
                                    background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08);
                                    border-radius:2px; margin-bottom:12px;">
                            <span style="color:{tag_color}; font-size:0.55rem; letter-spacing:2px;">
                                ◈ {tag}
                            </span>
                        </div>
                        <div style="margin-bottom:10px;">
                            <span style="color:var(--danger); font-size:0.55rem; letter-spacing:1px;">
                                WEAKEST DECISION
                            </span><br>
                            <span style="color:var(--text);">{weakness}</span>
                        </div>
                        <div style="margin-bottom:10px; background:rgba(201,168,76,0.04);
                                    border-left:2px solid var(--gold-border); padding:8px 12px;
                                    border-radius:0 2px 2px 0;">
                            <span style="color:var(--gold); font-size:0.55rem; letter-spacing:1px;">
                                PROPOSED NEW RULE
                            </span><br>
                            <span style="color:var(--text);">{new_rule}</span>
                        </div>
                        <div>
                            <span style="color:#4CAF9A; font-size:0.55rem; letter-spacing:1px;">
                                IDEAL DIRECTION
                            </span><br>
                            <span style="color:var(--text-muted);">{ideal}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        # ── High-performing patterns ───────────────────────────────────────────
        if patterns:
            st.markdown("<hr style='opacity:0.08; margin:20px 0;'>", unsafe_allow_html=True)
            st.markdown(
                '<div style="font-family:var(--font-m); font-size:0.55rem; color:#4CAF9A; '
                'letter-spacing:2px; margin-bottom:12px;">HIGH-PERFORMANCE PATTERNS (score ≥ 85)</div>',
                unsafe_allow_html=True,
            )
            for p in sorted(patterns, key=lambda x: x["score"], reverse=True)[:5]:
                st.markdown(
                    f'<div style="background:rgba(76,175,154,0.04); border:1px solid rgba(76,175,154,0.15); '
                    f'border-left:2px solid #4CAF9A; padding:10px 14px; margin-bottom:8px; '
                    f'border-radius:0 2px 2px 0; font-family:var(--font-m); font-size:0.65rem;">'
                    f'<span style="color:#4CAF9A; font-size:0.5rem;">{p["target"]} · {p["score"]}%</span><br>'
                    f'<span style="color:var(--text-muted);">{p.get("key_instruction","")[:200]}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        st.markdown("<hr style='opacity:0.1'>", unsafe_allow_html=True)
        if st.button("🔥 Clear Evolution Data", use_container_width=True, key="clear_evolution"):
            st.session_state[K.META_INSIGHTS]   = []
            st.session_state[K.CIPHER_PATTERNS] = []
            st.session_state[K.CIPHER_FAILURES] = []
            st.toast("Evolution data cleared.")
            st.rerun()
