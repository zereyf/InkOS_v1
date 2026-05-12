STYLES_LIGHT = '''
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&family=Noto+Naskh+Arabic:wght@400;600;700&family=IBM+Plex+Sans+Arabic:wght@400;500;600&family=Amiri:wght@400;700&display=swap');

/* ── LIGHT MODE TOKENS ── */
:root {
  --bg:             #F9F9F9;
  --bg-secondary:   #F0EEE9;
  --surface:        #FFFFFF;
  --surface-up:     #F5F3EF;
  --surface-card:   #FFFFFF;
  --border:         #E8E4DC;
  --border-gold:    #D4AF3733;
  --border-blue:    #2C3E5022;
  --accent:         #2C3E50;
  --accent-hover:   #1a2530;
  --accent-glow:    #2C3E5015;
  --gold:           #D4AF37;
  --gold-light:     #E8C84A;
  --gold-dim:       #D4AF3715;
  --gold-border:    #D4AF3740;
  --text-1:         #1A1A1A;
  --text-2:         #7F8C8D;
  --text-3:         #B0A898;
  --success:        #27AE60;
  --warning:        #F39C12;
  --danger:         #E74C3C;
  --font-serif:     'Playfair Display', Georgia, serif;
  --font-sans:      Inter, sans-serif;
  --font-mono:      'JetBrains Mono', monospace;
  --font-ar:        'IBM Plex Sans Arabic', sans-serif;
  --font-ar-serif:  'Amiri', 'Noto Naskh Arabic', serif;
  --shadow-sm:      0 1px 4px rgba(0,0,0,.06);
  --shadow-md:      0 4px 16px rgba(0,0,0,.08);
  --shadow-lg:      0 8px 32px rgba(0,0,0,.10);
}
</style>
'''

