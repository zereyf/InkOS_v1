"""
ui/styles.py — InkOS Design System
==========================================
The full CSS string exported as a single constant.

v7.0: THE LEVITATION OVERRIDE
- Text area acts as the primary pill.
- CSS physically floats the action buttons right over the corner of the text area.
"""

STYLES: str = """
<style>
/* ══════════════════════════════════════════
   FONT IMPORTS & DESIGN TOKENS
══════════════════════════════════════════ */
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=IBM+Plex+Mono:ital,wght@0,300;0,400;0,500;1,300&family=Noto+Naskh+Arabic:wght@400;600;700&display=swap');

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

*, *::before, *::after { box-sizing: border-box; margin: 0; }
.stApp { background-color: var(--bg-void); color: var(--text); font-family: var(--font-m); font-size: 14px; }

/* ══════════════════════════════════════════
   THE LEVITATION PILL (ChatGPT-Style Input)
══════════════════════════════════════════ */

/* 1. TEXT AREA BECOMES THE COMPLETE PILL */
div[data-testid="stTextArea"]:has(textarea[aria-label="intent"]) > div {
    background-color: var(--bg-input) !important;
    border: 1px solid var(--gold-border) !important;
    border-radius: 28px !important;
    box-shadow: inset 0 2px 10px rgba(0,0,0,0.3) !important;
    transition: all 0.3s ease !important;
    overflow: hidden !important;
}

div[data-testid="stTextArea"]:has(textarea[aria-label="intent"]):focus-within > div {
    border-color: var(--gold) !important;
    box-shadow: 0 0 12px var(--gold-glow), inset 0 2px 10px rgba(0,0,0,0.5) !important;
}

/* 2. TEXT AREA FORMATTING (Reserves space for the button) */
div[data-testid="stTextArea"]:has(textarea[aria-label="intent"]) textarea {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 16px 60px 16px 24px !important; /* 🚨 60px padding leaves room for the button */
    field-sizing: content !important; /* Auto-grows as you type */
    min-height: 56px !important;
    max-height: 250px !important;
    color: var(--text) !important;
    font-family: var(--font-m) !important;
    font-size: 0.9rem !important;
    line-height: 1.6 !important;
    margin: 0 !important;
}

div[data-testid="InputInstructions"] { display: none !important; }


/* 3. LEVITATION MECHANICS: Pull the Button UP and RIGHT */
div[data-testid="stAudioInput"],
button[title="Compile Blueprint"] {
    position: relative !important;
    float: right !important;
    top: -50px !important; /* Pulls it UP over the text area */
    right: 8px !important; /* Pulls it IN from the right edge */
    z-index: 100 !important;
    margin-bottom: -44px !important; /* Collapses its physical space so it doesn't leave a gap */
}

/* 4. MIC SPECIFIC FORMATTING */
div[data-testid="stAudioInput"] {
    width: 44px !important;
    height: 44px !important;
    min-width: 44px !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    overflow: hidden !important; /* Hides the waveform and timer */
}

div[data-testid="stAudioInput"] button {
    border-radius: 50% !important;
    width: 44px !important;
    height: 44px !important;
    padding: 0 !important;
    background: linear-gradient(145deg, #1e2025, #080c14) !important;
    border: 1px solid var(--gold-border) !important;
    color: var(--gold) !important;
    box-shadow: 4px 4px 10px #03040a, -2px -2px 8px rgba(201,168,76,0.05) !important;
}

/* 5. EXECUTE BOLT FORMATTING */
button[title="Compile Blueprint"] {
    border-radius: 50% !important;
    width: 44px !important;
    height: 44px !important;
    padding: 0 !important;
    background: linear-gradient(145deg, #1e2025, #080c14) !important;
    border: 1px solid var(--gold-border) !important;
    color: var(--gold) !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-shadow: 4px 4px 10px #03040a, -2px -2px 8px rgba(201,168,76,0.05) !important;
    transition: all 0.2s ease !important;
}

button[title="Compile Blueprint"]:hover,
div[data-testid="stAudioInput"] button:hover {
    background: var(--gold-glow) !important;
    border-color: var(--gold) !important;
    transform: scale(1.05) !important;
}

button[title="Compile Blueprint"] p {
    font-size: 1.4rem !important;
    margin: 0 !important;
    line-height: 1 !important;
}

/* Clears the CSS float so the character counter renders normally */
.char-counter {
    clear: both !important;
    padding-top: 10px !important;
}


/* ══════════════════════════════════════════
   STANDARD COMPONENTS (CARDS, METRICS)
══════════════════════════════════════════ */
.vc-wordmark { font-family: var(--font-d); font-size: 1.3rem; font-weight: 700; color: var(--gold); letter-spacing: 0.18em; text-transform: uppercase; line-height: 1; }
.vc-header { font-family: var(--font-d); font-size: 0.7rem; letter-spacing: 0.28em; text-transform: uppercase; color: var(--gold); border-bottom: 1px solid var(--gold-border); padding-bottom: 8px; margin-bottom: 18px; animation: fadeUp 0.4s ease both; }
.vc-card { background: var(--bg-card); border: 1px solid rgba(201,168,76,0.14); border-radius: 3px; padding: 18px 22px; position: relative; overflow: hidden; animation: fadeUp 0.5s ease both; }
.vc-card::after { content: ''; position: absolute; top: 0; left: 0; width: 2px; height: 100%; background: linear-gradient(180deg, var(--gold) 0%, transparent 70%); }
.score-block { background: var(--bg-card); border: 1px solid rgba(201,168,76,0.12); border-radius: 3px; padding: 18px 20px 16px 20px; margin-bottom: 12px; animation: fadeUp 0.55s ease 0.1s both; }

/* Standard Rectangular Buttons */
.stButton > button:not([title="Compile Blueprint"]) { background: transparent !important; border: 1px solid var(--gold) !important; color: var(--gold) !important; font-family: var(--font-d) !important; font-size: 0.72rem !important; letter-spacing: 0.22em !important; text-transform: uppercase !important; padding: 11px 22px !important; border-radius: 2px !important; transition: background 0.25s, box-shadow 0.25s, transform 0.15s !important; width: 100%; }
.stButton > button:not([title="Compile Blueprint"]):hover { background: var(--gold-glow) !important; box-shadow: 0 0 22px rgba(201,168,76,0.2) !important; transform: translateY(-1px) !important; }

.stDownloadButton > button { background: transparent !important; border: 1px solid var(--text-dim) !important; color: var(--text-muted) !important; font-family: var(--font-m) !important; font-size: 0.65rem !important; border-radius: 2px !important; }
.stDownloadButton > button:hover { border-color: var(--gold-border) !important; color: var(--gold) !important; }

/* ══════════════════════════════════════════
   STREAMLIT CHROME FIX & RESPONSIVENESS
══════════════════════════════════════════ */
#MainMenu, footer { visibility: hidden; }
[data-testid="stHeader"] { background-color: transparent !important; }
[data-testid="collapsedControl"] { color: var(--gold) !important; }

.block-container {
    padding-top: 1.8rem !important;
    padding-bottom: 3rem !important;
    max-width: 100vw !important;
    overflow-x: hidden !important;
}

@media (max-width: 768px) {
    .block-container { padding-top: 3.5rem !important; padding-left: 0.8rem !important; padding-right: 0.8rem !important; }
}

/* RTL Support */
.rtl-mode { direction: rtl !important; text-align: right !important; font-family: var(--font-a) !important; }
.rtl-mode .vc-header, .rtl-mode .vc-wordmark { direction: rtl !important; text-align: right !important; font-family: var(--font-a) !important; letter-spacing: 0 !important; }
.rtl-mode .stTextArea textarea { direction: rtl !important; text-align: right !important; font-family: var(--font-a) !important; }
.rtl-mode [data-testid="stSidebar"] { right: 0 !important; left: auto !important; }
</style>
"""
