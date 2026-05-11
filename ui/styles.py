STYLES = '''
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@400;600&family=Noto+Naskh+Arabic:wght@400;600;700&display=swap');
:root{--bg:#0a0a0f;--surface:#111118;--surface-up:#16161f;--border:#ffffff0f;--border-focus:#6366f1;--accent:#6366f1;--accent-glow:#6366f120;--accent-hover:#4f46e5;--text-1:#f1f1f3;--text-2:#71717a;--text-3:#3f3f46;--success:#22c55e;--warning:#f59e0b;--danger:#ef4444;}
html,body,[class*='css']{font-family:Inter,sans-serif!important;color:var(--text-1)} .mono{font-family:'JetBrains Mono',monospace!important}
.stApp{background:var(--bg)!important}.stApp::after{content:'حبر';position:fixed;bottom:-40px;right:20px;font:700 280px 'Noto Naskh Arabic',serif;color:#6366f108;z-index:0;pointer-events:none}
[data-testid='stSidebar']{background:var(--surface)!important;border-right:1px solid var(--border)!important}
.block-container,[data-testid='stSidebar'] .block-container{position:relative;z-index:1}
.uplink-bar{font:11px 'JetBrains Mono';color:var(--text-3);display:flex;justify-content:space-between;border-bottom:1px solid var(--border);padding-bottom:8px;margin-bottom:8px}.dot.active{color:var(--success)}
.brand-ar{font:28px 'Noto Naskh Arabic';text-align:right;color:var(--text-1)} .brand-divider{height:1px;background:#6366f1;margin:8px 0}.brand-en{font:11px 'JetBrains Mono';color:var(--text-2);letter-spacing:.15em}
.identity-card{height:44px;background:var(--surface-up);border:1px solid var(--border);border-radius:10px;padding:8px 10px;display:flex;align-items:center;gap:8px}.avatar{width:28px;height:28px;border-radius:999px;background:var(--accent);color:#fff;display:flex;align-items:center;justify-content:center}.name{font-size:13px;font-weight:600}.logout{margin-left:auto;opacity:0}.identity-card:hover .logout{opacity:1;color:var(--text-2)}
.stButton>button{border-radius:8px!important;height:44px}.stButton>button[kind='primary'],div[data-testid='stButton'] button:has(span:contains('Refine Prompt')){background:var(--accent)!important;color:#fff!important;height:52px!important;border-radius:10px!important}
.empty-state{text-align:center;color:var(--text-2);font-size:12px;padding:24px}
</style>
'''
