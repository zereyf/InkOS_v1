"""
ui/styles.py — InkOS Unified Design System
============================================
Phase 4 UI Rebuild.

Previously two parallel CSS systems existed:
  - ui/style.css  : full tech-noir tokens, fonts, geometric bg — never loaded
  - ui/styles.py  : minimal Montserrat/blue theme — applied everywhere

This file merges them into one authoritative system applied globally.
Every tab now shares the same design language.

Design tokens (from ui/style.css):
  Backgrounds : --bg-void, --bg-deep, --bg-card, --bg-raised, --bg-input
  Gold system : --gold, --gold-dim, --gold-glow, --gold-border, --gold-faint
  Accents     : --steel, --danger, --success
  Text        : --text, --text-muted, --text-dim
  Typography  : Cinzel (display), IBM Plex Mono (mono), Cairo (Arabic),
                Montserrat (UI), Playfair Display (serif brand)
"""


def get_styles(dark_mode: bool = True) -> str:
    return """
<style>
/* ── FONT IMPORTS ─────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=IBM+Plex+Mono:ital,wght@0,300;0,400;0,500;1,300&family=Cairo:wght@400;600;700&family=Montserrat:wght@400;500;600;700&family=Playfair+Display:wght@400;600;700&family=Noto+Naskh+Arabic:wght@400;600;700&display=swap');

/* ── DESIGN TOKENS ────────────────────────────────────────────────────── */
:root {
    /* Backgrounds */
    --bg-void:     #03040A;
    --bg-deep:     #07090F;
    --bg-card:     #0B1019;
    --bg-raised:   #101520;
    --bg-input:    #080C14;

    /* Gold system */
    --gold:        #C9A84C;
    --gold-dim:    #8A6E2E;
    --gold-glow:   rgba(201,168,76,0.14);
    --gold-border: rgba(201,168,76,0.28);
    --gold-faint:  rgba(201,168,76,0.06);

    /* Accent colours */
    --steel:       #7C9EBF;
    --danger:      #A93226;
    --danger-glow: rgba(169,50,38,0.12);
    --success:     #1E8449;
    --info:        #4299E1;

    /* Text hierarchy */
    --text:        #E2D5BC;
    --text-muted:  #5D6D7E;
    --text-dim:    #2C3545;

    /* Typography stacks */
    --font-d:  'Cinzel', Georgia, serif;
    --font-m:  'IBM Plex Mono', 'Courier New', monospace;
    --font-ui: 'Montserrat', sans-serif;
    --font-a:  'Cairo', 'Noto Naskh Arabic', 'Arial Unicode MS', serif;

    /* Spacing & radius */
    --radius-sm: 2px;
    --radius-md: 4px;
    --radius-lg: 8px;

    /* Borders */
    --border-subtle:  1px solid rgba(255,255,255,0.05);
    --border-gold:    1px solid var(--gold-border);
    --border-steel:   1px solid rgba(124,158,191,0.2);
}

/* ── BASE RESET ────────────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: var(--font-ui) !important;
    color: var(--text) !important;
}

.stApp {
    background-color: var(--bg-void) !important;
    color: var(--text);
    font-family: var(--font-ui);
    font-size: 14px;
}

/* ── GEOMETRIC BACKGROUND ──────────────────────────────────────────────── */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120'%3E%3Cdefs%3E%3Cpattern id='geo' x='0' y='0' width='120' height='120' patternUnits='userSpaceOnUse'%3E%3Cg fill='none' stroke='%23C9A84C' stroke-width='0.4' opacity='0.07'%3E%3Cpolygon points='60,10 70,30 90,30 75,45 80,68 60,55 40,68 45,45 30,30 50,30'/%3E%3Ccircle cx='60' cy='60' r='28' stroke-width='0.3' opacity='0.4'/%3E%3C/g%3E%3C/pattern%3E%3C/defs%3E%3Crect width='120' height='120' fill='url(%23geo)'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 0;
}

/* ── STREAMLIT CHROME REMOVAL ──────────────────────────────────────────── */
#MainMenu, footer, .stDeployButton { display: none !important; }
header[data-testid="stHeader"]     { background: transparent !important; }

/* ── MAIN CONTENT LAYER ────────────────────────────────────────────────── */
.main .block-container {
    position: relative;
    z-index: 1;
    padding-top: 1.5rem !important;
    max-width: 1100px;
}

/* ── SIDEBAR ───────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--bg-deep) !important;
    border-right: 1px solid rgba(201,168,76,0.1) !important;
}
[data-testid="stSidebar"] .block-container {
    padding: 1rem 0.75rem !important;
}

/* ── TYPOGRAPHY ────────────────────────────────────────────────────────── */
h1, h2, h3 {
    font-family: var(--font-d) !important;
    color: var(--text) !important;
    letter-spacing: 0.05em;
}
code, pre {
    font-family: var(--font-m) !important;
    background: var(--bg-raised) !important;
    color: var(--text) !important;
    border-radius: var(--radius-sm) !important;
}

/* Arabic text */
.ar-text, [dir="rtl"], [dir="rtl"] * {
    font-family: var(--font-a) !important;
    direction: rtl;
    text-align: right;
}

/* ── NATIVE CONTAINERS ─────────────────────────────────────────────────── */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--bg-card) !important;
    border: var(--border-subtle) !important;
    border-radius: var(--radius-lg) !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.4) !important;
    transition: border-color 0.2s ease;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: rgba(201,168,76,0.2) !important;
}

/* ── INPUT FIELDS ──────────────────────────────────────────────────────── */
.stTextArea textarea,
.stTextInput input {
    background: var(--bg-input) !important;
    color: var(--text) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: var(--radius-md) !important;
    font-family: var(--font-ui) !important;
    font-size: 13px !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
.stTextArea textarea:focus,
.stTextInput input:focus {
    border-color: var(--gold-border) !important;
    box-shadow: 0 0 0 1px var(--gold-dim) !important;
    outline: none !important;
}
.stTextArea label,
.stTextInput label {
    color: var(--text-muted) !important;
    font-family: var(--font-m) !important;
    font-size: 11px !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase;
}

/* ── BUTTONS ───────────────────────────────────────────────────────────── */
button[kind="primary"],
div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, rgba(201,168,76,0.15), rgba(201,168,76,0.05)) !important;
    border: 1px solid var(--gold-border) !important;
    color: var(--gold) !important;
    font-family: var(--font-m) !important;
    font-size: 11px !important;
    font-weight: 500 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase;
    border-radius: var(--radius-sm) !important;
    transition: all 0.2s ease !important;
}
button[kind="primary"]:hover,
div.stButton > button[kind="primary"]:hover {
    background: rgba(201,168,76,0.12) !important;
    box-shadow: 0 0 16px rgba(201,168,76,0.15) !important;
    transform: translateY(-1px);
}

div.stButton > button {
    background: rgba(255,255,255,0.02) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    color: var(--text-muted) !important;
    font-family: var(--font-m) !important;
    font-size: 11px !important;
    letter-spacing: 0.08em !important;
    border-radius: var(--radius-sm) !important;
    transition: all 0.2s ease !important;
}
div.stButton > button:hover {
    border-color: rgba(255,255,255,0.15) !important;
    color: var(--text) !important;
    background: rgba(255,255,255,0.04) !important;
}
div.stButton > button:disabled {
    opacity: 0.3 !important;
    cursor: not-allowed !important;
    transform: none !important;
}

/* ── SLIDERS ───────────────────────────────────────────────────────────── */
.stSlider > div > div > div > div {
    background: var(--gold) !important;
}
.stSlider [data-testid="stThumbValue"] {
    color: var(--gold) !important;
    font-family: var(--font-m) !important;
    font-size: 11px !important;
}

/* ── SELECTBOXES ───────────────────────────────────────────────────────── */
.stSelectbox > div > div {
    background: var(--bg-input) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    color: var(--text) !important;
    border-radius: var(--radius-md) !important;
}

/* ── EXPANDERS ─────────────────────────────────────────────────────────── */
.streamlit-expanderHeader {
    background: var(--bg-raised) !important;
    border: var(--border-subtle) !important;
    color: var(--text) !important;
    font-family: var(--font-m) !important;
    font-size: 12px !important;
    border-radius: var(--radius-sm) !important;
}
.streamlit-expanderContent {
    background: var(--bg-card) !important;
    border: var(--border-subtle) !important;
    border-top: none !important;
}

/* ── ALERTS ────────────────────────────────────────────────────────────── */
.stAlert {
    background: var(--bg-raised) !important;
    border-radius: var(--radius-md) !important;
    font-family: var(--font-m) !important;
    font-size: 12px !important;
}

/* ── SHARED COMPONENT CLASSES (used across tabs) ──────────────────────── */

/* Section header */
.vc-header {
    display: flex;
    align-items: center;
    gap: 10px;
    font-family: var(--font-m);
    font-size: 0.7rem;
    color: var(--gold);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    border-bottom: 1px solid rgba(201,168,76,0.15);
    padding-bottom: 12px;
    margin-bottom: 20px;
}

/* Status dot */
.status-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--gold);
    box-shadow: 0 0 6px var(--gold);
    display: inline-block;
    flex-shrink: 0;
}

/* Generic card */
.vc-card {
    background: var(--bg-card);
    border: var(--border-subtle);
    border-radius: var(--radius-md);
    padding: 16px 18px;
    margin-bottom: 12px;
    transition: border-color 0.2s ease;
}
.vc-card:hover {
    border-color: rgba(201,168,76,0.12);
}

/* Terminal code block */
.vc-terminal {
    background: #000;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: var(--radius-sm);
    padding: 14px 16px;
    font-family: var(--font-m);
    font-size: 12px;
    color: #4CAF9A;
    line-height: 1.6;
}

/* Score badge */
.score-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 3px 10px;
    border-radius: 100px;
    font-family: var(--font-m);
    font-size: 11px;
    font-weight: 500;
}
.score-high   { background: rgba(30,132,73,0.15);  color: #4CAF9A; border: 1px solid rgba(30,132,73,0.3); }
.score-mid    { background: rgba(201,168,76,0.1);   color: var(--gold); border: var(--gold-border); }
.score-low    { background: rgba(169,50,38,0.1);    color: #E57373; border: 1px solid rgba(169,50,38,0.3); }

/* ── SIDEBAR BRAND COMPONENTS ──────────────────────────────────────────── */
.uplink-bar {
    display: flex;
    justify-content: space-between;
    font-family: var(--font-m);
    font-size: 9px;
    color: var(--text-dim);
    letter-spacing: 0.15em;
    margin-bottom: 10px;
    padding-bottom: 8px;
    border-bottom: var(--border-subtle);
}
.uplink-bar .dot       { font-size: 10px; }
.uplink-bar .dot.active   { color: #4CAF9A; }
.uplink-bar .dot.inactive { color: var(--danger); }

.brand-en      { font-family: var(--font-d); font-size: 1.6rem; color: var(--text); letter-spacing: 3px; line-height: 1; }
.brand-sub     { font-family: var(--font-m); font-size: 8px; color: var(--steel); letter-spacing: 6px; text-transform: uppercase; margin-top: 2px; }
.brand-divider { height: 1px; background: linear-gradient(90deg, var(--gold-border), transparent); margin: 10px 0 6px; }
.brand-ar      { font-family: var(--font-a); font-size: 13px; color: var(--gold); direction: rtl; text-align: right; opacity: 0.7; }

/* ── SIDEBAR NAV ───────────────────────────────────────────────────────── */
.nav-section { margin-top: 12px; }
.nav-group-label {
    font-family: var(--font-m);
    font-size: 9px;
    color: var(--text-dim);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    padding: 8px 4px 4px;
}
.nav-item button {
    background: transparent !important;
    border: none !important;
    color: var(--text-muted) !important;
    text-align: left !important;
    font-family: var(--font-m) !important;
    font-size: 11px !important;
    letter-spacing: 0.06em !important;
    padding: 6px 8px !important;
    border-radius: var(--radius-sm) !important;
    width: 100% !important;
    transition: all 0.15s ease !important;
}
.nav-item button:hover {
    background: rgba(255,255,255,0.03) !important;
    color: var(--text) !important;
}
.nav-active button {
    background: var(--gold-faint) !important;
    border-left: 2px solid var(--gold) !important;
    color: var(--gold) !important;
}
.nav-locked {
    opacity: 0.4;
    pointer-events: none;
}
.nav-locked-label {
    font-family: var(--font-m);
    font-size: 9px;
    color: var(--text-dim);
    letter-spacing: 0.1em;
    padding: 2px 8px 6px;
}

/* ── SIDEBAR STATS ─────────────────────────────────────────────────────── */
.stats-card {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1px;
    background: rgba(255,255,255,0.04);
    border: var(--border-subtle);
    border-radius: var(--radius-md);
    overflow: hidden;
    margin: 10px 0;
}
.stat-item {
    background: var(--bg-card);
    padding: 8px 6px;
    text-align: center;
}
.stat-value {
    display: block;
    font-family: var(--font-d);
    font-size: 1.1rem;
    color: var(--text);
    line-height: 1;
    margin-bottom: 2px;
}
.stat-label {
    display: block;
    font-family: var(--font-m);
    font-size: 8px;
    color: var(--text-dim);
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

/* ── SIDEBAR INTEL CARD ────────────────────────────────────────────────── */
.intel-card {
    background: var(--bg-card);
    border: var(--border-subtle);
    border-top: 2px solid var(--steel);
    border-radius: 0 0 var(--radius-md) var(--radius-md);
    padding: 10px 12px;
    margin-top: 8px;
}
.intel-title {
    font-family: var(--font-m);
    font-size: 9px;
    color: var(--steel);
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.intel-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 4px;
}
.intel-key { font-family: var(--font-m); font-size: 9px; color: var(--text-dim); letter-spacing: 0.08em; }
.intel-val { font-family: var(--font-m); font-size: 10px; color: var(--text-muted); max-width: 120px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

/* ── IDENTITY CARD ─────────────────────────────────────────────────────── */
.identity-card {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 12px;
    background: var(--bg-card);
    border: var(--border-subtle);
    border-radius: var(--radius-md);
    margin-bottom: 10px;
}
.avatar {
    width: 28px; height: 28px;
    background: linear-gradient(135deg, var(--gold-dim), var(--gold));
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-family: var(--font-d); font-size: 12px; color: #000;
    font-weight: 700; flex-shrink: 0;
}
.identity-card .name  { font-family: var(--font-m); font-size: 11px; color: var(--text); flex: 1; }
.identity-card .logout { font-size: 14px; color: var(--text-dim); cursor: pointer; }

/* ── SIDEBAR SECTION LABEL ─────────────────────────────────────────────── */
.sidebar-section-label {
    font-family: var(--font-m);
    font-size: 9px;
    color: var(--text-dim);
    letter-spacing: 0.15em;
    text-transform: uppercase;
    padding: 10px 0 4px;
}

/* ── WORKSPACE SPECIFIC ────────────────────────────────────────────────── */
.ws-panel {
    background: var(--bg-card);
    border: var(--border-subtle);
    border-radius: var(--radius-lg);
    padding: 20px;
    margin-bottom: 16px;
    position: relative;
}
.ws-panel-label {
    font-family: var(--font-m);
    font-size: 9px;
    color: var(--text-dim);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 10px;
}
.ws-output-panel {
    background: var(--bg-card);
    border: var(--border-subtle);
    border-top: 2px solid var(--gold-dim);
    border-radius: 0 0 var(--radius-lg) var(--radius-lg);
    padding: 20px;
}

/* Audit score strip */
.audit-strip {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 10px 14px;
    background: rgba(0,0,0,0.3);
    border: var(--border-subtle);
    border-radius: var(--radius-md);
    margin-bottom: 14px;
    flex-wrap: wrap;
}
.audit-main-score {
    font-family: var(--font-d);
    font-size: 1.4rem;
    line-height: 1;
}
.audit-sub {
    font-family: var(--font-m);
    font-size: 10px;
    color: var(--text-muted);
    letter-spacing: 0.06em;
}
.audit-dim-label {
    font-family: var(--font-m);
    font-size: 9px;
    color: var(--text-dim);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 2px;
}
.audit-dim-bar {
    height: 3px;
    border-radius: 1px;
    background: rgba(255,255,255,0.05);
    width: 80px;
    overflow: hidden;
}
.audit-dim-fill {
    height: 100%;
    border-radius: 1px;
    background: var(--gold);
}

/* Example chips */
.example-chip {
    display: inline-block;
    padding: 4px 10px;
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 100px;
    font-family: var(--font-m);
    font-size: 10px;
    color: var(--text-muted);
    cursor: pointer;
    transition: all 0.15s ease;
    white-space: nowrap;
}
.example-chip:hover {
    border-color: var(--gold-border);
    color: var(--gold);
}

/* Routing tag */
.routing-tag {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 2px 8px;
    background: rgba(124,158,191,0.08);
    border: 1px solid rgba(124,158,191,0.2);
    border-radius: 100px;
    font-family: var(--font-m);
    font-size: 10px;
    color: var(--steel);
}

/* Maintenance lock */
.maintenance-lock {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 80vh;
    font-family: var(--font-m);
    font-size: 1.2rem;
    color: var(--danger);
    letter-spacing: 0.3em;
}

/* Scrollbar */
::-webkit-scrollbar            { width: 6px; height: 6px; }
::-webkit-scrollbar-track      { background: var(--bg-deep); }
::-webkit-scrollbar-thumb      { background: rgba(201,168,76,0.3); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--gold-dim); }

/* ── ANIMATIONS ────────────────────────────────────────────────────────── */
@keyframes pulse-gold {
    0%   { box-shadow: 0 0 4px var(--gold); opacity: 0.6; }
    50%  { box-shadow: 0 0 10px var(--gold); opacity: 1; }
    100% { box-shadow: 0 0 4px var(--gold); opacity: 0.6; }
}
@keyframes fade-in {
    from { opacity: 0; transform: translateY(4px); }
    to   { opacity: 1; transform: translateY(0); }
}
.fade-in { animation: fade-in 0.3s ease forwards; }
</style>
"""
