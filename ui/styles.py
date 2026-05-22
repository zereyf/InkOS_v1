"""
ui/styles.py — InkOS Unified Design System v6.0 (Tech-Noir Edition)
=====================================================================
FIXES:
  - Ripped out corporate/serif fonts (Montserrat, Cinzel, Playfair).
  - Enforced IBM Plex Mono as the primary UI driver for a terminal feel.
  - Background pushed to deep Obsidian (#050505) to match the gateway.
  - Form inputs and buttons squared off and sharpened.
"""

from __future__ import annotations
from functools import lru_cache


def _build_tokens(dark_mode: bool) -> str:
    """Returns the :root CSS variable block for the chosen theme."""
    if dark_mode:
        return """
    /* ── DARK THEME (OBSIDIAN TERMINAL) ─────────────────────────── */
    --bg-void:     #050505;
    --bg-deep:     #0A0A0C;
    --bg-card:     #0D0D12;
    --bg-raised:   #121218;
    --bg-input:    #08080A;

    --gold:        #C9A84C;
    --gold-dim:    #8A6E2E;
    --gold-glow:   rgba(201,168,76,0.15);
    --gold-border: rgba(201,168,76,0.3);
    --gold-faint:  rgba(201,168,76,0.05);

    --steel:       #5D6D7E;
    --steel-glow:  rgba(93,109,126,0.15);
    
    --danger:      #A93226;
    --danger-glow: rgba(169,50,38,0.12);
    --success:     #4CAF9A;
    --info:        #4299E1;

    --text:        #E2D5BC;
    --text-muted:  #7C9EBF;
    --text-dim:    #2C3545;

    --border-subtle:  1px solid rgba(255,255,255,0.06);
    --border-gold:    1px solid rgba(201,168,76,0.3);
    --border-steel:   1px solid rgba(93,109,126,0.25);

    --shadow-card:    0 4px 24px rgba(0,0,0,0.8);
    --shadow-elevated: 0 8px 32px rgba(0,0,0,0.9);

    --scrollbar-thumb: rgba(201,168,76,0.2);
    --scrollbar-track: #050505;
    """
    else:
        return """
    /* ── LIGHT THEME (HIGH-CONTRAST LAB) ────────────────────────── */
    --bg-void:     #F4F5F8;
    --bg-deep:     #ECEEF4;
    --bg-card:     #FFFFFF;
    --bg-raised:   #F9FAFB;
    --bg-input:    #FFFFFF;

    --gold:        #B8952A;
    --gold-dim:    #8A6E20;
    --gold-glow:   rgba(184,149,42,0.12);
    --gold-border: rgba(184,149,42,0.35);
    --gold-faint:  rgba(184,149,42,0.07);

    --steel:       #4A7FA0;
    --danger:      #C0392B;
    --success:     #1A7A42;
    --info:        #2563EB;

    --text:        #0D0D12;
    --text-muted:  #5D6D7E;
    --text-dim:    #A0AEC0;

    --border-subtle:  1px solid rgba(0,0,0,0.08);
    --border-gold:    1px solid rgba(184,149,42,0.35);
    --border-steel:   1px solid rgba(74,127,160,0.25);

    --shadow-card:    0 2px 12px rgba(0,0,0,0.05);
    --shadow-elevated: 0 4px 20px rgba(0,0,0,0.1);

    --scrollbar-thumb: rgba(184,149,42,0.3);
    --scrollbar-track: #ECEEF4;
    """


