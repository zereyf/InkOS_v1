"""
ui/components/profile_overlay.py
================================
v1.0: Local Operator Dossier with SVG Skill Radar.
"""
import streamlit as st
import textwrap
import hashlib
from datetime import datetime
from state import K

def render_profile_overlay():
    # Only render if the /profile command toggled this state to True
    if not st.session_state.get(K.SHOW_PROFILE):
        return

    # ── 1. LOCAL DATA AGGREGATION ──
    prompts = st.session_state.get(K.PROMPT_COUNT, 0)
    level = int((prompts ** 0.5) * 2) + 1
    sid = str(st.session_state.get(K.USER_HASH, "GUEST_ID"))
    dna_hash = hashlib.sha256(sid.encode()).hexdigest()[:12].upper()
    temp = 32 + (prompts * 0.5) % 15 
    
    # Uptime Calculation
    boot_time = st.session_state.get(K.BOOT_TIME)
    if boot_time:
        uptime = datetime.now() - boot_time
        uptime_mins = int(uptime.total_seconds() // 60)
    else:
        uptime_mins = 0

    # ── 2. DYNAMIC SKILL RADAR (PURE LOCAL SVG) ──
    val_logic = min(100, 60 + (prompts * 2))
    val_create = min(100, 40 + (prompts * 1.5))
    val_sec = min(100, 85 + (prompts * 0.5)) 
    val_velocity = min(100, 50 + (prompts * 3))

    pt_top = f"50,{50 - (val_logic * 0.4)}"
    pt_right = f"{50 + (val_create * 0.4)},50"
    pt_bot = f"50,{50 + (val_sec * 0.4)}"
    pt_left = f"{50 - (val_velocity * 0.4)},50"

    svg_radar = f"""
    <svg viewBox="0 0 100 100" style="width: 100%; max-width: 120px; height: auto; filter: drop-shadow(0 0 4px rgba(201,168,76,0.4));">
        <line x1="50" y1="10" x2="50" y2="90" stroke="rgba(255,255,255,0.1)" stroke-width="1" />
        <line x1="10" y1="50" x2="90" y2="50" stroke="rgba(255,255,255,0.1)" stroke-width="1" />
        <polygon points="50,10 90,50 50,90 10,50" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="1" />
        <polygon points="50,30 70,50 50,70 30,50" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="1" />
        <polygon points="{pt_top} {pt_right} {pt_bot} {pt_left}" fill="rgba(201,168,76,0.2)" stroke="var(--gold)" stroke-width="1.5" />
        <circle cx="{pt_top.split(',')[0]}" cy="{pt_top.split(',')[1]}" r="2" fill="var(--gold)" />
        <circle cx="{pt_right.split(',')[0]}" cy="{pt_right.split(',')[1]}" r="2" fill="var(--gold)" />
        <circle cx="{pt_bot.split(',')[0]}" cy="{pt_bot.split(',')[1]}" r="2" fill="var(--gold)" />
        <circle cx="{pt_left.split(',')[0]}" cy="{pt_left.split(',')[1]}" r="2" fill="var(--gold)" />
    </svg>
    """

    # ── 3. THE OVERLAY UI ──
    dossier_html = textwrap.dedent(f"""
        <div style="background: rgba(10,10,10,0.95); border: 1px solid var(--gold); padding: 25px; border-radius: 2px; margin-bottom: 25px; box-shadow: 0 0 30px rgba(0,0,0,0.7);">
            
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid rgba(201,168,76,0.1); padding-bottom: 15px; margin-bottom: 20px;">
                <div>
                    <div style="font-family: var(--font-m); color: var(--gold); font-size: 0.55rem; letter-spacing: 4px;">OPERATOR_DOSSIER // {dna_hash}</div>
                    <h2 style="font-family: var(--font-d); color: var(--text); margin: 0; font-size: 2rem; letter-spacing: 2px;">{sid[:12].upper()}</h2>
                </div>
                <div style="text-align: right;">
                    <div style="font-family: var(--font-m); color: var(--gold); font-size: 0.55rem; letter-spacing: 1px;">CLEARANCE</div>
                    <h2 style="font-family: var(--font-d); color: var(--gold); margin: 0;">LVL_{level:02d}</h2>
                </div>
            </div>

            <div style="display: grid; grid-template-columns: 1.5fr 2fr; gap: 20px; margin-bottom: 20px; align-items: center;">
                <div style="text-align: center; background: rgba(255,255,255,0.01); border: 1px solid rgba(255,255,255,0.03); padding: 10px; border-radius: 4px;">
                    {svg_radar}
                    <div style="font-family: var(--font-m); font-size: 0.45rem; color: var(--text-dim); margin-top: 5px; letter-spacing: 2px;">COGNITIVE_MATRIX</div>
                </div>
                <div style="display: flex; flex-direction: column; gap: 10px;">
                    <div style="background: rgba(255,255,255,0.02); padding: 8px 12px; border-left: 2px solid var(--steel); display: flex; justify-content: space-between;">
                        <span style="font-family: var(--font-m); color: var(--text-dim); font-size: 0.6rem;">L-LOGIC</span>
                        <span style="font-family: var(--font-m); color: var(--text); font-size: 0.7rem;">{val_logic}%</span>
                    </div>
                    <div style="background: rgba(255,255,255,0.02); padding: 8px 12px; border-left: 2px solid var(--steel); display: flex; justify-content: space-between;">
                        <span style="font-family: var(--font-m); color: var(--text-dim); font-size: 0.6rem;">C-CREATE</span>
                        <span style="font-family: var(--font-m); color: var(--text); font-size: 0.7rem;">{val_create}%</span>
                    </div>
                    <div style="background: rgba(255,255,255,0.02); padding: 8px 12px; border-left: 2px solid var(--danger); display: flex; justify-content: space-between;">
                        <span style="font-family: var(--font-m); color: var(--text-dim); font-size: 0.6rem;">S-SECURITY</span>
                        <span style="font-family: var(--font-m); color: var(--text); font-size: 0.7rem;">{val_sec}%</span>
                    </div>
                </div>
            </div>

            <div style="margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; font-family: var(--font-m); font-size: 0.5rem; color: var(--text-muted); margin-bottom: 5px;">
                    <span>PROGRESSION_TO_NEXT_LEVEL</span>
                    <span>72%</span>
                </div>
                <div style="height: 3px; background: rgba(255,255,255,0.05); width: 100%;">
                    <div style="height: 3px; background: var(--gold); width: 72%; box-shadow: 0 0 8px var(--gold);"></div>
                </div>
            </div>

            <div style="display: flex; gap: 8px;">
                <div title="System Architect" style="border: 1px solid var(--gold); color: var(--gold); padding: 4px 8px; font-family: var(--font-m); font-size: 0.5rem;">[ ◈ ] ARCHITECT</div>
                <div title="Verified Operator" style="border: 1px solid #4CAF9A; color: #4CAF9A; padding: 4px 8px; font-family: var(--font-m); font-size: 0.5rem;">[ ◈ ] SESSION_UPTIME: {uptime_mins}m</div>
            </div>
            
            <div style="margin-top: 20px; text-align: center; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 10px;">
                <span style="font-family: var(--font-m); font-size: 0.5rem; color: var(--text-dim); letter-spacing: 2px;">VELVETCODEX // NEURAL_TEMP: {temp:.1f}°C</span>
            </div>
        </div>
    """)
    
    st.markdown(dossier_html, unsafe_allow_html=True)
    
    # Unique Key added to prevent duplication bugs
    if st.button("[ CLOSE_DOSSIER ]", use_container_width=True, key="close_dossier_btn"):
        st.session_state[K.SHOW_PROFILE] = False
        st.rerun()
