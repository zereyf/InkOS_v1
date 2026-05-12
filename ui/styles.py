"""
ui/styles.py — Tech-Noir Typography & Structure
=================================================
Only injects fonts, RTL support, and native container overrides.
Colors are handled natively by config.toml for maximum stability.
"""

def get_styles(dark_mode: bool = True) -> str:
    # We accept the dark_mode parameter so we don't break your app.py logic,
    # but Tech-Noir natively enforces a dark terminal aesthetic.
    
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;600&family=Amiri:wght@400;700&display=swap');

    /* Base Typography */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
    }

    /* Native Container Soft Borders (For Cards & Terminals) */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 8px !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        transition: border-color 0.3s ease;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: rgba(212, 175, 55, 0.3) !important; /* Soft gold glow */
    }

    /* Streamlit Input Enhancements */
    .stTextArea textarea, .stTextInput input {
        border-radius: 8px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        font-family: 'Inter', sans-serif !important;
    }
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #D4AF37 !important;
        box-shadow: 0 0 0 1px #D4AF37 !important;
    }

    /* Hide Streamlit Chrome */
    #MainMenu, footer { visibility: hidden !important; }
    .stDeployButton { display: none !important; }

    /* Identity / Brand Typography */
    .brand-title {
        font-family: 'Playfair Display', serif;
        font-size: 2.5rem;
        color: #F8F9FA;
        margin-bottom: -10px;
    }
    .brand-subtitle {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        color: #D4AF37;
        letter-spacing: 0.2em;
        text-transform: uppercase;
    }

    /* RTL Arabic Support */
    .ar-text {
        font-family: 'Amiri', serif !important;
        direction: rtl;
        text-align: right;
    }
    </style>
    """