_BASE_CSS = """
/* ── FONT IMPORTS ─────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Cairo:wght@400;600;700&display=swap');

/* ── DESIGN TOKENS ────────────────────────────────────────────────────── */
:root {
    --font-m:  'IBM Plex Mono', monospace;
    --font-a:  'Cairo', sans-serif;
    --radius-sm: 2px;
    --radius-md: 4px;
    --radius-lg: 6px;
}

/* ── BASE RESET ────────────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: var(--font-m) !important;
    color: var(--text) !important;
}

.stApp {
    background-color: var(--bg-void) !important;
    background-image: radial-gradient(circle at 50% 0%, rgba(201, 168, 76, 0.03) 0%, transparent 70%);
    color: var(--text);
    font-family: var(--font-m);
    font-size: 13px;
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
    border-right: 1px solid rgba(255,255,255,0.03) !important;
}
[data-testid="stSidebar"] .block-container {
    padding: 1.5rem 1rem !important;
}

/* ── TYPOGRAPHY ────────────────────────────────────────────────────────── */
h1, h2, h3, h4, h5, h6 {
    font-family: var(--font-m) !important;
    color: var(--text) !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
code, pre {
    font-family: var(--font-m) !important;
    background: var(--bg-raised) !important;
    color: var(--gold) !important;
    border-radius: var(--radius-sm) !important;
    border: var(--border-subtle) !important;
}

.ar-text, [dir="rtl"], [dir="rtl"] * {
    font-family: var(--font-a) !important;
    direction: rtl;
    text-align: right;
}

/* ── NATIVE CONTAINERS ─────────────────────────────────────────────────── */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--bg-card) !important;
    border: var(--border-subtle) !important;
    border-radius: var(--radius-md) !important;
    box-shadow: var(--shadow-card) !important;
}

/* ── INPUT FIELDS ──────────────────────────────────────────────────────── */
.stTextArea textarea,
.stTextInput input {
    background: rgba(0,0,0,0.3) !important;
    color: var(--text) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: var(--radius-sm) !important;
    font-family: var(--font-m) !important;
    font-size: 13px !important;
    transition: all 0.2s ease;
}
.stTextArea textarea:focus,
.stTextInput input:focus {
    border-color: var(--gold) !important;
    box-shadow: 0 0 10px var(--gold-glow) !important;
    outline: none !important;
}
.stTextArea label,
.stTextInput label {
    color: var(--text-muted) !important;
    font-family: var(--font-m) !important;
    font-size: 10px !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase;
}

/* ── BUTTONS ───────────────────────────────────────────────────────────── */
button[kind="primary"],
div.stButton > button[kind="primary"] {
    background: var(--gold) !important;
    color: #000000 !important;
    font-family: var(--font-m) !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    border-radius: var(--radius-sm) !important;
    border: none !important;
    transition: all 0.2s ease !important;
}
button[kind="primary"]:hover,
div.stButton > button[kind="primary"]:hover {
    background: #E2D5BC !important;
    box-shadow: 0 0 15px var(--gold-glow) !important;
    transform: translateY(-1px);
}

div.stButton > button {
    background: transparent !important;
    border: 1px dashed rgba(255,255,255,0.15) !important;
    color: var(--text-muted) !important;
    font-family: var(--font-m) !important;
    font-size: 10px !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    border-radius: var(--radius-sm) !important;
    transition: all 0.2s ease !important;
}
div.stButton > button:hover {
    border-color: var(--steel) !important;
    color: var(--text) !important;
}

/* ── SLIDERS ───────────────────────────────────────────────────────────── */
.stSlider > div > div > div > div { background: var(--gold) !important; }
.stSlider [data-testid="stThumbValue"] {
    color: var(--gold) !important;
    font-family: var(--font-m) !important;
    font-size: 11px !important;
}

/* ── SELECTBOXES ───────────────────────────────────────────────────────── */
.stSelectbox > div > div {
    background: var(--bg-input) !important;
    border: var(--border-subtle) !important;
    color: var(--text) !important;
    border-radius: var(--radius-sm) !important;
    font-family: var(--font-m) !important;
    font-size: 12px !important;
}

/* ── EXPANDERS ─────────────────────────────────────────────────────────── */
.streamlit-expanderHeader {
    background: var(--bg-raised) !important;
    border: var(--border-subtle) !important;
    color: var(--text) !important;
    font-family: var(--font-m) !important;
    font-size: 11px !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    border-radius: var(--radius-sm) !important;
}
.streamlit-expanderContent {
    background: var(--bg-card) !important;
    border: var(--border-subtle) !important;
    border-top: none !important;
}

/* ── ALERTS ────────────────────────────────────────────────────────────── */
.stAlert {
    background: rgba(0,0,0,0.4) !important;
    border: var(--border-subtle) !important;
    border-radius: var(--radius-sm) !important;
    font-family: var(--font-m) !important;
    font-size: 12px !important;
}

/* ── SHARED COMPONENT CLASSES ─────────────────────────────────────────── */
.score-badge {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 3px 10px; border-radius: 100px;
    font-family: var(--font-m); font-size: 11px; font-weight: 500;
}
.score-high   { background: rgba(76,175,154,0.1); color: var(--success); border: 1px solid rgba(76,175,154,0.3); }
.score-mid    { background: var(--gold-faint); color: var(--gold); border: var(--border-gold); }
.score-low    { background: rgba(169,50,38,0.1); color: var(--danger); border: 1px solid rgba(169,50,38,0.3); }

/* ── SIDEBAR BRAND ─────────────────────────────────────────────────────── */
.uplink-bar {
    display: flex; justify-content: space-between;
    font-family: var(--font-m); font-size: 9px;
    color: var(--text-dim); letter-spacing: 0.15em;
    margin-bottom: 15px; padding-bottom: 8px;
    border-bottom: var(--border-subtle);
}
.uplink-bar .dot.active   { color: var(--success); }
.uplink-bar .dot.inactive { color: var(--danger); }

.brand-en      { font-family: var(--font-m); font-size: 1.4rem; font-weight: 600; color: var(--text); letter-spacing: 0.15em; text-transform: uppercase; line-height: 1; }
.brand-sub     { font-family: var(--font-m); font-size: 8px; color: var(--steel); letter-spacing: 0.2em; text-transform: uppercase; margin-top: 4px; }
.brand-divider { height: 1px; background: linear-gradient(90deg, var(--gold-border), transparent); margin: 12px 0 8px; }
.brand-ar      { font-family: var(--font-a); font-size: 14px; color: var(--gold); direction: rtl; text-align: right; opacity: 0.9; }

/* ── SIDEBAR STATS ─────────────────────────────────────────────────────── */
.stats-card {
    display: grid; grid-template-columns: repeat(3, 1fr);
    gap: 1px; background: rgba(255,255,255,0.03);
    border: var(--border-subtle); border-radius: var(--radius-sm);
    overflow: hidden; margin: 10px 0;
}
.stat-item   { background: var(--bg-card); padding: 10px 6px; text-align: center; }
.stat-value  { display: block; font-family: var(--font-m); font-size: 1rem; color: var(--text); line-height: 1; margin-bottom: 4px; }
.stat-label  { display: block; font-family: var(--font-m); font-size: 8px; color: var(--steel); letter-spacing: 0.1em; text-transform: uppercase; }

/* ── SIDEBAR INTEL CARD ────────────────────────────────────────────────── */
.intel-card {
    background: rgba(0,0,0,0.2); 
    border: var(--border-subtle);
    border-top: 2px solid var(--gold-dim);
    border-radius: 0 0 var(--radius-sm) var(--radius-sm);
    padding: 12px 14px; 
    margin-top: 10px;
}
.intel-title { 
    font-family: var(--font-m); font-size: 9px; color: var(--text-muted); 
    letter-spacing: 0.15em; text-transform: uppercase; margin-bottom: 10px; 
    border-bottom: 1px dashed rgba(255,255,255,0.05); padding-bottom: 6px; 
}
.intel-row   { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.intel-key   { font-family: var(--font-m); font-size: 9px; color: var(--steel); letter-spacing: 0.1em; }
.intel-val   { font-family: var(--font-m); font-size: 10px; color: var(--text); max-width: 120px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

/* ── IDENTITY CARD ─────────────────────────────────────────────────────── */
.identity-card {
    display: flex; align-items: center; gap: 12px;
    padding: 12px;
    background: rgba(0,0,0,0.3); border: var(--border-subtle);
    border-radius: var(--radius-sm); margin-bottom: 10px;
}
.avatar {
    width: 24px; height: 24px;
    background: var(--gold);
    border-radius: 2px;
    display: flex; align-items: center; justify-content: center;
    font-family: var(--font-m); font-size: 12px; color: #000;
    font-weight: 600; flex-shrink: 0;
}
.identity-card .name { font-family: var(--font-m); font-size: 11px; color: var(--text); letter-spacing: 0.05em; flex: 1; }

.sidebar-section-label {
    font-family: var(--font-m); font-size: 9px; color: var(--steel);
    letter-spacing: 0.2em; text-transform: uppercase; padding: 12px 0 6px;
    border-bottom: 1px dashed rgba(255,255,255,0.05); margin-bottom: 10px;
}

/* ── SCROLLBAR ─────────────────────────────────────────────────────────── */
::-webkit-scrollbar            { width: 4px; height: 4px; }
::-webkit-scrollbar-track      { background: var(--scrollbar-track); }
::-webkit-scrollbar-thumb      { background: var(--scrollbar-thumb); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: var(--gold-dim); }
"""

@lru_cache(maxsize=2)
def get_styles(dark_mode: bool = True) -> str:
    token_block = _build_tokens(dark_mode)
    return f"<style>\n:root {{{token_block}}}\n{_BASE_CSS}\n</style>"
