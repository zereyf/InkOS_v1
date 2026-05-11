STYLES = '''
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;600&family=Noto+Naskh+Arabic:wght@400;600;700&display=swap');

/* ── TOKENS ── */
:root {
  --bg:           #0f0e17;
  --surface:      #1a1825;
  --surface-up:   #211f2e;
  --surface-card: #181622;
  --border:       #ffffff08;
  --border-gold:  #c9a84c33;
  --accent:       #c9a84c;
  --accent-light: #e8c97a;
  --accent-glow:  #c9a84c20;
  --accent-dim:   #c9a84c11;
  --text-1:       #f5f0e8;
  --text-2:       #8a8070;
  --text-3:       #4a4535;
  --success:      #4ade80;
  --warning:      #fbbf24;
  --danger:       #f87171;
  --font-serif:   'Playfair Display', Georgia, serif;
  --font-sans:    Inter, sans-serif;
  --font-mono:    'JetBrains Mono', monospace;
  --font-ar:      'Noto Naskh Arabic', serif;
}

/* Add this directly below your existing :root block */

.light-theme {
  --bg:           #f8f9fa;
  --surface:      #ffffff;
  --surface-up:   #f1f3f5;
  --surface-card: #ffffff;
  --border:       #e5e7eb;
  --border-gold:  #e5e7eb; /* Muted gold/border for light mode */
  --accent:       #111827; /* Dark text/accents */
  --accent-light: #1f2937;
  --accent-glow:  #00000010;
  --accent-dim:   #f3f4f6;
  --text-1:       #111827;
  --text-2:       #4b5563;
  --text-3:       #9ca3af;
  --success:      #10b981;
  --warning:      #f59e0b;
  --danger:       #ef4444;
}

/* Update the watermark to match light mode contrast */
.light-theme .stApp::after {
  color: #00000004; 
}


/* ── BASE ── */
html, body, [class*="css"] {
  font-family: var(--font-sans) !important;
  color: var(--text-1) !important;
  -webkit-font-smoothing: antialiased;
}

/* ── APP BACKGROUND ── */
.stApp {
  background: var(--bg) !important;
}

/* Subtle ink-wash watermark */
.stApp::before {
  content: '';
  position: fixed;
  bottom: 0; right: 0;
  width: 320px; height: 320px;
  background: radial-gradient(ellipse at bottom right,
    #c9a84c08 0%, transparent 70%);
  pointer-events: none;
  z-index: 0;
}
.stApp::after {
  content: 'حبر';
  position: fixed;
  bottom: -20px; right: 16px;
  font: 700 240px var(--font-ar);
  color: #c9a84c06;
  z-index: 0;
  pointer-events: none;
  user-select: none;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
  background: var(--surface) !important;
  border-right: 1px solid var(--border-gold) !important;
}
[data-testid="stSidebar"] > div {
  padding-top: 0 !important;
}
.block-container,
[data-testid="stSidebar"] .block-container {
  position: relative;
  z-index: 1;
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
  background:  #c9a84c0a !important;
  color:       var(--text-1) !important;
  border-left: 3px solid var(--text-3) !important;
}
[data-testid="stSidebar"] .nav-active + div .stButton > button {
  background:  #c9a84c12 !important;
  border-left: 3px solid var(--accent) !important;
  color:       var(--accent-light) !important;
}

/* ── PRIMARY BUTTON ── */
.stButton > button[kind="primary"] {
  background:    linear-gradient(135deg, #c9a84c, #a8863a) !important;
  color:         #0f0e17 !important;
  border:        none !important;
  border-radius: 12px !important;
  height:        52px !important;
  font-size:     14px !important;
  font-weight:   600 !important;
  font-family:   var(--font-sans) !important;
  letter-spacing: 0.02em !important;
  box-shadow:    0 4px 20px #c9a84c30 !important;
  transition:    all 150ms ease !important;
}
.stButton > button[kind="primary"]:hover {
  background: linear-gradient(135deg, #e8c97a, #c9a84c) !important;
  box-shadow: 0 6px 28px #c9a84c40 !important;
  transform:  translateY(-1px) !important;
}
.stButton > button[kind="primary"]:active {
  transform: translateY(0) scale(0.99) !important;
}

/* ── SECONDARY BUTTONS ── */
.main .stButton > button,
section[data-testid="stMain"] .stButton > button {
  background:    var(--surface-up) !important;
  border:        1px solid var(--border-gold) !important;
  border-radius: 10px !important;
  color:         var(--text-2) !important;
  font-size:     13px !important;
  height:        42px !important;
  transition:    all 150ms ease !important;
}
.main .stButton > button:hover,
section[data-testid="stMain"] .stButton > button:hover {
  background:  #c9a84c0a !important;
  color:       var(--accent-light) !important;
  border-color:#c9a84c55 !important;
}

/* ── INPUTS ── */
.stTextArea textarea,
.stTextInput input {
  background:    var(--surface-up) !important;
  border:        1px solid var(--border-gold) !important;
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

/* ── SELECTBOX ── */
.stSelectbox > div > div {
  background:    var(--surface-up) !important;
  border:        1px solid var(--border-gold) !important;
  border-radius: 10px !important;
  color:         var(--text-1) !important;
}

/* ── LABELS ── */
label, .stTextArea label, .stTextInput label, .stSelectbox label {
  color:          var(--text-2) !important;
  font-size:      11px !important;
  font-weight:    500 !important;
  letter-spacing: 0.06em !important;
  text-transform: uppercase !important;
}

/* ── ALERTS ── */
.stAlert {
  border-radius: 10px !important;
  border:        none !important;
  font-size:     13px !important;
  background:    var(--surface-up) !important;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar       { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #c9a84c22; border-radius: 999px; }
::-webkit-scrollbar-thumb:hover { background: #c9a84c44; }

/* ── FOCUS ── */
*:focus-visible {
  outline:    none !important;
  box-shadow: 0 0 0 3px #c9a84c25 !important;
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
  border-bottom:   1px solid var(--border-gold);
  padding:         10px 0 8px;
  margin-bottom:   12px;
}
.dot.active   { color: var(--success); }
.dot.inactive { color: var(--danger); }

.brand-ar {
  font:        700 26px var(--font-ar);
  text-align:  right;
  color:       var(--accent-light);
  line-height: 1.3;
}
.brand-divider {
  height:     1px;
  background: linear-gradient(90deg, transparent, var(--accent), transparent);
  margin:     8px 0;
  opacity:    .6;
}
.brand-en {
  font:           11px var(--font-mono);
  color:          var(--text-3);
  letter-spacing: 0.15em;
  margin-bottom:  12px;
}

/* ── IDENTITY CARD ── */
.identity-card {
  height:        48px;
  background:    var(--surface-card);
  border:        1px solid var(--border-gold);
  border-radius: 12px;
  padding:       0 14px;
  display:       flex;
  align-items:   center;
  gap:           10px;
  margin-bottom: 4px;
}
.avatar {
  width:           32px;
  height:          32px;
  border-radius:   999px;
  background:      linear-gradient(135deg, #c9a84c, #a8863a);
  color:           #0f0e17;
  display:         flex;
  align-items:     center;
  justify-content: center;
  font-size:       13px;
  font-weight:     700;
  flex-shrink:     0;
  font-family:     var(--font-sans);
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
  font:           10px var(--font-mono);
  color:          var(--text-3);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  padding:        0 2px;
  margin:         12px 0 6px;
}

/* ── NAV SECTION ── */
.nav-section {
  margin:  8px 0;
  padding: 6px 0;
  border-top:    1px solid var(--border-gold);
  border-bottom: 1px solid var(--border-gold);
}

/* ── STATS CARD ── */
.stats-card {
  background:     var(--surface-card);
  border:         1px solid var(--border-gold);
  border-radius:  12px;
  padding:        14px 16px;
  display:        grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap:            8px;
  margin:         12px 0;
}
.stat-item  { text-align: center; }
.stat-value {
  font-size:   20px;
  font-weight: 700;
  color:       var(--accent-light);
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
  background:    var(--surface-card);
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
.intel-key { font-size: 10px; color: var(--text-3); text-transform: uppercase; }
.intel-val { font-size: 12px; color: var(--text-1); font-weight: 500; }

/* ── WORKSPACE GREETING ── */
.ws-greeting {
  padding: 24px 0 20px;
}
.ws-greeting-time {
  font:           11px var(--font-mono);
  color:          var(--text-3);
  letter-spacing: .1em;
  margin-bottom:  6px;
}
.ws-greeting-main {
  font:        600 32px var(--font-serif);
  color:       var(--text-1);
  line-height: 1.2;
  margin-bottom: 4px;
}
.ws-greeting-sub {
  font-size: 14px;
  color:     var(--text-2);
}

/* ── ORIGINAL PROMPT CARD ── */
.prompt-card {
  background:    var(--surface-card);
  border:        1px solid var(--border);
  border-radius: 16px;
  padding:       20px;
  margin-bottom: 0;
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
  font-size:   16px;
  color:       var(--text-1);
  line-height: 1.6;
  margin-bottom: 14px;
  font-family: var(--font-sans);
}
.prompt-card-meta {
  font-size: 12px;
  color:     var(--text-3);
}

/* ── CONNECTOR ── */
.card-connector {
  display:         flex;
  justify-content: center;
  align-items:     center;
  height:          36px;
  position:        relative;
  z-index:         1;
}
.card-connector::before {
  content:    '';
  position:   absolute;
  top:        0; bottom: 0;
  left:       50%;
  width:      1px;
  background: linear-gradient(to bottom, var(--border), var(--accent), var(--border));
}
.card-connector-dot {
  width:           28px;
  height:          28px;
  border-radius:   999px;
  background:      var(--surface-card);
  border:          1px solid var(--border-gold);
  display:         flex;
  align-items:     center;
  justify-content: center;
  font-size:       12px;
  color:           var(--accent);
  position:        relative;
  z-index:         2;
}

/* ── REFINED INK CARD ── */
.refined-card {
  background:    var(--surface-card);
  border:        1px solid var(--border-gold);
  border-radius: 16px;
  padding:       20px;
  position:      relative;
  overflow:      hidden;
}
.refined-card::before {
  content:    '';
  position:   absolute;
  inset:      0;
  background: linear-gradient(135deg, #c9a84c08 0%, transparent 60%);
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
  font-size:   14px;
  color:       var(--accent-light);
  font-weight: 600;
  font-family: var(--font-serif);
}
.refined-card-icon {
  width:           30px;
  height:          30px;
  border-radius:   999px;
  background:      var(--accent-dim);
  border:          1px solid var(--border-gold);
  display:         flex;
  align-items:     center;
  justify-content: center;
  font-size:       14px;
}
.refined-badge {
  background:    var(--accent-dim);
  border:        1px solid var(--border-gold);
  border-radius: 999px;
  padding:       4px 12px;
  font-size:     11px;
  color:         var(--accent-light);
  font-family:   var(--font-mono);
  letter-spacing:.04em;
}
.refined-card-text {
  font-size:   15px;
  color:       var(--accent-light);
  line-height: 1.7;
  margin-bottom: 16px;
  font-family:   var(--font-sans);
}
.refined-card-divider {
  height:     1px;
  background: linear-gradient(90deg, transparent, var(--accent-dim), transparent);
  margin:     12px 0;
}
.refined-card-meta {
  font-size: 12px;
  color:     var(--text-3);
}

/* ── ACTION ROW ── */
.action-row {
  display: flex;
  gap:     10px;
  margin:  16px 0;
}
.action-btn {
  flex:            1;
  height:          44px;
  background:      var(--surface-up);
  border:          1px solid var(--border-gold);
  border-radius:   12px;
  display:         flex;
  align-items:     center;
  justify-content: center;
  gap:             6px;
  font-size:       13px;
  color:           var(--text-2);
  cursor:          pointer;
  transition:      all 150ms ease;
}
.action-btn:hover {
  background:   var(--accent-dim);
  color:        var(--accent-light);
  border-color: var(--accent);
}

/* ── RECENT INKS LIST ── */
.section-header {
  display:         flex;
  justify-content: space-between;
  align-items:     center;
  margin:          24px 0 14px;
}
.section-title {
  font:        600 20px var(--font-serif);
  color:       var(--text-1);
}
.section-link {
  font-size: 13px;
  color:     var(--accent);
  cursor:    pointer;
}
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
}
.ink-item:hover {
  border-color: var(--border-gold);
  background:   var(--surface-up);
}
.ink-thumb {
  width:           48px;
  height:          48px;
  border-radius:   10px;
  background:      var(--surface-up);
  border:          1px solid var(--border-gold);
  display:         flex;
  align-items:     center;
  justify-content: center;
  font:            600 18px var(--font-ar);
  color:           var(--accent-light);
  flex-shrink:     0;
}
.ink-content { flex: 1; min-width: 0; }
.ink-title {
  font-size:     14px;
  font-weight:   600;
  color:         var(--text-1);
  margin-bottom: 4px;
  white-space:   nowrap;
  overflow:      hidden;
  text-overflow: ellipsis;
}
.ink-preview {
  font-size:   12px;
  color:       var(--text-2);
  line-height: 1.4;
  display:     -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow:    hidden;
}
.ink-date {
  font-size:  11px;
  color:      var(--text-3);
  white-space:nowrap;
  flex-shrink:0;
  font-family:var(--font-mono);
}

/* ── BOTTOM INPUT BAR ── */
#ws-bar {
  position:   fixed;
  bottom:     0; left: 0; right: 0;
  z-index:    1000;
  background: linear-gradient(to top, #0f0e17 70%, transparent);
  padding:    12px 16px 24px;
}
@media (min-width: 768px) {
  #ws-bar { left: 260px; padding: 16px 24px 28px; }
}
.ws-bar-inner {
  background:    var(--surface-up);
  border:        1px solid var(--border-gold);
  border-radius: 999px;
  padding:       8px 8px 8px 20px;
  display:       flex;
  align-items:   center;
  gap:           8px;
  max-width:     640px;
  margin:        0 auto;
  box-shadow:    0 4px 24px #00000040;
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
  border: none !important; box-shadow: none !important;
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
  color:      var(--accent-light) !important;
  background: var(--accent-dim) !important;
}
/* Send button */
#ws-bar [data-testid="stButton"]:last-child > button {
  background:    linear-gradient(135deg, #c9a84c, #a8863a) !important;
  color:         #0f0e17 !important;
  width:         40px !important;
  height:        40px !important;
  font-size:     17px !important;
}

/* ── QUICK ACTION PILLS ── */
.quick-pills {
  display:         flex;
  gap:             8px;
  justify-content: center;
  flex-wrap:       wrap;
  margin-bottom:   24px;
}
div[data-testid="column"] .stButton > button {
  background:    var(--surface-up) !important;
  border:        1px solid var(--border-gold) !important;
  border-radius: 999px !important;
  color:         var(--text-2) !important;
  font-size:     13px !important;
  height:        38px !important;
  padding:       0 16px !important;
  transition:    all 150ms !important;
  white-space:   nowrap !important;
}
div[data-testid="column"] .stButton > button:hover {
  background:   var(--accent-dim) !important;
  color:        var(--accent-light) !important;
  border-color: var(--accent) !important;
}

/* ── EMPTY STATE ── */
.empty-state { text-align: center; padding: 48px 24px; }
.empty-state .en {
  font:        600 20px var(--font-serif);
  color:       var(--text-3);
  margin-bottom: 8px;
}
.empty-state .ar {
  font-size:   14px;
  color:       var(--text-3);
  font-family: var(--font-ar);
}

/* ── PIPELINE ANIMATION ── */
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0); }
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
.sidebar-section-label {
  font:           10px var(--font-mono);
  color:          var(--text-3);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  padding:        0 2px;
  margin:         12px 0 6px;
}
.nav-section {
  margin:  8px 0;
  padding: 6px 0;
  border-top:    1px solid var(--border-gold);
  border-bottom: 1px solid var(--border-gold);
}
.nav-item { display: block; }
.topbar { display:flex; align-items:center; gap:10px; margin-bottom:16px; }
.tag {
  font-size:12px; background:var(--surface-up); color:var(--text-2);
  padding:2px 10px; border-radius:999px; border:1px solid var(--border-gold);
}
</style>
'''
