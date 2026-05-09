"""
ui/splash.py — The Terminal Gateway
=====================================
v1.4: Uses components.html() to bypass Streamlit's Markdown renderer.
v1.5: CSS variables sourced from ui.theme.VARS — single source of truth.
"""

import streamlit.components.v1 as components
from ui.theme import VARS


def render_splash_screen():
    v = VARS  # shorthand

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    background: transparent;
    font-family: {v['font_m']};
  }}

  @keyframes pulse {{
    0%   {{ opacity: 0.6; }}
    50%  {{ opacity: 1; text-shadow: 0 0 8px {v['danger']}; }}
    100% {{ opacity: 0.6; }}
  }}

  @keyframes fadeIn {{
    from {{ opacity: 0; transform: translateY(8px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
  }}

  .card {{
    max-width: 700px;
    margin: 20px auto 0;
    padding: 30px;
    background: {v['bg_card']};
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 4px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    animation: fadeIn 0.6s ease both;
  }}

  .header {{
    border-left: 3px solid {v['gold']};
    padding-left: 20px;
    margin-bottom: 40px;
  }}
  .header h1 {{
    font-family: {v['font_d']};
    color: {v['gold']};
    font-size: 2.5rem;
    letter-spacing: 2px;
  }}
  .header span {{
    font-family: {v['font_m']};
    font-size: 0.75rem;
    color: {v['text_dim']};
    letter-spacing: 4px;
  }}

  .intro {{
    margin-bottom: 30px;
    font-family: {v['font_m']};
    font-size: 0.9rem;
    color: {v['text']};
    line-height: 1.7;
  }}

  .arch {{
    background: rgba(0,0,0,0.3);
    border: 1px solid rgba(255,255,255,0.03);
    padding: 20px;
    margin-bottom: 30px;
  }}
  .arch-title {{
    font-family: {v['font_m']};
    font-size: 0.65rem;
    color: {v['gold']};
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 15px;
  }}
  .arch-item {{
    margin-bottom: 12px;
  }}
  .arch-item .label {{
    color: {v['steel']};
    font-weight: bold;
    font-family: {v['font_m']};
    font-size: 0.8rem;
    display: block;
  }}
  .arch-item .desc {{
    color: {v['text_muted']};
    font-size: 0.8rem;
  }}

  .footer {{
    display: flex;
    flex-wrap: wrap;
    gap: 16px;
    justify-content: space-between;
    align-items: flex-end;
    border-top: 1px solid rgba(255,255,255,0.05);
    padding-top: 20px;
  }}
  .architect-label {{
    font-family: {v['font_m']};
    font-size: 0.6rem;
    color: {v['text_dim']};
    letter-spacing: 2px;
  }}
  .architect-name {{
    color: {v['text']};
    font-family: {v['font_m']};
    font-size: 0.9rem;
  }}
  .lock {{
    text-align: right;
    animation: pulse 2s infinite;
  }}
  .lock-status {{
    font-family: {v['font_m']};
    font-size: 0.65rem;
    color: {v['danger']};
    letter-spacing: 2px;
    font-weight: bold;
  }}
  .lock-sub {{
    font-family: {v['font_m']};
    font-size: 0.55rem;
    color: {v['text_muted']};
    letter-spacing: 1px;
  }}

  .hint {{
    text-align: center;
    margin-top: 20px;
  }}
  .hint span {{
    background: rgba(229,62,62,0.05);
    border: 1px solid rgba(229,62,62,0.2);
    color: {v['danger']};
    padding: 8px 15px;
    font-family: {v['font_m']};
    font-size: 0.65rem;
    letter-spacing: 2px;
    display: inline-block;
  }}
</style>
</head>
<body>

<div class="card">

  <div class="header">
    <h1>&#x62D;&#x628;&#x631; &#x648;&#x641;&#x643;&#x631;&#x629;</h1>
    <span>INKOS V2026.4 // VELVETCODEX INITIATIVE</span>
  </div>

  <div class="intro">
    Most interfaces are soulless. InkOS is a highly opinionated intelligence terminal
    designed for precision, speed, and ethical rigor. It does not just generate text;
    it refracts intent through specialized cognitive frameworks.
  </div>

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

<div class="hint">
  <span>[&lt;&lt;] ALIGN IDENTITY IN SIDEBAR TO UNLOCK</span>
</div>

</body>
</html>"""

    components.html(html, height=520, scrolling=False)
