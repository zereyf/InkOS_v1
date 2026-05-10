"""Premium UI stylesheet for InkOS."""

STYLES: str = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Geist:wght@400;500;600;700&display=swap');
:root {
  --bg:#0b0d12; --bg-elev:#121722; --card:#141a26; --text:#f3f6fc; --muted:#9aa5b5;
  --border:#243042; --accent:#7aa2ff; --success:#3ad29f; --warn:#ffb86b; --danger:#ff6b6b;
}
[data-theme="light"] { --bg:#f6f8fc; --bg-elev:#ffffff; --card:#ffffff; --text:#101524; --muted:#5e6879; --border:#d7deea; --accent:#3f6fff; }
html, body, [class*="css"] { font-family: Inter, Geist, system-ui, -apple-system, sans-serif !important; }
.stApp{ background:var(--bg)!important; color:var(--text)!important; }
#MainMenu, footer{ visibility:hidden; }
header[data-testid="stHeader"]{ background:transparent; }
header[data-testid="stHeader"] [data-testid="collapsedControl"]{ visibility:visible; display:block; }
.block-container{ padding:1rem .8rem 2rem!important; max-width:1280px; }
@media (max-width: 900px){ .block-container{padding: .8rem .6rem 1.5rem!important;} }

[data-testid="stSidebar"]{ background:var(--bg-elev)!important; border-right:1px solid var(--border)!important; }

.stTextArea textarea, .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {
  background:var(--card)!important; color:var(--text)!important; border:1px solid var(--border)!important; border-radius:14px!important;
}
.stTextArea textarea:focus, .stTextInput input:focus { border-color:var(--accent)!important; box-shadow:0 0 0 2px rgba(122,162,255,.25)!important; }
.stButton > button {
  border-radius:12px!important; border:1px solid var(--border)!important; background:linear-gradient(180deg, var(--card), var(--bg-elev))!important;
  color:var(--text)!important; transition: transform .12s ease, border-color .2s ease, background .2s ease!important;
}
.stButton > button:hover{ transform:translateY(-1px); border-color:var(--accent)!important; }
.stButton > button:focus-visible{ outline:2px solid var(--accent)!important; outline-offset:2px; }

.premium-card { background:var(--card); border:1px solid var(--border); border-radius:16px; padding:14px; }
.prompt-panel textarea{ min-height:200px!important; font-size:1rem!important; line-height:1.65!important; }
.pill-note{font-size:.75rem;color:var(--muted);margin-bottom:8px}
.score-pill{display:inline-flex;align-items:center;gap:8px;padding:8px 12px;border-radius:999px;border:1px solid var(--border);font-weight:600}
.dot{width:10px;height:10px;border-radius:999px;display:inline-block}
.dot.good{background:var(--success)} .dot.mid{background:var(--warn)} .dot.bad{background:var(--danger)}
.kbd{font-size:.72rem;color:var(--muted)}
.diff-box{background:var(--bg-elev); border:1px solid var(--border); border-radius:12px; padding:10px; overflow:auto; max-height:360px}
.diff-add{background:rgba(58,210,159,.15)} .diff-del{background:rgba(255,107,107,.15)}
@keyframes shimmer {0%{background-position:-200% 0}100%{background-position:200% 0}}
.skeleton{height:18px;border-radius:8px;background:linear-gradient(90deg,var(--bg-elev) 25%, rgba(255,255,255,.08) 50%, var(--bg-elev) 75%);background-size:200% 100%;animation:shimmer 1.4s infinite}
.inline-actions{display:flex;gap:8px;flex-wrap:wrap}

/* Horizontal radio as pill tabs */
div[role="radiogroup"]{gap:8px}
div[role="radiogroup"] label[data-baseweb="radio"]{background:var(--card);border:1px solid var(--border);border-radius:999px;padding:5px 10px}
div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked){border-color:var(--accent);box-shadow:0 0 0 1px rgba(122,162,255,.35) inset}
</style>
"""
