"""
ui/tabs/workspace.py — Workspace Tab
======================================
v29.0: Dynamic HUD Status & Branded Error Handling.
       Synchronized with v16.0 Engine and v18.1 Vault.
"""

import hashlib
import textwrap
import streamlit as st
from datetime import datetime, timezone
from typing import Optional, Tuple

from state import K
from security.sanitizer import sanitize_input
from security.rate_limiter import check_rate_limit
from engine.cognitive_map import detect_arabic_pattern
from engine.refiner import run_refinement_and_audit, detect_best_target
from config import INPUT_MAX_CHARS, INPUT_WARN_THRESHOLD, AUTO_SELECT_LABEL
from i18n.translations import t

def _render_score_block(audit: dict, pattern: Optional[dict], triggers: list = None) -> None:
    score = int(audit.get("score", 0))
    precision = int(audit.get("precision", 0))
    alignment = int(audit.get("alignment", 0))
    efficiency = int(audit.get("efficiency", 0))
    critique = str(audit.get("critique", ""))
    
    # 🧠 DYNAMIC STATUS LOGIC
    if "[TERMINAL THROTTLED]" in critique:
        status_label = "THROTTLED"
        status_color = "#E53E3E" # Red
    elif score == 0:
        status_label = "NOT OPTIMIZED"
        status_color = "var(--text-dim)"
    elif score < 85:
        status_label = "SUB-OPTIMAL"
        status_color = "#C9A84C" # Gold/Yellow
    else:
        status_label = "OPTIMIZED"
        status_color = "#4CAF9A" # Green

    p_pct, a_pct, e_pct = min(100, (precision/40)*100), min(100, (alignment/40)*100), min(100, (efficiency/20)*100)

    # 💎 THE HIGH-END FORENSIC HUD
    hud_html = textwrap.dedent(f"""
        <div style="background: var(--bg-card); border: 1px solid rgba(255,255,255,0.05); border-radius: 3px; padding: 22px; position: relative; overflow: hidden; margin-bottom: 15px;">
            <div style="position: absolute; top: 0; left: 0; width: 40px; height: 2px; background: {status_color}; box-shadow: 0 0 10px {status_color};"></div>
            <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 24px;">
                <div>
                    <div style="font-family: var(--font-m); font-size: 0.55rem; color: var(--text-muted); letter-spacing: 2px; text-transform: uppercase;">Overall Fidelity</div>
                    <div style="font-family: var(--font-d); font-size: 3.2rem; color: {status_color}; line-height: 0.9; margin-top: 4px;">{score}<span style="font-size: 1.2rem; color: var(--gold-dim);">%</span></div>
                </div>
                <div style="text-align: right;">
                    <div style="font-family: var(--font-m); font-size: 0.5rem; color: var(--steel); letter-spacing: 1px;">STATUS</div>
                    <div style="font-family: var(--font-m); font-size: 0.75rem; color: {status_color}; font-weight: bold; letter-spacing: 1px;">{status_label}</div>
                </div>
            </div>
            <div style="display: flex; flex-direction: column; gap: 12px; margin-bottom: 24px;">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <span style="font-family: var(--font-m); font-size: 0.6rem; color: var(--text-muted); width: 80px; letter-spacing: 1px;">PRECISION</span>
                    <div style="flex: 1; height: 1px; background: rgba(255,255,255,0.08); margin: 0 15px; position: relative;"><div style="position: absolute; left: 0; top: -1px; height: 3px; width: {p_pct}%; background: var(--gold); box-shadow: 0 0 6px var(--gold);"></div></div>
                    <span style="font-family: var(--font-m); font-size: 0.65rem; color: var(--gold); width: 40px; text-align: right;">{precision}/40</span>
                </div>
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <span style="font-family: var(--font-m); font-size: 0.6rem; color: var(--text-muted); width: 80px; letter-spacing: 1px;">ALIGNMENT</span>
                    <div style="flex: 1; height: 1px; background: rgba(255,255,255,0.08); margin: 0 15px; position: relative;"><div style="position: absolute; left: 0; top: -1px; height: 3px; width: {a_pct}%; background: var(--steel); box-shadow: 0 0 6px var(--steel);"></div></div>
                    <span style="font-family: var(--font-m); font-size: 0.65rem; color: var(--steel); width: 40px; text-align: right;">{alignment}/40</span>
                </div>
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <span style="font-family: var(--font-m); font-size: 0.6rem; color: var(--text-muted); width: 80px; letter-spacing: 1px;">EFFICIENCY</span>
                    <div style="flex: 1; height: 1px; background: rgba(255,255,255,0.08); margin: 0 15px; position: relative;"><div style="position: absolute; left: 0; top: -1px; height: 3px; width: {e_pct}%; background: #4CAF9A; box-shadow: 0 0 6px #4CAF9A;"></div></div>
                    <span style="font-family: var(--font-m); font-size: 0.65rem; color: #4CAF9A; width: 40px; text-align: right;">{efficiency}/20</span>
                </div>
            </div>
            <div style="background: rgba(201,168,76,0.03); border-left: 2px solid var(--gold-border); padding: 12px 16px;">
                <div style="font-family: var(--font-m); font-size: 0.55rem; color: var(--gold); letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 6px;">> Forensic Log</div>
                <div style="font-family: var(--font-m); font-size: 0.75rem; color: var(--text); line-height: 1.6;">{critique}</div>
            </div>
        </div>
    """)
    st.markdown(hud_html, unsafe_allow_html=True)
