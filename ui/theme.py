"""
ui/theme.py — Single Source of Truth for CSS Variables
========================================================
v1.0: Extracted from app.py and splash.py.
      - Import CSS_VARS into any file that needs the :root block.
      - Import KEYFRAMES for animations.
      - Import THEME_STYLES for the full injection (vars + keyframes).
"""

# ── CSS Variables ────────────────────────────────────────────────────────────
CSS_VARS = """
<style>
    :root {
        --gold:       #C9A84C;
        --gold-border: rgba(201, 168, 76, 0.3);
        --gold-dim:   rgba(201, 168, 76, 0.6);
        --bg-card:    rgba(18, 18, 18, 0.95);
        --text:       #E2E8F0;
        --text-muted: #A0AEC0;
        --text-dim:   #718096;
        --steel:      #7C9EBF;
        --danger:     #E53E3E;
        --font-m:     'Courier New', Courier, monospace;
        --font-d:     'Georgia', 'Times New Roman', serif;
        --font-a:     'Amiri', serif;
    }
</style>
"""

# ── Keyframe Animations ──────────────────────────────────────────────────────
KEYFRAMES = """
<style>
    @keyframes pulse-gold {
        0%   { box-shadow: 0 0 0 0 rgba(201, 168, 76, 0.7); }
        70%  { box-shadow: 0 0 0 6px rgba(201, 168, 76, 0); }
        100% { box-shadow: 0 0 0 0 rgba(201, 168, 76, 0); }
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
</style>
"""

# ── Full Theme Injection (use this in app.py) ────────────────────────────────
THEME_STYLES = CSS_VARS + KEYFRAMES

# ── Raw variable values (for use inside components.html iframes) ─────────────
# Since iframes can't inherit :root from parent, splash.py inlines these.
VARS = {
    "gold":        "#C9A84C",
    "gold_border": "rgba(201, 168, 76, 0.3)",
    "gold_dim":    "rgba(201, 168, 76, 0.6)",
    "bg_card":     "rgba(18, 18, 18, 0.95)",
    "text":        "#E2E8F0",
    "text_muted":  "#A0AEC0",
    "text_dim":    "#718096",
    "steel":       "#7C9EBF",
    "danger":      "#E53E3E",
    "font_m":      "'Courier New', Courier, monospace",
    "font_d":      "'Georgia', 'Times New Roman', serif",
    "font_a":      "'Amiri', serif",
}
