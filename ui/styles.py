"""
ui/styles.py — InkOS Design System
==========================================
v4.0: THE COMMAND PILL & HARDWARE BUTTONS
- Injected 'field-sizing: content' for auto-expanding text areas.
- Created 'Obsidian Pill' aesthetic for the main intent box.
- Stylized circular 'Hardware' buttons for Mic/Execute actions.
- Preserved RTL and Mobile-Responsive logic.
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
   INKOS COMMAND PILL (Text Area Override)
══════════════════════════════════════════ */
div[data-testid="stTextArea"] textarea {
    border-radius: 28px !important;
    background-color: var(--bg-input) !important;
    border: 1px solid var(--gold-border) !important;
    padding: 14px 24px !important;
    field-sizing: content !important; /* MAGIC: Auto-grows vertically */
    min-height: 56px !important;
    max-height: 350px !important;
    color: var(--text) !important;
    font-family: var(--font-m) !important;
    font-size: 0.88rem !important;
    line-height: 1.6 !important;
    caret-color: var(--gold) !important;
    transition: all 0.3s ease !important;
    box-shadow: inset 0 2px 10px rgba(0,0,0,0.5) !important;
}

div[data-testid="stTextArea"] textarea:focus {
    border-color: var(--gold) !important;
    box-shadow: 0 0 15px var(--gold-glow), inset 0 2px 10px rgba(0,0,0,0.5) !important;
    outline: none !important;
}

/* Hide Character Limit Instructions to keep Pill clean */
div[data-testid="InputInstructions"] { display: none !important; }

/* ══════════════════════════════════════════
   HARDWARE BUTTONS (Mic & Execute)
══════════════════════════════════════════ */
/* Targets circular action buttons next to the pill */
.stButton > button, 
[data-testid="stAudioInput"] button {
    border-radius: 50% !important;
    width: 52px !important;
    height: 52px !important;
    min-width: 52px !important;
    padding: 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    background: linear-gradient(145deg, #1e2025, #080c14) !important;
    border: 1px solid var(--gold-border) !important;
    color: var(--gold) !important;
    box-shadow: 4px 4px 10px #03040a, -2px -2px 8px rgba(201,168,76,0.05) !important;
    transition: all 0.25s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
}

.stButton > button:hover {
    border-color: var(--gold) !important;
    box-shadow: 0 0 20px var(--gold-glow) !important;
    transform: scale(1.05) translateY(-2px) !important;
}

/* Lightning Bolt (⚡) button specific font-size */
#btn_exec_pill span {
    font-size: 1.4rem !important;
}

/* ══════════════════════════════════════════
   ARABIC GEOMETRIC BACKGROUND
══════════════════════════════════════════ */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120'%3E%3Cdefs%3E%3Cpattern id='vc-geo-001' x='0' y='0' width='120' height='120' patternUnits='userSpaceOnUse'%3E%3Cg fill='none' stroke='%23C9A84C' stroke-width='0.4' opacity='0.09'%3E%3Cpolygon points='60,10 70,30 90,30 75,45 80,68 60,55 40,68 45,45 30,30 50,30'/%3E%3Ccircle cx='60' cy='60' r='28' stroke-width='0.3' opacity='0.4'/%3E%3C/g%3E%3C/pattern%3E%3C/defs%3E%3Crect width='120' height='120' fill='url(%23vc-geo-001)'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 0;
}

/* ══════════════════════════════════════════
   STREAMLIT CHROME FIXES
══════════════════════════════════════════ */
#MainMenu, footer { visibility: hidden; }

[data-testid="stHeader"] { background-color: transparent !important; }

.block-container {
    padding-top: 1.8rem !important;
    padding-bottom: 3rem !important;
    animation: fadeUp 0.5s ease both;
}

/* Custom Column alignment for the Command Pill */
[data-testid="column"] {
    display: flex;
    align-items: flex-end;
}

/* ══════════════════════════════════════════
   SIDEBAR & TABS
══════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: var(--bg-deep) !important;
    border-right: 1px solid var(--gold-border) !important;
}

.stTabs [data-baseweb="tab-list"] { background: transparent !important; border-bottom: 1px solid var(--text-dim) !important; }
.stTabs [data-baseweb="tab"] { font-family: var(--font-m) !important; font-size: 0.65rem !important; letter-spacing: 0.14em !important; text-transform: uppercase !important; color: var(--text-muted) !important; }

/* ══════════════════════════════════════════
   COMPONENTS (CARDS, METRICS, ETC)
══════════════════════════════════════════ */
.vc-wordmark { font-family: var(--font-d); font-size: 1.3rem; font-weight: 700; color: var(--gold); letter-spacing: 0.18em; text-transform: uppercase; line-height: 1; }
.vc-header { font-family: var(--font-d); font-size: 0.7rem; letter-spacing: 0.28em; text-transform: uppercase; color: var(--gold); border-bottom: 1px solid var(--gold-border); padding-bottom: 8px; margin-bottom: 18px; }
.vc-card { background: var(--bg-card); border: 1px solid rgba(201,168,76,0.14); border-radius: 3px; padding: 18px 22px; position: relative; overflow: hidden; }

.score-block { background: var(--bg-card); border: 1px solid rgba(201,168,76,0.12); border-radius: 3px; padding: 18px 20px; margin-bottom: 12px; }
.score-num { font-family: var(--font-d); font-size: 2.6rem; color: var(--gold); line-height: 1; }

.islamic-badge { font-family: var(--font-m); font-size: 0.63rem; color: #6ee7b7; background: rgba(16,185,129,0.07); border: 1px solid rgba(16,185,129,0.22); border-radius: 3px; padding: 9px 12px; margin-top: 8px; }

/* RTL Support */
.rtl-mode { direction: rtl !important; text-align: right !important; }
.rtl-mode [data-testid="stSidebar"] { right: 0 !important; left: auto !important; }

/* Animations */
@keyframes fadeUp { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: translateY(0); } }

</style>
"""
