STYLES_LIGHT = '''
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&family=IBM+Plex+Sans+Arabic:wght@400;500;600&family=Amiri:wght@400;700&display=swap');

:root {
  --bg:            #F6F5F2; /* Updated to iOS Mockup */
  --bg-secondary:  #F0EEE9;
  --surface:       #FFFFFF;
  --surface-up:    #F5F3EF;
  --surface-card:  #FFFFFF;
  --border:        #E8E4DC;
  --border-gold:   #D4AF3733;
  --border-blue:   #2C3E5022;
  --accent:        #2C3E50;
  --accent-hover:  #1a2530;
  --accent-glow:   #2C3E5015;
  --gold:          #D4AF37;
  --gold-light:    #E8C84A;
  --gold-dim:      #D4AF3715;
  --gold-border:   #D4AF3740;
  --text-1:        #111111; /* Updated to iOS Mockup */
  --text-2:        #7A7A7A; /* Updated to iOS Mockup */
  --text-3:        #A8A095; /* Updated to iOS Mockup */
  --success:       #27AE60;
  --warning:       #F39C12;
  --danger:        #E74C3C;
  --font-serif:    'Playfair Display', Georgia, serif;
  --font-sans:     Inter, sans-serif;
  --font-mono:     'JetBrains Mono', monospace;
  --font-ar:       'IBM Plex Sans Arabic', sans-serif;
  --font-ar-serif: 'Amiri', serif;
  --shadow-sm:     0 2px 10px rgba(0,0,0,0.03); /* Softened */
  --shadow-md:     0 4px 16px rgba(0,0,0,0.05);
  --shadow-lg:     0 10px 30px rgba(0,0,0,0.08); /* Float shadow */
}
</style>
'''

STYLES_DARK = '''
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&family=IBM+Plex+Sans+Arabic:wght@400;500;600&family=Amiri:wght@400;700&display=swap');

:root {
  --bg:            #0f0e17;
  --bg-secondary:  #13121c;
  --surface:       #1a1825;
  --surface-up:    #211f2e;
  --surface-card:  #181622;
  --border:        #ffffff0a;
  --border-gold:   #D4AF3725;
  --border-blue:   #4A90D944;
  --accent:        #4A90D9;
  --accent-hover:  #5BA3E8;
  --accent-glow:   #4A90D920;
  --gold:          #D4AF37;
  --gold-light:    #E8C84A;
  --gold-dim:      #D4AF3712;
  --gold-border:   #D4AF3733;
  --text-1:        #F5F0E8;
  --text-2:        #8a8070;
  --text-3:        #4a4535;
  --success:       #2ECC71;
  --warning:       #F39C12;
  --danger:        #E74C3C;
  --font-serif:    'Playfair Display', Georgia, serif;
  --font-sans:     Inter, sans-serif;
  --font-mono:     'JetBrains Mono', monospace;
  --font-ar:       'IBM Plex Sans Arabic', sans-serif;
  --font-ar-serif: 'Amiri', serif;
  --shadow-sm:     0 1px 4px rgba(0,0,0,.30);
  --shadow-md:     0 4px 16px rgba(0,0,0,.40);
  --shadow-lg:     0 8px 32px rgba(0,0,0,.50);
}
</style>
'''

