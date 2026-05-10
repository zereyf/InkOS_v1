"""Premium dark UI theme for InkOS frontend (Streamlit CSS override only)."""

STYLES: str = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
:root{
 --bg:#0a0a0a;--panel:#101114;--panel-2:#151720;--text:#f3f4f6;--muted:#9aa0ae;--border:rgba(255,255,255,.09);
 --accent:#5b7cff;--accent-soft:rgba(91,124,255,.16);--ok:#4ade80;--warn:#f59e0b;
}
html,body,[class*="css"]{font-family:'Inter',system-ui,sans-serif!important}
.stApp{background:radial-gradient(circle at 0 0,#111425 0%,#0a0a0a 45%);color:var(--text)}
#MainMenu,footer,header[data-testid="stHeader"]{visibility:hidden}
.block-container{max-width:1200px;padding:2rem 1.2rem 2.8rem!important;animation:enter .35s ease both}
@keyframes enter{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}

[data-testid="stSidebar"]{background:#0d0f14;border-right:1px solid var(--border)}
[data-testid="stSidebar"] .stRadio label,[data-testid="stSidebar"] .stSelectbox label{font-size:.74rem;color:var(--muted)}

.stTextArea textarea,.stTextInput input,.stSelectbox [data-baseweb="select"]>div{background:var(--panel)!important;border:1px solid var(--border)!important;border-radius:14px!important;color:var(--text)!important}
.stTextArea textarea{min-height:170px!important;font-size:1rem!important;line-height:1.6;padding:1rem!important}
.stTextArea textarea:focus,.stTextInput input:focus{border-color:var(--accent)!important;box-shadow:0 0 0 3px var(--accent-soft)!important}

.stButton>button{height:44px;border-radius:12px!important;border:1px solid var(--border)!important;background:var(--panel)!important;color:var(--text)!important;font-weight:600;transition:.2s}
.stButton>button:hover{transform:translateY(-1px);border-color:var(--accent)!important;background:linear-gradient(180deg,#171c2f,#11131a)!important}
.stButton>button[kind="primary"]{background:linear-gradient(180deg,#5b7cff,#4466f2)!important;color:white!important;border:none!important}

[data-testid="stMetricValue"],h1,h2,h3{color:var(--text)!important}
hr{border-color:var(--border)!important}

.premium-card{background:var(--panel);border:1px solid var(--border);border-radius:16px;padding:18px}
.premium-header{display:flex;justify-content:space-between;gap:12px;align-items:flex-start;margin-bottom:14px}
.premium-title{font-size:1.3rem;font-weight:650;letter-spacing:-.01em}
.premium-caption{font-size:.8rem;color:var(--muted)}
.pill{display:inline-flex;align-items:center;padding:5px 10px;border:1px solid var(--border);border-radius:999px;font-size:.72rem;color:#cdd3e2;background:rgba(255,255,255,.02);margin-left:6px}
.score{display:flex;align-items:center;gap:12px;margin-bottom:10px}.score-dot{width:10px;height:10px;border-radius:50%;background:var(--ok)}
.diff{background:var(--panel-2);border:1px solid var(--border);border-radius:12px;padding:10px;min-height:300px}
.diff mark{background:rgba(91,124,255,.25);color:inherit;border-radius:4px;padding:0 2px}

.stProgress > div > div > div{background:linear-gradient(90deg,#4b63ff,#7b8dff)!important}
[data-testid="stSkeleton"]{border-radius:12px!important}

@media (max-width: 768px){
  .block-container{padding:1rem .8rem 5rem!important}
  .stButton>button{min-height:44px}
}
</style>
"""
