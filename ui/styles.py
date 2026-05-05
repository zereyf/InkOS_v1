"""
ui/styles.py — InkOS Design System
==========================================
The full CSS string exported as a single constant.

v5.0: THE PURE PILL ARCHITECTURE
- Nuked deep [data-baseweb] backgrounds using universal selectors.
- Forced gap: 0px to prevent mobile overflow.
- Unified Text Area and Context Actions into a single, seamless component.
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
   THE PURE PILL (ChatGPT-Style Input)
══════════════════════════════════════════ */

/* 1. The Unified Container */
div[data-testid="stHorizontalBlock"]:has(.command-pill-marker) {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    background-color: var(--bg-input) !important;
    border: 1px solid var(--gold-border) !important;
    border-radius: 28px !important;
    align-items: flex-end !important;
    width: 100% !important;
    min-height: 56px !important;
    gap: 0px !important; /* 🚨 PREVENTS BUTTON FROM PUSHING OFF SCREEN */
    padding: 4px 6px 4px 0px !important;
    box-shadow: inset 0 2px 10px rgba(0,0,0,0.3) !important;
    transition: border-color 0.3s ease, box-shadow 0.3s ease !important;
}

div[data-testid="stHorizontalBlock"]:has(.command-pill-marker):focus-within {
    border-color: var(--gold) !important;
    box-shadow: 0 0 12px var(--gold-glow), inset 0 2px 10px rgba(0,0,0,0.5) !important;
}

/* 2. Column Width Locks */
div[data-testid="stHorizontalBlock"]:has(.command-pill-marker) > div[data-testid="column"]:nth-child(1) {
    width: calc(100% - 48px) !important;
    flex: 1 1 auto !important;
    min-width: 0 !important;
    padding: 0 !important; margin: 0 !important;
}

div[data-testid="stHorizontalBlock"]:has(.command-pill-marker) > div[data-testid="column"]:nth-child(2) {
    width: 48px !important;
    flex: 0 0 48px !important;
    min-width: 48px !important;
    padding: 0 !important; margin: 0 !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    padding-bottom: 2px !important;
}

/* 3. 🚨 TOTAL ANNIHILATION OF STREAMLIT'S GREY BOXES 🚨 */
div[data-testid="stHorizontalBlock"]:has(.command-pill-marker) [data-testid="stTextArea"] * {
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

/* 4. Text Area Formatting */
div[data-testid="stHorizontalBlock"]:has(.command-pill-marker) textarea {
    field-sizing: content !important; /* Auto-grows */
    min-height: 48px !important;
    max-height: 250px !important;
    color: var(--text) !important;
    font-family: var(--font-m) !important;
    font-size: 0.88rem !important;
    line-height: 1.6 !important;
    padding: 12px 0px 12px 20px !important;
    margin: 0 !important;
}

div[data-testid="stHorizontalBlock"]:has(.command-pill-marker) textarea:focus { outline: none !important; }
div[data-testid="InputInstructions"] { display: none !important; }

/* 5. Action Buttons (Mic / Send Bolt) */
div[data-testid="stHorizontalBlock"]:has(.command-pill-marker) [data-testid="stAudioInput"] {
    width: 44px !important;
    min-width: 44px !important;
    background: transparent !important;
    border: none !important;
    overflow: hidden !important; /* Hides the native audio timer/waveform */
    margin: 0 !important; padding: 0 !important;
}

div[data-testid="stHorizontalBlock"]:has(.command-pill-marker) button {
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
    margin: 0 !important;
    transition: all 0.2s ease !important;
}

div[data-testid="stHorizontalBlock"]:has(.command-pill-marker) button:hover {
    background: var(--gold-glow) !important;
    border-color: var(--gold) !important;
    transform: scale(1.05) !important;
}

div[data-testid="stHorizontalBlock"]:has(.command-pill-marker) button p {
    font-size: 1.4rem !important;
    margin: 0 !important;
    line-height: 1 !important;
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
