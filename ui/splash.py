"""
ui/splash.py — The Terminal Gateway
=====================================
v1.4: Nuclear Fix — bypass Streamlit's Markdown renderer entirely.
      - Uses st.components.v1.html() which renders raw HTML directly.
      - No more code-block leaking, no Markdown interpretation, no stripping.
      - Self-contained: all CSS vars, fonts, animations inside the component.
"""

import streamlit.components.v1 as components


def render_splash_screen():
    html = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --gold:       #C9A84C;
    --steel:      #8BA7B8;
    --danger:     #E53E3E;
    --bg-card:    #0E1117;
    --text:       #D4D4D4;
    --text-dim:   #666677;
    --text-muted: #888899;
    --font-d:     'Georgia', 'Times New Roman', serif;
    --font-m:     'Courier New', 'Lucida Console', monospace;
  }

  body {
    background: transparent;
    font-family: var(--font-m);
  }

  @keyframes pulse {
    0%   { opacity: 0.6; }
    50%  { opacity: 1; text-shadow: 0 0 8px var(--danger); }
    100% { opacity: 0.6; }
  }

  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
  }

  .card {
    max-width: 700px;
    margin: 20px auto 0;
    padding: 30px;
    background: var(--bg-card);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 4px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    animation: fadeIn 0.6s ease both;
  }

  /* HEADER */
  .header {
    border-left: 3px solid var(--gold);
    padding-left: 20px;
    margin-bottom: 40px;
  }
  .header h1 {
    font-family: var(--font-d);
    color: var(--gold);
    font-size: 2.5rem;
    letter-spacing: 2px;
  }
  .header span {
    font-family: var(--font-m);
    font-size: 0.75rem;
    color: var(--text-dim);
    letter-spacing: 4px;
  }

  /* INTRO */
  .intro {
    margin-bottom: 30px;
    font-family: var(--font-m);
    font-size: 0.9rem;
    color: var(--text);
    line-height: 1.7;
  }

  /* ARCHITECTURE */
  .arch {
    background: rgba(0,0,0,0.3);
    border: 1px solid rgba(255,255,255,0.03);
    padding: 20px;
    margin-bottom: 30px;
  }
  .arch-title {
    font-family: var(--font-m);
    font-size: 0.65rem;
    color: var(--gold);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 15px;
  }
  .arch-item {
    margin-bottom: 12px;
  }
  .arch-item .label {
    color: var(--steel);
    font-weight: bold;
    font-family: var(--font-m);
    font-size: 0.8rem;
    display: block;
  }
  .arch-item .desc {
    color: var(--text-muted);
    font-size: 0.8rem;
  }

  /* FOOTER */
  .footer {
    display: flex;
    flex-wrap: wrap;
    gap: 16px;
    justify-content: space-between;
    align-items: flex-end;
    border-top: 1px solid rgba(255,255,255,0.05);
    padding-top: 20px;
  }
  .architect-label {
    font-family: var(--font-m);
    font-size: 0.6rem;
    color: var(--text-dim);
    letter-spacing: 2px;
  }
  .architect-name {
    color: var(--text);
    font-family: var(--font-m);
    font-size: 0.9rem;
  }
  .lock {
    text-align: right;
    animation: pulse 2s infinite;
  }
  .lock-status {
    font-family: var(--font-m);
    font-size: 0.65rem;
    color: var(--danger);
    letter-spacing: 2px;
    font-weight: bold;
  }
  .lock-sub {
    font-family: var(--font-m);
    font-size: 0.55rem;
    color: var(--text-muted);
    letter-spacing: 1px;
  }

  /* HINT */
  .hint {
    text-align: center;
    margin-top: 20px;
  }
  .hint span {
    background: rgba(229,62,62,0.05);
    border: 1px solid rgba(229,62,62,0.2);
    color: var(--danger);
    padding: 8px 15px;
    font-family: var(--font-m);
    font-size: 0.65rem;
    letter-spacing: 2px;
    display: inline-block;
  }
</style>
</head>
<body>

<div class="card">

  <!-- HEADER -->
  <div class="header">
    <h1>حبر وفكرة</h1>
    <span>INKOS V2026.4 // VELVETCODEX INITIATIVE</span>
  </div>

  <!-- INTRO -->
  <div class="intro">
    Most interfaces are soulless. InkOS is a highly opinionated intelligence terminal
    designed for precision, speed, and ethical rigor. It does not just generate text;
    it refracts intent through specialized cognitive frameworks.
  </div>

  <!-- ARCHITECTURE SPECS -->
  <div class="arch">
    <div class="arch-title">&gt;&gt; System Architecture</div>

    <div class="arch-item">
      <span class="label">[ THE REFLEX ENGINE ]</span>
      <span class="desc">Instantaneous logic routing powered by 8B open-source intelligence.</span>
    </div>

    <div class="arch-item">
      <span class="label">[ LIS&#x100;N AL-&#x2018;ARAB ]</span>
      <span class="desc">Deep morphological rigor. Dialectal bleed is negated; classical Fusha is enforced.</span>
    </div>

    <div class="arch-item">
      <span class="label">[ MAQASID LAYER ]</span>
      <span class="desc">Strict ethical filtering. Generative outputs are inherently aligned with foundational principles.</span>
    </div>
  </div>

  <!-- AUTHOR SIGNATURE -->
  <div class="footer">
    <div>
      <div class="architect-label">ARCHITECT</div>
      <div class="architect-name">AMEERINK</div>
    </div>

    <div class="lock">
      <div class="lock-status">[ &#x2298; ] TERMINAL LOCKED</div>
      <div class="lock-sub">AWAITING OPERATOR LATCH</div>
    </div>
  </div>

</div>

<!-- HINT BAR -->
<div class="hint">
  <span>[&lt;&lt;] ALIGN IDENTITY IN SIDEBAR TO UNLOCK</span>
</div>

</body>
</html>
"""

    components.html(html, height=520, scrolling=False)