STYLES_DARK = '''
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&family=Noto+Naskh+Arabic:wght@400;600;700&family=IBM+Plex+Sans+Arabic:wght@400;500;600&family=Amiri:wght@400;700&display=swap');

/* ── DARK MODE TOKENS ── */
:root {
  --bg:             #0f0e17;
  --bg-secondary:   #13121c;
  --surface:        #1a1825;
  --surface-up:     #211f2e;
  --surface-card:   #181622;
  --border:         #ffffff0a;
  --border-gold:    #D4AF3725;
  --border-blue:    #2C3E5044;
  --accent:         #4A90D9;
  --accent-hover:   #5BA3E8;
  --accent-glow:    #4A90D920;
  --gold:           #D4AF37;
  --gold-light:     #E8C84A;
  --gold-dim:       #D4AF3712;
  --gold-border:    #D4AF3733;
  --text-1:         #F5F0E8;
  --text-2:         #8a8070;
  --text-3:         #4a4535;
  --success:        #2ECC71;
  --warning:        #F39C12;
  --danger:         #E74C3C;
  --font-serif:     'Playfair Display', Georgia, serif;
  --font-sans:      Inter, sans-serif;
  --font-mono:      'JetBrains Mono', monospace;
  --font-ar:        'IBM Plex Sans Arabic', sans-serif;
  --font-ar-serif:  'Amiri', 'Noto Naskh Arabic', serif;
  --shadow-sm:      0 1px 4px rgba(0,0,0,.30);
  --shadow-md:      0 4px 16px rgba(0,0,0,.40);
  --shadow-lg:      0 8px 32px rgba(0,0,0,.50);
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

/* Ink wash watermark */
.stApp::after {
  content: 'حبر';
  position: fixed;
  bottom: -20px; right: 16px;
  font: 700 220px var(--font-ar-serif);
  color: var(--gold-dim);
  z-index: 0;
  pointer-events: none;
  user-select: none;
  opacity: .6;
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
  position: relative; z-index: 1;
}

/* ── SIDEBAR NAV BUTTONS ── */
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

/* ── PRIMARY BUTTON ── */
.stButton > button[kind="primary"] {
  background:    var(--accent) !important;
  color:         #FFFFFF !important;
  border:        none !important;
  border-radius: 12px !important;
  height:        52px !important;
  font-size:     14px !important;
  font-weight:   600 !important;
  font-family:   var(--font-sans) !important;
  letter-spacing:.02em !important;
  box-shadow:    0 4px 16px var(--accent-glow) !important;
  transition:    all 150ms ease !important;
}
.stButton > button[kind="primary"]:hover {
  background: var(--accent-hover) !important;
  box-shadow: 0 6px 24px var(--accent-glow) !important;
  transform:  translateY(-1px) !important;
}
.stButton > button[kind="primary"]:active {
  transform: translateY(0) scale(0.99) !important;
}

/* ── SECONDARY BUTTONS ── */
.main .stButton > button,
section[data-testid="stMain"] .stButton > button {
  background:    var(--surface-up) !important;
  border:        1px solid var(--border) !important;
  border-radius: 10px !important;
  color:         var(--text-2) !important;
  font-size:     13px !important;
  height:        42px !important;
  transition:    all 150ms ease !important;
  font-family:   var(--font-sans) !important;
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
  color:       var(--text-3) !important;
  font-family: var(--font-sans) !important;
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
.stTextInput label,
.stSelectbox label {
  color:          var(--text-2) !important;
  font-size:      11px !important;
  font-weight:    500 !important;
  letter-spacing: 0.06em !important;
  text-transform: uppercase !important;
}

/* ── CHECKBOX & TOGGLE ── */
.stCheckbox label,
.stToggle label {
  color:     var(--text-2) !important;
  font-size: 13px !important;
}

/* ── ALERTS ── */
.stAlert {
  border-radius: 10px !important;
  border:        none !important;
  font-size:     13px !important;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar       { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
  background:    var(--border);
  border-radius: 999px;
}
::-webkit-scrollbar-thumb:hover { background: var(--text-3); }

/* ── FOCUS ── */
*:focus-visible {
  outline:    none !important;
  box-shadow: 0 0 0 3px var(--accent-glow) !important;
}

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu, footer { visibility: hidden !important; }
[data-testid="collapsedControl"] { display: flex !important; }
.stDeployButton { display: none !important; }

/* ── MAIN LAYOUT ── */
.main .block-container {
  padding-bottom: 160px !important;
  padding-top:    0 !important;
  max-width:      680px !important;
  margin:         0 auto !important;
}

/* ── BRAND CLASSES ── */
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

/* Arabic brand */
.brand-ar {
  font:        700 26px var(--font-ar-serif);
  text-align:  right;
  color:       var(--text-1);
  line-height: 1.3;
}
.brand-divider {
  height:     1px;
  background: linear-gradient(
    90deg, transparent, var(--accent), transparent
  );
  margin: 8px 0;
  opacity: .4;
}
.brand-en {
  font:           600 18px var(--font-serif);
  color:          var(--text-1);
  margin-bottom:  4px;
  letter-spacing: -.01em;
}
.brand-sub {
  font:           11px var(--font-mono);
  color:          var(--text-3);
  letter-spacing: .12em;
  margin-bottom:  12px;
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
  width:           32px;
  height:          32px;
  border-radius:   999px;
  background:      var(--accent);
  color:           #fff;
  display:         flex;
  align-items:     center;
  justify-content: center;
  font-size:       13px;
  font-weight:     700;
  flex-shrink:     0;
}
.name   { font-size:13px; font-weight:600; color:var(--text-1); }
.logout {
  margin-left:auto; opacity:0; color:var(--text-2);
  font-size:16px; cursor:pointer; transition:opacity 150ms;
}
.identity-card:hover .logout { opacity: 1; }

/* ── SIDEBAR SECTION LABELS ── */
.sidebar-section-label {
  font:           10px var(--font-mono);
  color:          var(--text-3);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  padding:        0 2px;
  margin:         14px 0 6px;
}

/* ── NAV SECTION ── */
.nav-section {
  margin:  8px 0;
  padding: 6px 0;
  border-top:    1px solid var(--border);
  border-bottom: 1px solid var(--border);
}
.nav-item { display: block; }

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
.stat-item  { text-align: center; }
.stat-value {
  font-size:   20px;
  font-weight: 700;
  color:       var(--accent);
  font-family: var(--font-serif);
  display:     block;
}
.stat-label {
  font-size:      9px;
  color:          var(--text-3);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  margin-top:     2px;
  display:        block;
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
  font:           10px var(--font-mono);
  color:          var(--accent);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  margin-bottom:  8px;
}
.intel-row {
  display:         flex;
  justify-content: space-between;
  align-items:     center;
  margin-bottom:   4px;
}
.intel-key { font-size:10px; color:var(--text-3); text-transform:uppercase; }
.intel-val { font-size:12px; color:var(--text-1); font-weight:500; }

/* ── WORKSPACE GREETING ── */
.ws-greeting        { padding: 28px 0 16px; }
.ws-greeting-main   {
  font:          600 36px var(--font-serif);
  color:         var(--text-1);
  line-height:   1.2;
  margin-bottom: 6px;
}
.ws-greeting-sub    { font-size:15px; color:var(--text-2); }

/* ── INKOS LOGO IN WORKSPACE ── */
.ws-logo {
  text-align:    center;
  padding:       16px 0 8px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 24px;
}
.ws-logo-title {
  font:           700 28px var(--font-serif);
  color:          var(--accent);
  letter-spacing: -.02em;
}
.ws-logo-sub {
  font:           10px var(--font-mono);
  color:          var(--text-3);
  letter-spacing: .2em;
  margin-top:     4px;
}

/* ── PROMPT INPUT (DESK STYLE) ── */
.desk-input-wrap {
  background:    var(--surface-card);
  border:        1px solid var(--border);
  border-radius: 16px;
  padding:       16px 20px;
  display:       flex;
  align-items:   center;
  gap:           12px;
  box-shadow:    var(--shadow-md);
  margin-bottom: 16px;
}
.desk-input-icon {
  font-size:   20px;
  color:       var(--text-3);
  flex-shrink: 0;
}

/* ── QUICK ACTION PILLS ── */
div[data-testid="column"] .stButton > button {
  background:    var(--surface-card) !important;
  border:        1px solid var(--border) !important;
  border-radius: 999px !important;
  color:         var(--text-2) !important;
  font-size:     13px !important;
  height:        38px !important;
  padding:       0 14px !important;
  gap:           6px !important;
  transition:    all 150ms ease !important;
  box-shadow:    var(--shadow-sm) !important;
  font-family:   var(--font-sans) !important;
}
div[data-testid="column"] .stButton > button:hover {
  background:   var(--accent-glow) !important;
  color:        var(--accent) !important;
  border-color: var(--border-blue) !important;
}

/* ── ORIGINAL PROMPT CARD ── */
.prompt-card {
  background:    var(--surface-card);
  border:        1px solid var(--border);
  border-radius: 16px;
  padding:       20px;
  box-shadow:    var(--shadow-sm);
}
.prompt-card-header {
  display:         flex;
  justify-content: space-between;
  align-items:     center;
  margin-bottom:   14px;
}
.prompt-card-label {
  display:     flex;
  align-items: center;
  gap:         8px;
  font-size:   13px;
  color:       var(--text-2);
  font-weight: 500;
}
.prompt-card-icon {
  width:           28px;
  height:          28px;
  border-radius:   999px;
  background:      var(--surface-up);
  border:          1px solid var(--border);
  display:         flex;
  align-items:     center;
  justify-content: center;
  font-size:       13px;
}
.prompt-card-text {
  font-size:     16px;
  color:         var(--text-1);
  line-height:   1.65;
  margin-bottom: 14px;
  font-family:   var(--font-sans);
}
.prompt-card-meta {
  font-size: 12px;
  color:     var(--text-3);
  display:   flex;
  justify-content: space-between;
}

/* ── CONNECTOR ── */
.card-connector {
  display:         flex;
  justify-content: center;
  align-items:     center;
  height:          40px;
  position:        relative;
}
.card-connector::before {
  content:    '';
  position:   absolute;
  top:0; bottom:0; left:50%;
  width:      1px;
  background: linear-gradient(
    to bottom, var(--border), var(--gold), var(--border)
  );
}
.card-connector-dot {
  width:           32px;
  height:          32px;
  border-radius:   999px;
  background:      var(--surface-card);
  border:          1px solid var(--gold-border);
  display:         flex;
  align-items:     center;
  justify-content: center;
  font-size:       14px;
  color:           var(--gold);
  position:        relative;
  z-index:         2;
  box-shadow:      0 0 12px var(--gold-dim);
}

/* ── REFINED INK CARD ── */
.refined-card {
  background:    var(--surface-card);
  border:        1px solid var(--gold-border);
  border-radius: 16px;
  padding:       20px;
  position:      relative;
  overflow:      hidden;
  box-shadow:    0 4px 20px var(--gold-dim);
}
.refined-card::before {
  content:    '';
  position:   absolute;
  inset:      0;
  background: linear-gradient(
    135deg, var(--gold-dim) 0%, transparent 50%
  );
  pointer-events: none;
}
.refined-card-header {
  display:         flex;
  justify-content: space-between;
  align-items:     center;
  margin-bottom:   14px;
}
.refined-card-label {
  display:     flex;
  align-items: center;
  gap:         8px;
  font-size:   15px;
  color:       var(--gold);
  font-weight: 600;
  font-family: var(--font-serif);
}
.refined-card-icon {
  width:           30px;
  height:          30px;
  border-radius:   999px;
  background:      var(--gold-dim);
  border:          1px solid var(--gold-border);
  display:         flex;
  align-items:     center;
  justify-content: center;
  font-size:       14px;
}
.refined-badge {
  background:    var(--gold-dim);
  border:        1px solid var(--gold-border);
  border-radius: 999px;
  padding:       4px 12px;
  font-size:     11px;
  color:         var(--gold);
  font-family:   var(--font-mono);
  letter-spacing:.04em;
}
.refined-card-text {
  font-size:   16px;
  color:       var(--gold);
  line-height: 1.7;
  margin-bottom:14px;
  font-family: var(--font-serif);
}
.refined-card-divider {
  height:     1px;
  background: linear-gradient(
    90deg, transparent, var(--gold-border), transparent
  );
  margin: 12px 0;
}
.refined-card-meta {
  font-size:       12px;
  color:           var(--text-3);
  display:         flex;
  justify-content: space-between;
}

/* ── SECTION HEADER ── */
.section-header {
  display:         flex;
  justify-content: space-between;
  align-items:     center;
  margin:          28px 0 16px;
}
.section-title {
  font:        600 22px var(--font-serif);
  color:       var(--text-1);
}
.section-link {
  font-size: 13px;
  color:     var(--accent);
  cursor:    pointer;
}

/* ── RECENT INK ITEMS ── */
.ink-item {
  display:       flex;
  align-items:   flex-start;
  gap:           14px;
  padding:       16px;
  background:    var(--surface-card);
  border:        1px solid var(--border);
  border-radius: 14px;
  margin-bottom: 10px;
  transition:    all 150ms ease;
  cursor:        pointer;
  box-shadow:    var(--shadow-sm);
}
.ink-item:hover {
  border-color: var(--border-blue);
  box-shadow:   var(--shadow-md);
  transform:    translateY(-1px);
}
.ink-thumb {
  width:           48px;
  height:          48px;
  border-radius:   10px;
  background:      var(--surface-up);
  border:          1px solid var(--border);
  display:         flex;
  align-items:     center;
  justify-content: center;
  font:            600 18px var(--font-ar-serif);
  color:           var(--accent);
  flex-shrink:     0;
}
.ink-content  { flex:1; min-width:0; }
.ink-title    {
  font-size:     14px;
  font-weight:   600;
  color:         var(--text-1);
  margin-bottom: 4px;
  white-space:   nowrap;
  overflow:      hidden;
  text-overflow: ellipsis;
}
.ink-preview  {
  font-size:          12px;
  color:              var(--text-2);
  line-height:        1.45;
  display:            -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow:           hidden;
}
.ink-date {
  font-size:   11px;
  color:       var(--text-3);
  white-space: nowrap;
  flex-shrink: 0;
  font-family: var(--font-mono);
}

/* ── BOTTOM INPUT BAR ── */
#ws-bar {
  position:   fixed;
  bottom:0; left:0; right:0;
  z-index:    1000;
  background: linear-gradient(
    to top, var(--bg) 65%, transparent
  );
  padding: 12px 16px 24px;
}
@media(min-width:768px){
  #ws-bar { left:260px; padding:16px 24px 28px; }
}
.ws-bar-inner {
  background:    var(--surface-card);
  border:        1px solid var(--border);
  border-radius: 999px;
  padding:       8px 8px 8px 20px;
  display:       flex;
  align-items:   center;
  gap:           8px;
  max-width:     640px;
  margin:        0 auto;
  box-shadow:    var(--shadow-md);
}
#ws-bar .stTextArea textarea {
  background:  transparent !important;
  border:      none !important;
  box-shadow:  none !important;
  padding:     4px 0 !important;
  font-size:   14px !important;
  min-height:  40px !important;
  max-height:  120px !important;
  resize:      none !important;
  color:       var(--text-1) !important;
  font-family: var(--font-sans) !important;
}
#ws-bar .stTextArea textarea:focus {
  border:     none !important;
  box-shadow: none !important;
}
#ws-bar .stButton > button {
  background:    transparent !important;
  border:        none !important;
  border-radius: 999px !important;
  width:         36px !important;
  height:        36px !important;
  padding:       0 !important;
  font-size:     16px !important;
  color:         var(--text-2) !important;
  transition:    all 150ms !important;
  flex-shrink:   0 !important;
  box-shadow:    none !important;
}
#ws-bar .stButton > button:hover {
  color:      var(--accent) !important;
  background: var(--accent-glow) !important;
}
/* Send button */
#ws-bar [data-testid="stButton"]:last-child > button {
  background:    var(--accent) !important;
  color:         #fff !important;
  width:         40px !important;
  height:        40px !important;
  font-size:     18px !important;
  box-shadow:    0 2px 8px var(--accent-glow) !important;
}
#ws-bar [data-testid="stButton"]:last-child > button:hover {
  background: var(--accent-hover) !important;
}

/* ── EMPTY STATE ── */
.empty-state      { text-align:center; padding:60px 24px; }
.empty-state .en  {
  font:        600 22px var(--font-serif);
  color:       var(--text-3);
  margin-bottom:8px;
}
.empty-state .ar  {
  font-size:   15px;
  color:       var(--text-3);
  font-family: var(--font-ar-serif);
}

/* ── PIPELINE ANIMATION ── */
@keyframes spin    { to { transform: rotate(360deg); } }
@keyframes fadeUp  {
  from { opacity:0; transform:translateY(10px); }
  to   { opacity:1; transform:translateY(0);    }
}
@keyframes inkDrop {
  0%   { opacity:0; transform:scaleY(0); transform-origin:top; }
  100% { opacity:1; transform:scaleY(1); }
}

/* ── RTL SUPPORT ── */
[dir="rtl"] .brand-ar        { text-align:left; }
[dir="rtl"] .identity-card   { flex-direction:row-reverse; }
[dir="rtl"] .logout          { margin-left:0; margin-right:auto; }
[dir="rtl"] .prompt-card-text,
[dir="rtl"] .refined-card-text {
  text-align:  right;
  font-family: var(--font-ar-serif);
  font-size:   17px;
  line-height: 1.9;
}
[dir="rtl"] .ink-title,
[dir="rtl"] .ink-preview { text-align:right; font-family:var(--font-ar); }
[dir="rtl"] .ws-greeting-main,
[dir="rtl"] .ws-greeting-sub { text-align:right; font-family:var(--font-ar); }
[dir="rtl"] .section-title   { font-family:var(--font-ar); }
[dir="rtl"] [data-testid="stSidebar"] .stButton > button {
  text-align:    right !important;
  border-left:   none !important;
  border-right:  3px solid transparent !important;
  border-radius: 8px 0 0 8px !important;
}
[dir="rtl"] [data-testid="stSidebar"] .nav-active + div .stButton > button {
  border-right: 3px solid var(--accent) !important;
  border-left:  none !important;
}

/* ── MAINTENANCE ── */
.maintenance-lock {
  text-align:  center;
  padding:     40px;
  font-family: var(--font-mono);
  color:       var(--danger);
  font-size:   18px;
}

/* ── MISC ── */
.topbar { display:flex; align-items:center; gap:10px; margin-bottom:16px; }
.tag {
  font-size:12px; background:var(--surface-up);
  color:var(--text-2); padding:2px 10px;
  border-radius:999px; border:1px solid var(--border);
}
</style>
'''


def get_styles(dark_mode: bool = True) -> str:
    """Return complete styles for the given mode."""
    token_block = STYLES_DARK if dark_mode else STYLES_LIGHT
    return token_block + STYLES_BASE
