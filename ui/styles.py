"""Premium UI stylesheet for InkOS."""

STYLES: str = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
:root {
  --bg:#0a0a0f; --surface:#111118; --surface-raised:#16161f; --border:#ffffff0f; --focus:#6366f1;
  --accent:#6366f1; --accent-glow:#6366f120; --text:#f1f1f3; --text-secondary:#71717a; --text-muted:#3f3f46;
  --success:#22c55e; --warning:#f59e0b; --danger:#ef4444;
}
html, body, [class*="css"] { font-family: Inter, system-ui, -apple-system, sans-serif !important; }
.stApp{ background:var(--bg)!important; color:var(--text)!important; }
#MainMenu, footer{ visibility:hidden; }
header[data-testid="stHeader"]{ background:transparent; }
.block-container{ padding:20px!important; max-width:720px; margin:0 auto; animation: fadeIn .2s ease; }
[data-testid="stSidebar"]{ background:var(--surface)!important; border-right:1px solid var(--border)!important; }
[data-testid="stSidebar"] .block-container{max-width:unset; padding:16px!important;}

.stTextArea textarea, .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {
  background:var(--surface)!important; color:var(--text)!important; border:1px solid var(--border)!important; border-radius:10px!important;
}
.stTextArea textarea{ min-height:180px!important; line-height:1.6!important; font-size:14px!important; }
.stTextArea textarea:focus, .stTextInput input:focus { border-color:var(--focus)!important; box-shadow:0 0 0 3px #6366f130!important; }

.stButton > button { height:44px; border-radius:8px!important; border:1px solid var(--border)!important; background:transparent!important; color:var(--text)!important; transition:all .15s ease!important; }
.stButton > button:hover{ transform:scale(1.01); border-color:var(--focus)!important; }
.primary-btn button{ height:52px!important; background:var(--accent)!important; border-color:var(--accent)!important; font-weight:600; }
.primary-btn button:hover{ box-shadow:0 0 24px var(--accent-glow); }

.mono{ font-family:"JetBrains Mono", monospace!important; }
.topbar{ display:flex;justify-content:space-between;align-items:center;margin-bottom:12px; }
.brand{ font-size:13px;color:var(--text-secondary);font-family:"JetBrains Mono",monospace; }
.tag{ border:1px solid var(--border);border-radius:999px;padding:2px 10px;color:var(--text-muted);font-size:11px; }
.card{ background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:16px;box-shadow:0 1px 3px #00000040; }
.voice{ height:48px;border:1px solid var(--border);border-radius:10px;display:flex;align-items:center;justify-content:space-between;padding:0 12px;color:var(--text-secondary); }
.score-pill{ display:inline-flex; padding:6px 10px; border-radius:999px; font-size:12px; font-weight:600; }
.score-excellent{ background:#22c55e20; color:var(--success); }
.score-good{ background:#f59e0b20; color:var(--warning); }
.score-fair{ background:#ef444420; color:var(--danger); }
.diff-box{ background:var(--surface-raised); border:1px solid var(--border); border-radius:12px; padding:10px; max-height:360px; overflow:auto; font-family:"JetBrains Mono", monospace; font-size:13px; }
.diff-add{ background:#22c55e15; color:var(--success);} .diff-del{ background:#ef444415; color:var(--danger);} 
.sidebar-h{ font-size:11px;color:var(--text-secondary);letter-spacing:.08em;font-family:"JetBrains Mono", monospace;margin:16px 0 8px; }
.stat-row{ display:grid;grid-template-columns:repeat(3,1fr);gap:8px; }
.stat-card{ background:var(--surface-raised);border:1px solid var(--border);border-radius:10px;padding:10px;text-align:center; }
@media (max-width: 768px){ .block-container{padding:16px!important;} }
@keyframes fadeIn { from {opacity:0;} to {opacity:1;} }
</style>
"""