STYLES_BASE = '''
<style>

/* ── BASE ── */
html, body, [class*="css"] {
  font-family: var(--font-sans) !important;
  color: var(--text-1) !important;
  -webkit-font-smoothing: antialiased;
}

/* ── APP BACKGROUND ── */
.stApp { background: var(--bg) !important; }

/* Arabic ink watermark */
.stApp::after {
  content: 'حبر';
  position: fixed;
  bottom: -20px; right: 16px;
  font: 700 220px var(--font-ar-serif);
  color: var(--gold-dim);
  z-index: 0;
  pointer-events: none;
  user-select: none;
  opacity: .5;
}

/* iOS Watercolor Abstract Background */
.stApp::before {
    content: "";
    position: fixed;
    top: -10%; left: -10%; width: 120%; height: 120%;
    background: radial-gradient(circle at 15% 20%, rgba(168, 160, 149, 0.05) 0%, transparent 40%),
                radial-gradient(circle at 85% 80%, rgba(17, 17, 17, 0.02) 0%, transparent 50%);
    pointer-events: none;
    z-index: 0;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
  background: var(--surface) !important;
  border-right: 1px solid var(--border) !important;
  box-shadow: var(--shadow-sm) !important;
}
[data-testid="stSidebar"] > div { padding-top: 0 !important; }
.block-container,
[data-testid="stSidebar"] .block-container {
  position: relative;
  z-index: 1;
}

/* ── SIDEBAR NAV BUTTONS — slim rows ── */
[data-testid="stSidebar"] .stButton > button {
  background:    transparent !important;
  border:        none !important;
  border-left:   3px solid transparent !important;
  border-radius: 0 8px 8px 0 !important;
  color:         var(--text-2) !important;
  font-size:     13px !important;
  font-weight:   500 !important;
  font-family:   var(--font-sans) !important;
  text-align:    left !important;
  height:        44px !important;
  padding:       0 16px !important;
  width:         100% !important;
  box-shadow:    none !important;
  transition:    all 150ms ease !important;
  margin-bottom: 2px !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
  background:  var(--accent-glow) !important;
  color:       var(--text-1) !important;
  border-left: 3px solid var(--text-3) !important;
}
[data-testid="stSidebar"] .nav-active + div .stButton > button {
  background:  var(--accent-glow) !important;
  border-left: 3px solid var(--accent) !important;
  color:       var(--accent) !important;
  font-weight: 600 !important;
}

/* ── PRIMARY BUTTON — Ink Blue ── */
.stButton > button[kind="primary"] {
  background:     var(--accent) !important;
  color:          #FFFFFF !important;
  border:         none !important;
  border-radius:  12px !important;
  height:         52px !important;
  font-size:      14px !important;
  font-weight:    600 !important;
  font-family:    var(--font-sans) !important;
  letter-spacing: .02em !important;
  box-shadow:     0 4px 16px var(--accent-glow) !important;
  transition:     all 150ms ease !important;
}
.stButton > button[kind="primary"]:hover {
  background: var(--accent-hover) !important;
  box-shadow: 0 6px 24px var(--accent-glow) !important;
  transform:  translateY(-1px) !important;
}
.stButton > button[kind="primary"]:active {
  transform: translateY(0) scale(0.99) !important;
}

/* ── SECONDARY BUTTONS — main area ── */
.main .stButton > button,
section[data-testid="stMain"] .stButton > button {
  background:    var(--surface-up) !important;
  border:        1px solid var(--border) !important;
  border-radius: 10px !important;
  color:         var(--text-2) !important;
  font-size:     13px !important;
  height:        42px !important;
  font-family:   var(--font-sans) !important;
  transition:    all 150ms ease !important;
  box-shadow:    var(--shadow-sm) !important;
}
.main .stButton > button:hover,
section[data-testid="stMain"] .stButton > button:hover {
  background:   var(--accent-glow) !important;
  color:        var(--accent) !important;
  border-color: var(--border-blue) !important;
}

/* ── INPUTS ── */
.stTextArea textarea,
.stTextInput input {
  background:    var(--surface-up) !important;
  border:        1px solid var(--border) !important;
  border-radius: 12px !important;
  color:         var(--text-1) !important;
  font-family:   var(--font-sans) !important;
  font-size:     14px !important;
  transition:    border-color 150ms ease !important;
  caret-color:   var(--accent) !important;
}
.stTextArea textarea:focus,
.stTextInput input:focus {
  border-color: var(--accent) !important;
  box-shadow:   0 0 0 3px var(--accent-glow) !important;
  outline:      none !important;
}
.stTextArea textarea::placeholder,
.stTextInput input::placeholder {
  color: var(--text-3) !important;
}

/* ── DESK INPUT — transparent inside pill (Using :has to fix Streamlit issue) ── */
div[data-testid="stHorizontalBlock"]:has(.input-marker) .stTextArea textarea {
  background:  transparent !important;
  border:      none !important;
  box-shadow:  none !important;
  font-size:   15px !important;
  padding:     8px 4px !important;
  min-height:  44px !important;
  max-height:  100px !important;
  resize:      none !important;
}
div[data-testid="stHorizontalBlock"]:has(.input-marker) .stTextArea textarea:focus {
  border:     none !important;
  box-shadow: none !important;
}

/* ── SELECTBOX ── */
.stSelectbox > div > div {
  background:    var(--surface-up) !important;
  border:        1px solid var(--border) !important;
  border-radius: 10px !important;
  color:         var(--text-1) !important;
}

/* ── LABELS ── */
label, .stTextArea label,
.stTextInput label, .stSelectbox label {
  color:          var(--text-2) !important;
  font-size:      11px !important;
  font-weight:    500 !important;
  letter-spacing: 0.06em !important;
  text-transform: uppercase !important;
}

/* ── CHECKBOX / TOGGLE ── */
.stCheckbox label, .stToggle label {
  color: var(--text-2) !important; font-size: 13px !important;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar       { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 999px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-3); }

/* ── FOCUS ── */
*:focus-visible {
  outline:    none !important;
  box-shadow: 0 0 0 3px var(--accent-glow) !important;
}

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu, footer { visibility: hidden !important; }
.stDeployButton { display: none !important; }

/* ── MAIN LAYOUT (iOS Width Constraint) ── */
.main .block-container {
  padding-bottom: 120px !important; /* Space for Bottom Nav */
  padding-top:    0 !important;
  max-width:      430px !important; /* Mobile width constraint */
  margin:         0 auto !important;
}

/* ── DESK QUICK ACTION PILLS ── */
div[data-testid="column"] .stButton > button {
  background:    var(--surface-card) !important;
  border:        1px solid var(--border) !important;
  border-radius: 999px !important;
  color:         var(--text-2) !important;
  font-size:     13px !important;
  height:        38px !important;
  padding:       0 14px !important;
  transition:    all 150ms ease !important;
  box-shadow:    var(--shadow-sm) !important;
  font-family:   var(--font-sans) !important;
}
div[data-testid="column"] .stButton > button:hover {
  background:   var(--accent-glow) !important;
  color:        var(--accent) !important;
  border-color: var(--border-blue) !important;
}

/* ── BRAND ── */
.uplink-bar {
  font:            11px var(--font-mono);
  color:           var(--text-3);
  display:         flex;
  justify-content: space-between;
  align-items:     center;
  border-bottom:   1px solid var(--border);
  padding:         10px 0 8px;
  margin-bottom:   12px;
}
.dot.active   { color: var(--success); }
.dot.inactive { color: var(--danger); }
.brand-en {
  font:           700 20px var(--font-serif);
  color:          var(--accent);
  margin-bottom:  2px;
}
.brand-sub {
  font:           10px var(--font-mono);
  color:          var(--text-3);
  letter-spacing: .2em;
  margin-bottom:  8px;
}
.brand-divider {
  height:     1px;
  background: linear-gradient(90deg, transparent, var(--accent), transparent);
  margin:     8px 0;
  opacity:    .3;
}
.brand-ar {
  font:        600 22px var(--font-ar-serif);
  text-align:  right;
  color:       var(--text-1);
  line-height: 1.3;
  margin-bottom: 8px;
}

/* ── IDENTITY CARD ── */
.identity-card {
  height:        48px;
  background:    var(--surface-card);
  border:        1px solid var(--border);
  border-radius: 12px;
  padding:       0 14px;
  display:       flex;
  align-items:   center;
  gap:           10px;
  margin-bottom: 4px;
  box-shadow:    var(--shadow-sm);
}
.avatar {
  width:28px; height:28px; border-radius:999px;
  background:var(--accent); color:#fff;
  display:flex; align-items:center; justify-content:center;
  font-size:13px; font-weight:700; flex-shrink:0;
}
.name   { font-size:13px; font-weight:600; color:var(--text-1); }
.logout {
  margin-left:auto; opacity:0; color:var(--text-2);
  font-size:16px; cursor:pointer; transition:opacity 150ms;
}
.identity-card:hover .logout { opacity: 1; }

/* ── STATS CARD ── */
.stats-card {
  background:            var(--surface-card);
  border:                1px solid var(--border);
  border-radius:         12px;
  padding:               14px 16px;
  display:               grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap:                   8px;
  margin:                12px 0;
  box-shadow:            var(--shadow-sm);
}
.stat-item { text-align: center; }
.stat-value {
  font-size:   20px; font-weight:700;
  color:       var(--accent);
  font-family: var(--font-serif);
  display:     block;
}
.stat-label {
  font-size:      9px; color:var(--text-3);
  letter-spacing: 0.12em; text-transform:uppercase;
  margin-top:     2px; display:block;
}

/* ── INTELLIGENCE CARD ── */
.intel-card {
  border-left:   2px solid var(--accent);
  background:    var(--surface-up);
  border-radius: 0 10px 10px 0;
  padding:       10px 14px;
  margin:        8px 0;
}
.intel-title {
  font:10px var(--font-mono); color:var(--accent);
  letter-spacing:.1em; text-transform:uppercase; margin-bottom:8px;
}
.intel-row {
  display:flex; justify-content:space-between;
  align-items:center; margin-bottom:4px;
}
.intel-key { font-size:10px; color:var(--text-3); text-transform:uppercase; }
.intel-val { font-size:12px; color:var(--text-1); font-weight:500; }

/* ── RTL SUPPORT ── */
[dir="rtl"] .brand-ar          { text-align: left; }
[dir="rtl"] .identity-card     { flex-direction: row-reverse; }
[dir="rtl"] .logout            { margin-left: 0; margin-right: auto; }

/* ── BOTTOM NAVIGATION (iOS Style) ── */
.bottom-nav-container {
    position: fixed;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 100%;
    max-width: 430px;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border-top: 1px solid rgba(0,0,0,0.05);
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 20px 25px 20px; /* Account for iOS home bar */
    z-index: 999;
}

/* Base style for the hidden Streamlit buttons inside the nav */
.bottom-nav-container .stButton {
    width: auto !important;
    flex-grow: 1;
}
.bottom-nav-container .stButton > button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: auto !important;
    padding: 5px 0 !important;
    color: var(--text-2) !important;
    border-radius: 0 !important;
}

/* Nav Item Typography */
.bottom-nav-container .stButton > button p {
    font-size: 10px !important;
    font-weight: 500 !important;
    margin-top: 4px !important;
    font-family: var(--font-sans) !important;
}

/* Nav Icons (Injected via CSS since Streamlit buttons don't support custom HTML inside) */
.bottom-nav-container div:nth-child(1) .stButton > button::before { content: "⌂"; font-size: 22px; line-height: 1; }
.bottom-nav-container div:nth-child(2) .stButton > button::before { content: "❖"; font-size: 20px; line-height: 1; }
.bottom-nav-container div:nth-child(4) .stButton > button::before { content: "☆"; font-size: 22px; line-height: 1; }
.bottom-nav-container div:nth-child(5) .stButton > button::before { content: "👤"; font-size: 18px; line-height: 1; margin-top: 2px; }

/* The Floating Fab Button (Center) */
.bottom-nav-container div:nth-child(3) .stButton > button {
    background: var(--text-1) !important;
    color: var(--surface) !important;
    width: 54px !important;
    height: 54px !important;
    border-radius: 50% !important;
    margin-top: -30px !important; /* Pull it up out of the bar */
    box-shadow: var(--shadow-lg) !important;
    transition: transform 0.2s ease !important;
}
.bottom-nav-container div:nth-child(3) .stButton > button::before {
    content: "+"; font-size: 28px; font-weight: 300; line-height: 0;
}
.bottom-nav-container div:nth-child(3) .stButton > button p { display: none !important; /* Hide text on FAB */ }

/* Active State Simulation (You will control this via Streamlit Session State classes later) */
.nav-active > button { color: var(--text-1) !important; }

</style>
'''

def get_styles(dark_mode: bool = False) -> str:
    """
    Returns complete CSS for the given mode.
    """
    token_block = STYLES_DARK if dark_mode else STYLES_LIGHT
    return token_block + STYLES_BASE
