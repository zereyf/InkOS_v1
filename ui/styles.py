"""
ui/styles.py — VelvetCodex Design System
==========================================
The full CSS string exported as a single constant.
"""

STYLES: str = """
<style>
/* ══════════════════════════════════════════
   FONT IMPORTS
══════════════════════════════════════════ */
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=IBM+Plex+Mono:ital,wght@0,300;0,400;0,500;1,300&family=Noto+Naskh+Arabic:wght@400;600;700&display=swap');

/* ══════════════════════════════════════════
   DESIGN TOKENS
══════════════════════════════════════════ */
:root {
    --bg-void:     #03040A;
    --bg-deep:     #07090F;
    --bg-card:     #0B1019;
    --bg-raised:   #101520;
    --bg-input:    #080C14;
    --gold:        #C9A84C;
    --gold-dim:    #8A6E2E;
    --gold-glow:   rgba(201,168,76,0.14);
    --gold-border: rgba(201,168,76,0.28);
    --gold-faint:  rgba(201,168,76,0.06);
    --steel:       #7C9EBF;
    --danger:      #A93226;
    --danger-glow: rgba(169,50,38,0.12);
    --success:     #1E8449;
    --text:        #E2D5BC;
    --text-muted:  #5D6D7E;
    --text-dim:    #2C3545;
    --font-d:      'Cinzel', Georgia, serif;
    --font-m:      'IBM Plex Mono', 'Courier New', monospace;
    --font-a:      'Noto Naskh Arabic', 'Arial Unicode MS', serif;
}

/* ══════════════════════════════════════════
   RESET & BASE
══════════════════════════════════════════ */
*, *::before, *::after { box-sizing: border-box; margin: 0; }
.stApp {
    background-color: var(--bg-void);
    color: var(--text);
    font-family: var(--font-m);
    font-size: 14px;
}

/* ══════════════════════════════════════════
   CUSTOM CURSOR — gold crosshair
══════════════════════════════════════════ */
* {
    cursor: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24'%3E%3Cline x1='12' y1='2' x2='12' y2='10' stroke='%23C9A84C' stroke-width='1.5'/%3E%3Cline x1='12' y1='14' x2='12' y2='22' stroke='%23C9A84C' stroke-width='1.5'/%3E%3Cline x1='2' y1='12' x2='10' y2='12' stroke='%23C9A84C' stroke-width='1.5'/%3E%3Cline x1='14' y1='12' x2='22' y2='12' stroke='%23C9A84C' stroke-width='1.5'/%3E%3Ccircle cx='12' cy='12' r='2' fill='none' stroke='%23C9A84C' stroke-width='1'/%3E%3C/svg%3E") 12 12, crosshair !important;
}
a, button, [role="button"], select, input, textarea, label {
    cursor: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24'%3E%3Cline x1='12' y1='2' x2='12' y2='10' stroke='%23C9A84C' stroke-width='1.5'/%3E%3Cline x1='12' y1='14' x2='12' y2='22' stroke='%23C9A84C' stroke-width='1.5'/%3E%3Cline x1='2' y1='12' x2='10' y2='12' stroke='%23C9A84C' stroke-width='1.5'/%3E%3Cline x1='14' y1='12' x2='22' y2='12' stroke='%23C9A84C' stroke-width='1.5'/%3E%3Ccircle cx='12' cy='12' r='2' fill='none' stroke='%23C9A84C' stroke-width='1.5'/%3E%3C/svg%3E") 12 12, pointer !important;
}

/* ══════════════════════════════════════════
   ARABIC GEOMETRIC BACKGROUND
══════════════════════════════════════════ */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120'%3E%3Cdefs%3E%3Cpattern id='vc-geo-001' x='0' y='0' width='120' height='120' patternUnits='userSpaceOnUse'%3E%3Cg fill='none' stroke='%23C9A84C' stroke-width='0.4' opacity='0.09'%3E%3Cpolygon points='60,10 70,30 90,30 75,45 80,68 60,55 40,68 45,45 30,30 50,30'/%3E%3Cpolygon points='60,18 67,34 85,34 71,44 76,62 60,52 44,62 49,44 35,34 53,34' stroke-width='0.2' opacity='0.5'/%3E%3Cline x1='60' y1='0' x2='60' y2='120'/%3E%3Cline x1='0' y1='60' x2='120' y2='60'/%3E%3Cline x1='0' y1='0' x2='120' y2='120'/%3E%3Cline x1='120' y1='0' x2='0' y2='120'/%3E%3Ccircle cx='60' cy='60' r='28' stroke-width='0.3' opacity='0.4'/%3E%3Ccircle cx='60' cy='60' r='4' stroke-width='0.4'/%3E%3Cpolygon points='60,32 68,52 90,52 73,64 80,86 60,73 40,86 47,64 30,52 52,52' stroke-width='0.2' opacity='0.3'/%3E%3C/g%3E%3C/pattern%3E%3C/defs%3E%3Crect width='120' height='120' fill='url(%23vc-geo-001)'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 0;
}

/* ══════════════════════════════════════════
   KEYFRAME ANIMATIONS
══════════════════════════════════════════ */
@keyframes fadeUp { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: translateY(0); } }
@keyframes patternReveal { 0% { opacity: 0; transform: translateX(-8px); border-color: transparent; } 60% { border-color: var(--gold); } 100% { opacity: 1; transform: translateX(0); } }
@keyframes barGrow { from { width: 0%; } }
@keyframes scoreReveal { from { opacity: 0; transform: scale(0.85); } to { opacity: 1; transform: scale(1); } }
@keyframes borderPulse { 0%, 100% { box-shadow: 0 0 0px rgba(201,168,76,0); } 50% { box-shadow: 0 0 18px rgba(201,168,76,0.25); } }
@keyframes threatSlide { from { opacity: 0; transform: translateX(-12px); } to { opacity: 1; transform: translateX(0); } }
@keyframes pulse-dot { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }

/* ══════════════════════════════════════════
   SCROLLBAR
══════════════════════════════════════════ */
::-webkit-scrollbar { width: 3px; height: 3px; }
::-webkit-scrollbar-track { background: var(--bg-void); }
::-webkit-scrollbar-thumb { background: var(--gold-dim); border-radius: 2px; }

/* ══════════════════════════════════════════
   STREAMLIT CHROME FIX (RESPONSIVENESS)
══════════════════════════════════════════ */
/* Hide the Main Menu and Footer, but KEEP the Header for toggle accessibility */
#MainMenu, footer { visibility: hidden; }

/* Make the top header transparent to blend with design */
[data-testid="stHeader"] {
    background-color: transparent !important;
}

/* Style the Sidebar Toggles to VelvetCodex Gold */
[data-testid="collapsedControl"], 
[data-testid="collapsedControl"] svg {
    color: var(--gold) !important;
    fill: var(--gold) !important;
}

.block-container {
    padding-top: 1.8rem !important;
    padding-bottom: 3rem !important;
    animation: fadeUp 0.5s ease both;
}

/* Mobile-Specific Overrides */
@media (max-width: 768px) {
    .block-container {
        padding-top: 3.5rem !important;
        padding-left: 1.2rem !important;
        padding-right: 1.2rem !important;
    }
    .score-num { font-size: 2rem !important; }
    .vc-wordmark { font-size: 1.1rem !important; }
}

/* ══════════════════════════════════════════
   TYPOGRAPHY
══════════════════════════════════════════ */
h1, h2, h3 { font-family: var(--font-d); color: var(--gold); letter-spacing: 0.06em; }

/* ══════════════════════════════════════════
   SIDEBAR
══════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: var(--bg-deep) !important;
    border-right: 1px solid var(--gold-border) !important;
    position: relative;
}
[data-testid="stSidebar"]::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, var(--gold) 50%, transparent); z-index: 10;
}
[data-testid="stSidebar"] > div { animation: fadeUp 0.4s ease both; }

/* ══════════════════════════════════════════
   COMPONENTS (CARDS, BUTTONS, FORMS)
══════════════════════════════════════════ */
.vc-wordmark { font-family: var(--font-d); font-size: 1.3rem; font-weight: 700; color: var(--gold); letter-spacing: 0.18em; text-transform: uppercase; line-height: 1; }
.vc-wordmark-sub { font-family: var(--font-m); font-size: 0.58rem; color: var(--text-muted); letter-spacing: 0.22em; text-transform: uppercase; margin-top: 4px; }
.vc-header { font-family: var(--font-d); font-size: 0.7rem; letter-spacing: 0.28em; text-transform: uppercase; color: var(--gold); border-bottom: 1px solid var(--gold-border); padding-bottom: 8px; margin-bottom: 18px; animation: fadeUp 0.4s ease both; }

.vc-card { background: var(--bg-card); border: 1px solid rgba(201,168,76,0.14); border-radius: 3px; padding: 18px 22px; position: relative; overflow: hidden; animation: fadeUp 0.5s ease both; }
.vc-card::after { content: ''; position: absolute; top: 0; left: 0; width: 2px; height: 100%; background: linear-gradient(180deg, var(--gold) 0%, transparent 70%); }

.pattern-card { background: linear-gradient(130deg, rgba(201,168,76,0.09) 0%, var(--bg-card) 55%); border: 1px solid var(--gold-border); border-radius: 3px; padding: 14px 18px; margin: 10px 0 14px 0; position: relative; overflow: hidden; animation: patternReveal 0.5s cubic-bezier(0.16,1,0.3,1) both; }
.p-label { font-family: var(--font-m); font-size: 0.58rem; color: var(--text-muted); letter-spacing: 0.18em; text-transform: uppercase; display: block; margin-bottom: 5px; }
.p-arabic { font-family: var(--font-a); font-size: 1.55rem; direction: rtl; display: block; line-height: 1.3; margin-bottom: 3px; }
.p-paradigm { font-family: var(--font-m); font-size: 0.68rem; letter-spacing: 0.1em; text-transform: uppercase; }

.score-block { background: var(--bg-card); border: 1px solid rgba(201,168,76,0.12); border-radius: 3px; padding: 18px 20px 16px 20px; margin-bottom: 12px; animation: fadeUp 0.55s ease 0.1s both; }
.score-num { font-family: var(--font-d); font-size: 2.6rem; color: var(--gold); line-height: 1; animation: scoreReveal 0.4s ease 0.2s both; }
.score-num span { font-size: 1rem; color: var(--text-muted); }
.score-lbl { font-family: var(--font-m); font-size: 0.6rem; color: var(--text-muted); letter-spacing: 0.15em; text-transform: uppercase; margin-bottom: 18px; margin-top: 2px; }
.bar-row { display: flex; align-items: center; gap: 10px; margin: 7px 0; }
.bar-lbl { font-family: var(--font-m); font-size: 0.6rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.07em; width: 74px; flex-shrink: 0; }
.bar-track { flex: 1; height: 3px; background: var(--bg-raised); border-radius: 2px; overflow: hidden; }
.bar-fill { height: 3px; border-radius: 2px; animation: barGrow 0.9s cubic-bezier(0.16,1,0.3,1) both; }
.bar-val { font-family: var(--font-m); font-size: 0.6rem; color: var(--text-muted); width: 36px; text-align: right; flex-shrink: 0; }
.critique-line { font-family: var(--font-m); font-style: italic; font-size: 0.68rem; color: var(--text-muted); border-left: 2px solid var(--gold-border); padding-left: 10px; margin-top: 14px; line-height: 1.6; }

.stButton > button { background: transparent !important; border: 1px solid var(--gold) !important; color: var(--gold) !important; font-family: var(--font-d) !important; font-size: 0.72rem !important; letter-spacing: 0.22em !important; text-transform: uppercase !important; padding: 11px 22px !important; border-radius: 2px !important; transition: background 0.25s, box-shadow 0.25s, transform 0.15s !important; width: 100%; }
.stButton > button:hover { background: var(--gold-glow) !important; box-shadow: 0 0 22px rgba(201,168,76,0.2) !important; transform: translateY(-1px) !important; }
.stButton > button:active { transform: translateY(0px) !important; box-shadow: 0 0 8px rgba(201,168,76,0.1) !important; }
.stButton > button:focus { animation: borderPulse 1.2s ease 2 !important; outline: none !important; }

.stDownloadButton > button { background: transparent !important; border: 1px solid var(--text-dim) !important; color: var(--text-muted) !important; font-family: var(--font-m) !important; font-size: 0.65rem !important; letter-spacing: 0.1em !important; border-radius: 2px !important; transition: border-color 0.2s, color 0.2s !important; }
.stDownloadButton > button:hover { border-color: var(--gold-border) !important; color: var(--gold) !important; }

.stTextArea textarea { background: var(--bg-input) !important; border: 1px solid var(--text-dim) !important; border-radius: 3px !important; color: var(--text) !important; font-family: var(--font-m) !important; font-size: 0.82rem !important; line-height: 1.75 !important; caret-color: var(--gold) !important; transition: border-color 0.2s, box-shadow 0.2s !important; }
.stTextArea textarea:focus { border-color: var(--gold-border) !important; box-shadow: 0 0 0 1px var(--gold-border), inset 0 0 20px var(--gold-faint) !important; outline: none !important; }
.stTextArea textarea::placeholder { color: var(--text-dim) !important; }

.stSelectbox > div > div { background: var(--bg-input) !important; border-color: var(--text-dim) !important; color: var(--text) !important; font-family: var(--font-m) !important; font-size: 0.78rem !important; border-radius: 3px !important; }
.stRadio > div { font-family: var(--font-m) !important; font-size: 0.75rem !important; }
.stRadio label { color: var(--text-muted) !important; }

/* ══════════════════════════════════════════
   TABS (Hardened for Mobile)
══════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] { 
    background: transparent !important; 
    border-bottom: 1px solid var(--text-dim) !important; 
    gap: 0 !important;
    display: flex !important;
    flex-wrap: wrap !important; /* Forces tabs to wrap instead of scroll */
}

.stTabs [data-baseweb="tab"] {
    font-family: var(--font-m) !important; 
    font-size: 0.65rem !important;
    letter-spacing: 0.14em !important; 
    text-transform: uppercase !important;
    color: var(--text-muted) !important; 
    background: transparent !important;
    border: none !important; 
    border-bottom: 2px solid transparent !important;
    padding: 10px 12px !important; /* Reduced from 18px to save space */
    transition: color 0.2s !important;
    white-space: nowrap !important;
}

/* ══════════════════════════════════════════
   STREAMLIT CHROME & RESPONSIVENESS FIX
══════════════════════════════════════════ */
#MainMenu, footer { visibility: hidden; }

[data-testid="stHeader"] { background-color: transparent !important; }

[data-testid="collapsedControl"], [data-testid="collapsedControl"] svg {
    color: var(--gold) !important;
    fill: var(--gold) !important;
}

.block-container {
    max-width: 100vw !important; /* Strictly prevents horizontal scroll */
    overflow-x: hidden !important;
    padding-top: 1.8rem !important;
    padding-bottom: 3rem !important;
    animation: fadeUp 0.5s ease both;
}

/* Mobile-Specific Overrides (The Final Alignment) */
@media (max-width: 768px) {
    .block-container {
        padding-top: 3.5rem !important;
        padding-left: 0.8rem !important; /* Tighter margins for mobile */
        padding-right: 0.8rem !important;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 8px !important; /* Even tighter padding on tiny screens */
        font-size: 0.58rem !important; /* Slightly smaller text for fit */
    }
    .score-num { font-size: 2rem !important; }
    .vc-wordmark { font-size: 1.1rem !important; }
    
    /* Ensure code blocks and cards don't force width */
    .vc-card, [data-testid="stCode"] {
        width: 100% !important;
        margin-left: 0 !important;
        margin-right: 0 !important;
    }
}

[data-testid="stCode"] > div { background: var(--bg-input) !important; border: 1px solid var(--text-dim) !important; border-radius: 3px !important; }
code { font-family: var(--font-m) !important; color: var(--gold) !important; font-size: 0.78rem !important; }

details { background: var(--bg-card) !important; border: 1px solid var(--text-dim) !important; border-radius: 3px !important; margin-bottom: 6px !important; transition: border-color 0.2s !important; }
details:hover { border-color: var(--gold-border) !important; }
details summary { font-family: var(--font-m) !important; font-size: 0.7rem !important; color: var(--text-muted) !important; letter-spacing: 0.08em !important; padding: 10px 14px !important; }

[data-testid="stMetricValue"] { font-family: var(--font-d) !important; color: var(--gold) !important; font-size: 1.6rem !important; }
[data-testid="stMetricLabel"] { font-family: var(--font-m) !important; font-size: 0.58rem !important; letter-spacing: 0.12em !important; text-transform: uppercase !important; color: var(--text-muted) !important; }

hr { border: none !important; border-top: 1px solid var(--text-dim) !important; margin: 18px 0 !important; }
.stToggle label span { font-family: var(--font-m) !important; font-size: 0.73rem !important; color: var(--text-muted) !important; }
.stSpinner > div { border-top-color: var(--gold) !important; }
.stAlert { border-radius: 3px !important; font-family: var(--font-m) !important; font-size: 0.75rem !important; }
label[data-testid="stWidgetLabel"] p, .stSelectbox label, .stRadio label span { font-family: var(--font-m) !important; font-size: 0.65rem !important; letter-spacing: 0.13em !important; text-transform: uppercase !important; color: var(--text-muted) !important; }

.islamic-badge { font-family: var(--font-m); font-size: 0.63rem; color: #6ee7b7; background: rgba(16,185,129,0.07); border: 1px solid rgba(16,185,129,0.22); border-radius: 3px; padding: 9px 12px; letter-spacing: 0.05em; margin-top: 8px; line-height: 1.7; animation: fadeUp 0.3s ease both; }
.char-counter { font-family: var(--font-m); font-size: 0.62rem; text-align: right; letter-spacing: 0.06em; margin-top: -6px; margin-bottom: 10px; transition: color 0.3s; }
.threat-entry { font-family: var(--font-m); font-size: 0.7rem; color: #FC8181; background: var(--danger-glow); border-left: 2px solid var(--danger); padding: 10px 14px; border-radius: 0 3px 3px 0; margin-bottom: 7px; letter-spacing: 0.04em; animation: threatSlide 0.35s ease both; }
.map-entry { background: var(--bg-card); border: 1px solid rgba(201,168,76,0.11); border-radius: 3px; padding: 18px 22px; margin-bottom: 10px; transition: border-color 0.25s, background 0.25s; animation: fadeUp 0.4s ease both; }
.map-entry:hover { border-color: var(--gold-border); background: linear-gradient(130deg, rgba(201,168,76,0.05) 0%, var(--bg-card) 50%); }
.map-arabic { font-family: var(--font-a); font-size: 1.35rem; direction: rtl; line-height: 1.3; margin-bottom: 3px; }
.map-paradigm { font-family: var(--font-m); font-size: 0.62rem; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 10px; opacity: 0.85; }
.map-instruction { font-family: var(--font-m); font-size: 0.7rem; color: var(--text-muted); line-height: 1.75; border-top: 1px solid var(--text-dim); padding-top: 11px; margin-top: 8px; }
.trigger-chip { display: inline-block; font-family: var(--font-a); font-size: 0.78rem; background: rgba(201,168,76,0.07); border: 1px solid var(--gold-border); border-radius: 2px; padding: 2px 8px; margin: 2px; direction: rtl; color: var(--gold); transition: background 0.2s; }
.trigger-chip:hover { background: rgba(201,168,76,0.15); }
.arc-meta { font-family: var(--font-m); font-size: 0.6rem; color: var(--text-muted); letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 6px; }
.status-dot { display: inline-block; width: 5px; height: 5px; background: var(--gold); border-radius: 50%; margin-right: 7px; animation: pulse-dot 2.5s ease infinite; vertical-align: middle; }
.status-dot.green { background: #27AE60; }
.status-dot.red   { background: var(--danger); }

/* ══════════════════════════════════════════
   RTL MODE — Arabic UI direction
   Applied by injecting class="rtl-mode" on
   the stApp element via st.markdown JS trick.
   All text flips to right-to-left.
   Sidebar moves to right side.
══════════════════════════════════════════ */
.rtl-mode {
    direction: rtl !important;
    text-align: right !important;
    font-family: var(--font-a) !important;
}
.rtl-mode .vc-header,
.rtl-mode .vc-wordmark,
.rtl-mode .vc-wordmark-sub,
.rtl-mode .score-lbl,
.rtl-mode .bar-lbl,
.rtl-mode .p-label,
.rtl-mode .p-paradigm,
.rtl-mode .arc-meta {
    direction: rtl !important;
    text-align: right !important;
    font-family: var(--font-a) !important;
    letter-spacing: 0 !important;
}
.rtl-mode .stTextArea textarea,
.rtl-mode .stSelectbox > div > div,
.rtl-mode label {
    direction: rtl !important;
    text-align: right !important;
    font-family: var(--font-a) !important;
}
.rtl-mode [data-testid="stSidebar"] {
    right: 0 !important;
    left: auto !important;
}

</style>
"""