"""
ui/styles.py — InkOS Official UX/UI Design System
=================================================
Implements the AmeerInk "Ink and Idea" aesthetic.
Typography: Montserrat (En), Cairo (Ar), Playfair (Serif).
Colors: Driven natively by config.toml for extreme stability.
"""

def get_styles(dark_mode: bool = True) -> str:
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&family=Montserrat:wght@400;500;600;700&family=Playfair+Display:wght@400;600;700&display=swap');

    /* ── BASE TYPOGRAPHY ── */
    html, body, [class*="css"] {
        font-family: 'Montserrat', sans-serif !important;
        color: #FFFFFF !important;
    }

    /* ── NATIVE CONTAINER SOFT BORDERS (Cards & Terminals) ── */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 8px !important;
        border: 1px solid rgba(226, 232, 240, 0.1) !important; /* Adapted from #E2E8F0 Light Gray */
        background-color: #2D3748 !important; /* Secondary Dark */
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2) !important;
        transition: border-color 0.3s ease;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #4299E1 !important; /* Accent Blue Glow */
    }

    /* ── STREAMLIT INPUT ENHANCEMENTS ── */
    .stTextArea textarea, .stTextInput input {
        border-radius: 8px !important;
        border: 1px solid rgba(226, 232, 240, 0.2) !important;
        font-family: 'Montserrat', sans-serif !important;
    }
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #4299E1 !important;
        box-shadow: 0 0 0 1px #4299E1 !important;
    }

    /* ── HIDE STREAMLIT CHROME ── */
    #MainMenu, footer { visibility: hidden !important; }
    .stDeployButton { display: none !important; }

    /* ── BRAND / HERO TYPOGRAPHY ── */
    .brand-title {
        font-family: 'Playfair Display', serif;
        font-size: 2.5rem;
        color: #FFFFFF;
        margin-bottom: -10px;
    }
    .brand-subtitle {
        font-family: 'Montserrat', sans-serif;
        font-size: 0.7rem;
        color: #4299E1; /* Accent Blue */
        letter-spacing: 0.2em;
        text-transform: uppercase;
        font-weight: 600;
    }

    /* ── RTL ARABIC SUPPORT ── */
    .ar-text, [dir="rtl"], [dir="rtl"] * {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl;
        text-align: right;
    }
    
    /* ── BUTTON OVERRIDES ── */
    button[kind="primary"] {
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
    }
    button[kind="primary"]:hover {
        transform: scale(0.98);
        box-shadow: 0 4px 12px rgba(66, 153, 225, 0.3) !important;
    }
    </style>
    """
