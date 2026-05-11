STYLES = '''
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&family=Noto+Naskh+Arabic:wght@400;600;700&display=swap');

/* ── TOKENS ── */
:root {
  --bg:           #0a0a0f;
  --surface:      #111118;
  --surface-up:   #16161f;
  --border:       #ffffff0f;
  --border-focus: #6366f1;
  --accent:       #6366f1;
  --accent-glow:  #6366f120;
  --accent-hover: #4f46e5;
  --text-1:       #f1f1f3;
  --text-2:       #71717a;
  --text-3:       #3f3f46;
  --success:      #22c55e;
  --warning:      #f59e0b;
  --danger:       #ef4444;
}

/* ── BASE ── */
html, body, [class*="css"] {
  font-family: Inter, sans-serif !important;
  color: var(--text-1) !important;
}
.mono { font-family: "JetBrains Mono", monospace !important; }

/* ── APP BACKGROUND ── */
.stApp { background: var(--bg) !important; }

/* Arabic watermark */
.stApp::after {
  content: 'حبر';
  position: fixed;
  bottom: -40px;
  right: 20px;
  font: 700 280px 'Noto Naskh Arabic', serif;
  color: #6366f108;
  z-index: 0;
  pointer-events: none;
  user-select: none;
}

/* ── SIDEBAR BASE ── */
[data-testid="stSidebar"] {
  background: var(--surface) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] > div {
  padding-top: 0 !important;
}
.block-container,
[data-testid="stSidebar"] .block-container {
  position: relative;
  z-index: 1;
}

/* ── SIDEBAR NAV ROWS ──
   All buttons inside sidebar become slim text rows.
   The .nav-active wrapper div signals the active state.
*/
[data-testid="stSidebar"] .stButton > button {
  background:    transparent !important;
  border:        none !important;
  border-left:   3px solid transparent !important;
  border-radius: 0 8px 8px 0 !important;
  color:         var(--text-2) !important;
  font-size:     13px !important;
  font-weight:   500 !important;
  font-family:   Inter, sans-serif !important;
  text-align:    left !important;
  height:        44px !important;
  padding:       0 16px !important;
  width:         100% !important;
  box-shadow:    none !important;
  transition:    all 150ms ease !important;
  margin-bottom: 2px !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
  background:  #ffffff08 !important;
  color:       var(--text-1) !important;
  border-left: 3px solid var(--text-3) !important;
}

/* Active nav item — sibling button gets accent styles */
[data-testid="stSidebar"] .nav-active + div .stButton > button,
[data-testid="stSidebar"] .nav-active ~ div .stButton > button:first-child {
  background:  #6366f11a !important;
  border-left: 3px solid var(--accent) !important;
  color:       var(--text-1) !important;
}

/* Logout button — distinct from nav */
[data-testid="stSidebar"] button[data-testid="baseButton-secondary"]:has-text("Logout") {
  background:    var(--surface-up) !important;
  border:        1px solid var(--border) !important;
  border-radius: 8px !important;
  color:         var(--text-2) !important;
  font-size:     12px !important;
  height:        36px !important;
  margin-top:    4px !important;
}

/* ── MAIN AREA — PRIMARY BUTTON (Refine Prompt / Send) ── */
.stButton > button[kind="primary"] {
  background:    var(--accent) !important;
  color:         #ffffff !important;
  border:        none !important;
  border-radius: 10px !important;
  height:        52px !important;
  font-size:     15px !important;
  font-weight:   600 !important;
  box-shadow:    none !important;
  transition:    all 150ms ease !important;
}
.stButton > button[kind="primary"]:hover {
  background:  var(--accent-hover) !important;
  box-shadow:  0 0 20px var(--accent-glow) !important;
  transform:   scale(1.01) !important;
}
.stButton > button[kind="primary"]:active {
  transform: scale(0.99) !important;
}

/* ── SECONDARY BUTTONS (main area only) ── */
.main .stButton > button,
section[data-testid="stMain"] .stButton > button {
  background:    var(--surface-up) !important;
  border:        1px solid var(--border) !important;
  border-radius: 8px !important;
  color:         var(--text-2) !important;
  font-size:     13px !important;
  height:        40px !important;
  transition:    all 150ms ease !important;
}
.main .stButton > button:hover,
section[data-testid="stMain"] .stButton > button:hover {
  background: #ffffff0a !important;
  color:      var(--text-1) !important;
}

/* ── INPUTS ── */
.stTextArea textarea,
.stTextInput input {
  background:  var(--surface-up) !important;
  border:      1px solid var(--border) !important;
  border-radius: 10px !important;
  color:       var(--text-1) !important;
  font-family: Inter, sans-serif !important;
  font-size:   14px !important;
  transition:  border-color 150ms ease !important;
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

/* ── SELECTBOX ── */
.stSelectbox > div > div {
  background:    var(--surface-up) !important;
  border:        1px solid var(--border) !important;
  border-radius: 10px !important;
  color:         var(--text-1) !important;
}

/* ── LABELS ── */
.stTextArea label,
.stTextInput label,
.stSelectbox label {
  color:          var(--text-2) !important;
  font-size:      12px !important;
  font-weight:    500 !important;
  letter-spacing: 0.04em !important;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar       { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #ffffff15; border-radius: 999px; }
::-webkit-scrollbar-thumb:hover { background: #ffffff30; }

/* ── FOCUS ── */
*:focus-visible {
  outline:    none !important;
  box-shadow: 0 0 0 3px #6366f130 !important;
}

/* ── ALERTS ── */
.stAlert {
  border-radius: 10px !important;
  border:        none !important;
  font-size:     13px !important;
}

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu, footer { visibility: hidden !important; }
[data-testid="collapsedControl"] { display: flex !important; }
.stDeployButton { display: none !important; }

/* ── BRAND CLASSES ── */
.uplink-bar {
  font:            11px 'JetBrains Mono', monospace;
  color:           var(--text-3);
  display:         flex;
  justify-content: space-between;
  border-bottom:   1px solid var(--border);
  padding-bottom:  8px;
  margin-bottom:   12px;
}
.dot.active   { color: var(--success); }
.dot.inactive { color: var(--danger); }

.brand-ar {
  font:       700 28px 'Noto Naskh Arabic', serif;
  text-align: right;
  color:      var(--text-1);
  line-height:1.3;
}
.brand-divider {
  height:     1px;
  background: var(--accent);
  margin:     8px 0;
}
.brand-en {
  font:           11px 'JetBrains Mono', monospace;
  color:          var(--text-2);
  letter-spacing: 0.15em;
  margin-bottom:  16px;
}

/* ── IDENTITY CARD ── */
.identity-card {
  height:        48px;
  background:    var(--surface-up);
  border:        1px solid var(--border);
  border-radius: 10px;
  padding:       0 12px;
  display:       flex;
  align-items:   center;
  gap:           10px;
  margin-bottom: 4px;
}
.avatar {
  width:           28px;
  height:          28px;
  border-radius:   999px;
  background:      var(--accent);
  color:           #fff;
  display:         flex;
  align-items:     center;
  justify-content: center;
  font-size:       12px;
  font-weight:     700;
  flex-shrink:     0;
}
.name   { font-size: 13px; font-weight: 600; color: var(--text-1); }
.logout {
  margin-left: auto;
  opacity:     0;
  color:       var(--text-2);
  font-size:   16px;
  cursor:      pointer;
  transition:  opacity 150ms;
}
.identity-card:hover .logout { opacity: 1; }

/* ── SIDEBAR SECTION LABELS ── */
.sidebar-section-label {
  font:           11px 'JetBrains Mono', monospace;
  color:          var(--text-3);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  padding:        0 4px;
  margin-bottom:  6px;
  margin-top:     4px;
}

/* ── NAV SECTION ── */
.nav-section {
  margin:        12px 0;
  border-top:    1px solid var(--border);
  border-bottom: 1px solid var(--border);
  padding:       8px 0;
}
.nav-item { display: block; }

/* ── STATS CARD ── */
.stats-card {
  background:     var(--surface-up);
  border:         1px solid var(--border);
  border-radius:  12px;
  padding:        14px 16px;
  display:        grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap:            8px;
  margin:         12px 0;
  text-align:     center;
}
.stat-item  { text-align: center; }
.stat-value {
  font-size:   18px;
  font-weight: 700;
  color:       var(--text-1);
  font-family: 'JetBrains Mono', monospace;
  display:     block;
}
.stat-label {
  font-size:      10px;
  color:          var(--text-3);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  margin-top:     2px;
  display:        block;
}

/* ── INTELLIGENCE CARD ── */
.intel-card {
  border-left:   2px solid var(--accent);
  background:    var(--surface-up);
  border-radius: 0 8px 8px 0;
  padding:       10px 14px;
  margin:        8px 0;
}
.intel-title {
  font:           11px 'JetBrains Mono', monospace;
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
.intel-key {
  font-size:      10px;
  color:          var(--text-3);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.intel-val {
  font-size:   12px;
  color:       var(--text-1);
  font-weight: 500;
}

/* ── EMPTY STATE ── */
.empty-state      { text-align: center; padding: 48px 24px; }
.empty-state .en  { font-size: 14px; color: var(--text-3); margin-bottom: 6px; }
.empty-state .ar  {
  font-size:   13px;
  color:       var(--text-3);
  font-family: 'Noto Naskh Arabic', serif;
}

/* ── MAINTENANCE ── */
.maintenance-lock {
  text-align:  center;
  padding:     40px;
  font-family: 'JetBrains Mono', monospace;
  color:       var(--danger);
  font-size:   18px;
}

/* ── ANIMATIONS ── */
@keyframes spin {
  to { transform: rotate(360deg); }
}
@keyframes fadeSlideUp {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0);   }
}

/* ── WORKSPACE BOTTOM BAR ── */
.main .block-container {
  padding-bottom: 150px !important;
  padding-top:    8px !important;
  max-width:      720px !important;
  margin:         0 auto !important;
}

/* ── QUICK ACTION CARDS ── */
div[data-testid="column"] .stButton > button {
  background:    var(--surface-up) !important;
  border:        1px solid var(--border) !important;
  border-radius: 14px !important;
  color:         var(--text-2) !important;
  font-size:     12px !important;
  height:        auto !important;
  padding:       12px 8px !important;
  white-space:   normal !important;
  line-height:   1.4 !important;
  transition:    all 150ms ease !important;
}
div[data-testid="column"] .stButton > button:hover {
  background:   #1c1c2a !important;
  color:        var(--text-1) !important;
  border-color: #6366f133 !important;
}

/* ── TOPBAR ── */
.topbar {
  display:     flex;
  align-items: center;
  gap:         10px;
  margin-bottom: 20px;
}
.tag {
  font-size:     11px;
  background:    var(--surface-up);
  color:         var(--text-2);
  padding:       2px 8px;
  border-radius: 999px;
  border:        1px solid var(--border);
}

</style>
'''
