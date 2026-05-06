"""
ui/styles.py — InkOS Design System
==========================================
The full CSS string exported as a single constant.
Integrated Ghost Menu and Horizontal Switcher modules.
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
* { cursor: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24'%3E%3Cline x1='12' y1='2' x2='12' y2='10' stroke='%23C9A84C' stroke-width='1.5'/%3E%3Cline x1='12' y1='14' x2='12' y2='22' stroke='%23C9A84C' stroke-width='1.5'/%3E%3Cline x1='2' y1='12' x2='10' y2='12' stroke='%23C9A84C' stroke-width='1.5'/%3E%3Cline x1='14' y1='12' x2='22' y2='12' stroke='%23C9A84C' stroke-width='1.5'/%3E%3Ccircle cx='12' cy='12' r='2' fill='none' stroke='%23C9A84C' stroke-width='1'/%3E%3C/svg%3E") 12 12, crosshair !important; }
a, button, [role="button"], select, input, textarea, label { cursor: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24'%3E%3Cline x1='12' y1='2' x2='12' y2='10' stroke='%23C9A84C' stroke-width='1.5'/%3E%3Cline x1='12' y1='14' x2='12' y2='22' stroke='%23C9A84C' stroke-width='1.5'/%3E%3Cline x1='2' y1='12' x2='10' y2='12' stroke='%23C9A84C' stroke-width='1.5'/%3E%3Cline x1='14' y1='12' x2='22' y2='12' stroke='%23C9A84C' stroke-width='1.5'/%3E%3Ccircle cx='12' cy='12' r='2' fill='none' stroke='%23C9A84C' stroke-width='1.5'/%3E%3C/svg%3E") 12 12, pointer !important; }

/* ══════════════════════════════════════════
   ARABIC GEOMETRIC BACKGROUND
══════════════════════════════════════════ */
.stApp::before {
    content: ''; position: fixed; inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120'%3E%3Cdefs%3E%3Cpattern id='vc-geo-001' x='0' y='0' width='120' height='120' patternUnits='userSpaceOnUse'%3E%3Cg fill='none' stroke='%23C9A84C' stroke-width='0.4' opacity='0.09'%3E%3Cpolygon points='60,10 70,30 90,30 75,45 80,68 60,55 40,68 45,45 30,30 50,30'/%3E%3Cpolygon points='60,18 67,34 85,34 71,44 76,62 60,52 44,62 49,44 35,34 53,34' stroke-width='0.2' opacity='0.5'/%3E%3Cline x1='60' y1='0' x2='60' y2='120'/%3E%3Cline x1='0' y1='60' x2='120' y2='60'/%3E%3Cline x1='0' y1='0' x2='120' y2='120'/%3E%3Cline x1='120' y1='0' x2='0' y2='120'/%3E%3Ccircle cx='60' cy='60' r='28' stroke-width='0.3' opacity='0.4'/%3E%3Ccircle cx='60' cy='60' r='4' stroke-width='0.4'/%3E%3Cpolygon points='60,32 68,52 90,52 73,64 80,86 60,73 40,86 47,64 30,52 52,52' stroke-width='0.2' opacity='0.3'/%3E%3C/g%3E%3C/pattern%3E%3C/defs%3E%3Crect width='120' height='120' fill='url(%23vc-geo-001)'/%3E%3C/svg%3E");
    pointer-events: none; z-index: 0;
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
   SCROLLBAR & HEADER CHROME
══════════════════════════════════════════ */
::-webkit-scrollbar { width: 3px; height: 3px; }
::-webkit-scrollbar-track { background: var(--bg-void); }
::-webkit-scrollbar-thumb { background: var(--gold-dim); border-radius: 2px; }

header[data-testid="stHeader"] { position: fixed !important; top: 0 !important; z-index: 9999 !important; background-color: transparent !important; }
#MainMenu, footer { visibility: hidden; }

[data-testid="collapsedControl"], [data-testid="collapsedControl"] svg {
    color: var(--gold) !important; fill: var(--gold) !important;
}

.block-container {
    padding-top: 4rem !important;
    padding-bottom: 3rem !important;
    max-width: 100vw !important; 
    overflow-x: hidden !important;
    animation: fadeUp 0.5s ease both;
}

/* ══════════════════════════════════════════
   GHOST MENU & SIDEBAR OVERHAUL (INTEGRATED)
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

/* LOGO WORDMARK */
.sidebar-logo-box {
    background: linear-gradient(135deg, rgba(201,168,76,0.1) 0%, transparent 100%);
    border-left: 2px solid var(--gold);
    padding: 15px; border-radius: 0 8px 8px 0; margin-bottom: 25px;
    box-shadow: 10px 0 20px rgba(0,0,0,0.2);
}
.logo-text {
    font-family: 'Cinzel', serif !important; font-size: 1.4rem !important;
    font-weight: 700 !important; color: var(--gold) !important;
    letter-spacing: 3px !important; text-transform: uppercase;
    line-height: 1; display: flex; align-items: center; gap: 10px;
}
.logo-subtext {
    font-family: 'IBM Plex Mono', monospace !important; font-size: 0.55rem !important;
    color: var(--text-muted) !important; letter-spacing: 2px !important;
    margin-top: 5px; margin-left: 2px;
}

div[data-testid="stSidebarNav"] { display: none; }

/* GHOST RADIO BUTTON CLOAKING (The "Invisible Ink" Method) */
/* 1. Hide the actual input node */
[data-testid="stSidebar"] [role="radiogroup"] input[type="radio"] {
    position: absolute !important; opacity: 0 !important; width: 0 !important; height: 0 !important;
}

/* 2. Hide any generic div/span immediately following the input (BaseWeb's circle drawing) */
[data-testid="stSidebar"] [role="radiogroup"] input[type="radio"] + div,
[data-testid="stSidebar"] [role="radiogroup"] input[type="radio"] + span {
    display: none !important; opacity: 0 !important; width: 0 !important; height: 0 !important; margin: 0 !important; padding: 0 !important; border: none !important;
}

/* 3. Hide any div inside the radio container that DOES NOT contain text (fallback) */
[data-testid="stSidebar"] [role="radiogroup"] [data-baseweb="radio"] > div:not(:last-child) {
    display: none !important; opacity: 0 !important; width: 0 !important; height: 0 !important; margin: 0 !important; padding: 0 !important; border: none !important;
}

/* MENU ITEM CONTAINERS */
[data-testid="stSidebar"] [role="radiogroup"] label[data-baseweb="radio"] {
    width: 100% !important; padding: 10px 14px !important; margin-bottom: 4px !important;
    border-radius: 4px !important; background: transparent !important;
    border-left: 3px solid transparent !important; transition: all 0.2s ease !important;
    cursor: pointer !important; display: block !important;
}

/* TEXT TYPOGRAPHY */
[data-testid="stSidebar"] [role="radiogroup"] label[data-baseweb="radio"] div,
[data-testid="stSidebar"] [role="radiogroup"] label[data-baseweb="radio"] p,
[data-testid="stSidebar"] [role="radiogroup"] label[data-baseweb="radio"] span {
    font-family: 'IBM Plex Mono', monospace !important; font-size: 0.75rem !important;
    letter-spacing: 0.15em !important; color: #85929E !important; 
    text-transform: uppercase !important; margin: 0 !important;
    transition: color 0.2s ease !important; visibility: visible !important; opacity: 1 !important;
}

/* MENU HOVER */
[data-testid="stSidebar"] [role="radiogroup"] label[data-baseweb="radio"]:hover {
    background: rgba(201, 168, 76, 0.04) !important; border-left: 3px solid rgba(201, 168, 76, 0.4) !important;
}
[data-testid="stSidebar"] [role="radiogroup"] label[data-baseweb="radio"]:hover div,
[data-testid="stSidebar"] [role="radiogroup"] label[data-baseweb="radio"]:hover p,
[data-testid="stSidebar"] [role="radiogroup"] label[data-baseweb="radio"]:hover span { 
    color: #E2D5BC !important; 
}

/* MENU ACTIVE */
[data-testid="stSidebar"] [role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) {
    background: linear-gradient(90deg, rgba(201,168,76,0.12) 0%, transparent 100%) !important;
    border-left: 3px solid #C9A84C !important;
}
[data-testid="stSidebar"] [role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) div,
[data-testid="stSidebar"] [role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) p,
[data-testid="stSidebar"] [role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) span {
    color: #C9A84C !important; font-weight: 600 !important; text-shadow: 0 0 10px rgba(201,168,76,0.2) !important;
}

/* ══════════════════════════════════════════
   HORIZONTAL LANGUAGE SWITCHER
══════════════════════════════════════════ */
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"]:has(button) {
    display: flex !important; flex-direction: row !important;
    flex-wrap: nowrap !important; gap: 6px !important;
    align-items: center !important; margin-bottom: 10px !important;
}
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"]:has(button) > div {
    min-width: 0 !important; flex: 1 1 0% !important;
}
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] button {
    height: 36px !important; margin: 0 !important; padding: 0 !important;
    display: flex !important; align-items: center !important; justify-content: center !important;
    border: 1px solid var(--text-dim) !important; background: transparent !important;
    font-family: var(--font-m) !important; font-size: 0.7rem !important; color: var(--text-muted) !important;
    border-radius: 4px !important; transition: none !important; 
}
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] button[kind="primary"] {
    border: 1px solid var(--gold) !important; background: var(--gold-glow) !important; color: var(--gold) !important;
}
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] button[kind="secondary"]:hover {
    border: 1px solid var(--gold-border) !important; color: var(--text) !important;
}

/* ══════════════════════════════════════════
   COMPONENTS (CARDS, METRICS, FORMS)
══════════════════════════════════════════ */
h1, h2, h3 { font-family: var(--font-d); color: var(--gold); letter-spacing: 0.06em; }

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

.stButton > button { background: transparent !important; border: 1px solid var(--gold) !important; color: var(--gold) !important; font-family: var(--font-d) !important; font-size: 0.72rem !important; letter-spacing: 0.22em !important; text-transform: uppercase !important; padding: 11px 22px !important; border-radius: 2px !important; transition: background 0.25s, box-shadow 0.25s, transform 0.15s !important; width: 100%; }
.stButton > button:hover { background: var(--gold-glow) !important; box-shadow: 0 0 22px rgba(201,168,76,0.2) !important; transform: translateY(-1px) !important; }
.stButton > button:active { transform: translateY(0px) !important; box-shadow: 0 0 8px rgba(201,168,76,0.1) !important; }

.stTextArea textarea { background: var(--bg-input) !important; border: 1px solid var(--text-dim) !important; border-radius: 3px !important; color: var(--text) !important; font-family: var(--font-m) !important; font-size: 0.82rem !important; line-height: 1.75 !important; caret-color: var(--gold) !important; transition: border-color 0.2s, box-shadow 0.2s !important; }
.stTextArea textarea:focus { border-color: var(--gold-border) !important; box-shadow: 0 0 0 1px var(--gold-border), inset 0 0 20px var(--gold-faint) !important; outline: none !important; }

.stSelectbox > div > div { background: var(--bg-input) !important; border-color: var(--text-dim) !important; color: var(--text) !important; font-family: var(--font-m) !important; font-size: 0.78rem !important; border-radius: 3px !important; }
.stRadio > div { font-family: var(--font-m) !important; font-size: 0.75rem !important; }
.stRadio label { color: var(--text-muted) !important; }

/* ══════════════════════════════════════════
   MOBILE OVERRIDES & MISC
══════════════════════════════════════════ */
@media (max-width: 768px) {
    .block-container { padding-top: 3.5rem !important; padding-left: 0.8rem !important; padding-right: 0.8rem !important; }
    .score-num { font-size: 2rem !important; }
    .vc-wordmark { font-size: 1.1rem !important; }
    .vc-card, [data-testid="stCode"] { width: 100% !important; margin-left: 0 !important; margin-right: 0 !important; }
}

[data-testid="stMetricValue"] { font-family: var(--font-d) !important; color: var(--gold) !important; font-size: 1.6rem !important; }
[data-testid="stMetricLabel"] { font-family: var(--font-m) !important; font-size: 0.58rem !important; letter-spacing: 0.12em !important; text-transform: uppercase !important; color: var(--text-muted) !important; }

hr { border: none !important; border-top: 1px solid var(--text-dim) !important; margin: 18px 0 !important; }
.status-dot { display: inline-block; width: 5px; height: 5px; background: var(--gold); border-radius: 50%; margin-right: 7px; animation: pulse-dot 2.5s ease infinite; vertical-align: middle; }

/* ══════════════════════════════════════════
   RTL MODE
══════════════════════════════════════════ */
.rtl-mode { direction: rtl !important; text-align: right !important; font-family: var(--font-a) !important; }
.rtl-mode .vc-header, .rtl-mode .vc-wordmark, .rtl-mode .vc-wordmark-sub, .rtl-mode .score-lbl, .rtl-mode .bar-lbl, .rtl-mode .p-label, .rtl-mode .p-paradigm, .rtl-mode .arc-meta { direction: rtl !important; text-align: right !important; font-family: var(--font-a) !important; letter-spacing: 0 !important; }
.rtl-mode .stTextArea textarea, .rtl-mode .stSelectbox > div > div, .rtl-mode label { direction: rtl !important; text-align: right !important; font-family: var(--font-a) !important; }
.rtl-mode [data-testid="stSidebar"] { right: 0 !important; left: auto !important; }
</style>
"""
