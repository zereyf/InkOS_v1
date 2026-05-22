"""
ui/tabs/visual_director.py — Visual Director Mode
===================================================
Dedicated image prompt compiler tab.

Walks the user through all 10 VISUAL DIRECTOR LAYERS with guided inputs,
weak/strong examples, and a completeness meter. Assembled brief feeds
directly into stream_refinement() with the correct target format contract.

The key difference from the workspace tab:
  - Workspace: free-form input → CIPHER guesses what layers to apply
  - Visual Director: layer-by-layer structured input → CIPHER compiles
    a brief that is already 80% of the way there before the LLM touches it

This produces consistently elite image prompts because the user is forced
to think in layers — zones, Kelvin temps, hex codes, narrative logic —
rather than typing "make it look cool and cinematic."
"""

from __future__ import annotations

import time
from datetime import datetime, timezone

import streamlit as st

from engine.refiner import stream_refinement
from forge.prompt_assembler import assemble_master_payload, make_dna_context
from state import K
from ui.tabs.workspace import extract_clean_output, _audit_score_component

UTC = timezone.utc

IMAGE_TARGETS = ["Midjourney", "DALL-E", "Stable Diffusion", "FLUX"]

_TARGET_NOTES = {
    "Midjourney":       "Uses :: separators. Strongest for stylized art and anime.",
    "DALL-E":           "Prose paragraphs. Best for editorial and photorealistic.",
    "Stable Diffusion": "Keyword tags + Negative prompt: block. Most customizable.",
    "FLUX":             "Natural language. Best text-in-image and typography support.",
}

_PLACEHOLDERS = {
    "subject": (
        "single male figure, seated upright in minimal dark chair, "
        "one elbow on armrest, fingers loosely curled, eyes closed, "
        "faint smirk — running an empire in his mind while physically at rest"
    ),
    "zone1": "pure #000000 immediate background, dark green gradient vignette 4% opacity — almost invisible, just a color temperature. Role: void that makes character readable.",
    "zone2": "enormous perspective grid receding to vanishing point behind head, fine emerald lines barely visible against black. Role: infinite digital depth.",
    "zone3": "content fragments at 15%-90% opacity, ghost text floating multiple depths, depth blur on most distant. Role: the digital world the character is connected to.",
    "lighting": "zero traditional key light. 3200K emerald rim both shoulders from code. White-green point light from cable connection at head. Face in shadow, 2700K green ambient only.",
    "lens": "85mm equivalent, f/1.8, eye-level +3deg tilt, face-to-torso sharp, background progressive bokeh, far fragments fully dissolved.",
    "composition": "subject centered below midpoint — grounded. Cable vertical axis head to upper-center draws eye upward. Eye path: typography → face → cable → fragments. Negative space upper 40% for content.",
    "face": "high contrast halftone bitmap texture — editorial magazine portrait. Shadows become dot patterns, not gradients.",
    "clothing": "clean sharp anime line art, flat color fills. Dark structured jacket over white shirt.",
    "hands": "photorealistic render, visible knuckle detail, skin texture.",
    "glitch": "GLITCH 1 — Eyes: RGB split, red 2px left, blue 2px right. Story: seeing digital frequencies.\nGLITCH 2 — Left shoulder: displacement block 3px, faint afterimage. Story: body briefly becoming data.\nGLITCH 3 — Cable midpoint: pulse interruption. Story: connection is real and imperfect.",
    "palette": "#000000 pure black — the void.\n#00C853 emerald green — digital world, cable, code.\n#FFFFFF pure white — typography, highlights.\n#2C2C2C deep charcoal — halftone midtones.\nNothing else. Four colors. Discipline.",
    "mood": "Mastery",
    "narrative": "The single cable is powerful because there is only one. A hundred cables says chaos. One cable says mastery.\nThe smirk works because his eyes are closed. Open eyes would be reactive. Closed eyes says he already knows.\nThe green is powerful because everything else is black. In a universe of restraint, one color becomes a statement.\nRestraint is the concept. Every element earns its place. Empty space is controlled silence.",
    "exclusions": "cheap cyberpunk clichés, cluttered neon overload, distorted text, unrealistic anatomy, Matrix ripoffs, mobile game aesthetics, cables everywhere, lens flare, busy background, western cartoon, 3D render, watermark",
}

_EXAMPLES = {
    "subject":   ("dynamic anime character",                "single male, seated, eyes closed, faint smirk — running an empire while at rest"),
    "zone2":     ("futuristic cityscape",                   "rain-slicked Shibuya 02:15 AM, elevated rail midground, neon kanji reflections"),
    "lighting":  ("cinematic lighting",                     "3200K neon underlighting magenta, electric blue rim above-right, zero fill"),
    "lens":      ("low angle",                              "24mm f/2.0, knee-height 25deg up, foreground sharp"),
    "face":      ("anime style",                            "high contrast halftone bitmap — editorial portrait, shadows become dot patterns"),
    "palette":   ("vibrant neon",                           "#000000 void · #00C853 digital · #FFFFFF type — four colors, discipline"),
    "narrative": ("looks cool and cinematic",               "The single cable says more than a hundred ever could. Restraint is the concept."),
}


def _example_note(key: str) -> str:
    if key not in _EXAMPLES:
        return ""
    weak, strong = _EXAMPLES[key]
    return (
        f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:9px;'
        f'margin-bottom:6px;">'
        f'<span style="color:#E57373;">✗ {weak}</span>'
        f'<span style="color:rgba(44,53,69,1);"> &nbsp;→&nbsp; </span>'
        f'<span style="color:#4CAF9A;">✓ {strong}</span></div>'
    )


def _layer_label(num: str, title: str, note: str = "") -> None:
    st.markdown(
        f'<div style="display:flex;align-items:baseline;gap:10px;margin-bottom:4px;">'
        f'<span style="font-family:Cinzel,serif;font-size:1rem;color:#C9A84C;">{num}</span>'
        f'<span style="font-family:IBM Plex Mono,monospace;font-size:10px;'
        f'color:rgba(226,213,188,0.9);letter-spacing:0.12em;text-transform:uppercase;">{title}</span>'
        f'{"<span style='font-family:IBM Plex Mono,monospace;font-size:9px;color:rgba(44,53,69,1);'>" + note + "</span>" if note else ""}'
        f'</div>',
        unsafe_allow_html=True,
    )


def _zone_label(label: str) -> None:
    st.markdown(
        f'<div style="font-family:IBM Plex Mono,monospace;font-size:9px;'
        f'color:#7C9EBF;margin:6px 0 3px;">{label}</div>',
        unsafe_allow_html=True,
    )


def _assemble_brief(layers: dict, target: str) -> str:
    return f"""VISUAL DIRECTOR BRIEF — TARGET: {target}

[LAYER 1 — SUBJECT]
{layers.get('subject', '').strip() or '(not specified)'}

[LAYER 2 — ENVIRONMENT: THREE ZONES]
ZONE 1 (immediate): {layers.get('zone1', '').strip() or '(not specified)'}
ZONE 2 (mid): {layers.get('zone2', '').strip() or '(not specified)'}
ZONE 3 (far): {layers.get('zone3', '').strip() or '(not specified)'}

[LAYER 3 — LIGHTING]
{layers.get('lighting', '').strip() or '(not specified)'}

[LAYER 4 — LENS]
{layers.get('lens', '').strip() or '(not specified)'}

[LAYER 5 — COMPOSITION]
{layers.get('composition', '').strip() or '(not specified)'}

[LAYER 6 — PER-REGION STYLE]
FACE: {layers.get('face', '').strip() or '(not specified)'}
CLOTHING: {layers.get('clothing', '').strip() or '(not specified)'}
HANDS: {layers.get('hands', '').strip() or '(not specified)'}

[LAYER 7 — PALETTE]
{layers.get('palette', '').strip() or '(not specified)'}

[LAYER 8 — GLITCH / EFFECTS]
{layers.get('glitch', '').strip() or 'None.'}

[LAYER 9 — EXCLUSIONS]
{layers.get('exclusions', '').strip() or '(not specified)'}

[LAYER 10 — NARRATIVE LOGIC]
{layers.get('narrative', '').strip() or '(not specified)'}

[MOOD WORD]
{layers.get('mood', '').strip() or '(not specified)'}

Compile the above into a production-grade {target} prompt.
Follow the FORMAT_DIRECTIVE exactly.
All 10 Visual Director layers must appear in the compiled output.
Layer 10 Narrative Logic is mandatory — include it.
For Midjourney: use :: separators between every layer.
For DALL-E: prose paragraphs, end with Avoid: sentence.
For Stable Diffusion: keyword tags + Negative prompt: block.
For FLUX: layered natural language paragraphs.
""".strip()


def render_visual_director() -> None:

    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;
                font-family:'IBM Plex Mono',monospace;font-size:0.7rem;
                color:#C9A84C;letter-spacing:0.2em;text-transform:uppercase;
                border-bottom:1px solid rgba(201,168,76,0.15);
                padding-bottom:12px;margin-bottom:24px;">
        <span style="width:7px;height:7px;border-radius:50%;background:#C9A84C;
                     box-shadow:0 0 6px #C9A84C;flex-shrink:0;"></span>
        VISUAL DIRECTOR
        <span style="margin-left:auto;font-size:9px;color:rgba(44,53,69,1);">
            10-LAYER IMAGE PROMPT COMPILER
        </span>
    </div>
    """, unsafe_allow_html=True)

    # Target
    c1, c2 = st.columns([1, 2])
    with c1:
        target = st.selectbox(
            "Target", IMAGE_TARGETS, key="vd_target",
            label_visibility="collapsed",
        )
    with c2:
        st.markdown(
            f'<div style="font-family:IBM Plex Mono,monospace;font-size:10px;'
            f'color:rgba(124,158,191,0.8);padding-top:10px;">'
            f'{_TARGET_NOTES.get(target, "")}</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    layers: dict = {}

    # ── Layer 1 — Subject ─────────────────────────────────────────────────────
    with st.expander("01 — SUBJECT", expanded=True):
        _layer_label("01", "SUBJECT", "anatomy-level · behavioral expression · no adjectives")
        st.markdown(_example_note("subject"), unsafe_allow_html=True)
        layers["subject"] = st.text_area("s1", height=90,
            placeholder=_PLACEHOLDERS["subject"],
            label_visibility="collapsed", key="vd_s1")

    # ── Layer 2 — Environment (3 zones) ───────────────────────────────────────
    with st.expander("02 — ENVIRONMENT — THREE ZONES", expanded=True):
        _layer_label("02", "ENVIRONMENT", "three named depth zones, each with a role")
        st.markdown(_example_note("zone2"), unsafe_allow_html=True)
        _zone_label("ZONE 1 — Immediate background (role: ___)")
        layers["zone1"] = st.text_area("s_z1", height=65,
            placeholder=_PLACEHOLDERS["zone1"],
            label_visibility="collapsed", key="vd_z1")
        _zone_label("ZONE 2 — Mid background (role: ___)")
        layers["zone2"] = st.text_area("s_z2", height=65,
            placeholder=_PLACEHOLDERS["zone2"],
            label_visibility="collapsed", key="vd_z2")
        _zone_label("ZONE 3 — Far background (role: ___)")
        layers["zone3"] = st.text_area("s_z3", height=65,
            placeholder=_PLACEHOLDERS["zone3"],
            label_visibility="collapsed", key="vd_z3")

    # ── Layer 3 — Lighting ────────────────────────────────────────────────────
    with st.expander("03 — LIGHTING", expanded=False):
        _layer_label("03", "LIGHTING", "Kelvin temps required · no mood adjectives")
        st.markdown(_example_note("lighting"), unsafe_allow_html=True)
        layers["lighting"] = st.text_area("s3", height=90,
            placeholder=_PLACEHOLDERS["lighting"],
            label_visibility="collapsed", key="vd_s3")

    # ── Layer 4 — Lens ────────────────────────────────────────────────────────
    with st.expander("04 — LENS", expanded=False):
        _layer_label("04", "LENS", "focal length · aperture · angle in degrees")
        st.markdown(_example_note("lens"), unsafe_allow_html=True)
        layers["lens"] = st.text_area("s4", height=75,
            placeholder=_PLACEHOLDERS["lens"],
            label_visibility="collapsed", key="vd_s4")

    # ── Layer 5 — Composition ─────────────────────────────────────────────────
    with st.expander("05 — COMPOSITION", expanded=False):
        _layer_label("05", "COMPOSITION", "named framing rule · eye movement path · negative space location")
        layers["composition"] = st.text_area("s5", height=90,
            placeholder=_PLACEHOLDERS["composition"],
            label_visibility="collapsed", key="vd_s5")

    # ── Layer 6 — Per-region style ────────────────────────────────────────────
    with st.expander("06 — PER-REGION STYLE", expanded=True):
        _layer_label("06", "STYLE / RENDER", "assign separately: face · clothing · hands")
        st.markdown(_example_note("face"), unsafe_allow_html=True)
        _zone_label("FACE treatment")
        layers["face"] = st.text_area("s6f", height=55,
            placeholder=_PLACEHOLDERS["face"],
            label_visibility="collapsed", key="vd_s6f")
        _zone_label("CLOTHING treatment")
        layers["clothing"] = st.text_area("s6c", height=55,
            placeholder=_PLACEHOLDERS["clothing"],
            label_visibility="collapsed", key="vd_s6c")
        _zone_label("HANDS treatment")
        layers["hands"] = st.text_area("s6h", height=45,
            placeholder=_PLACEHOLDERS["hands"],
            label_visibility="collapsed", key="vd_s6h")

    # ── Layer 7 — Palette ─────────────────────────────────────────────────────
    with st.expander("07 — PALETTE", expanded=True):
        _layer_label("07", "PALETTE", "hex codes · max 4 colors · state role of each · end with 'Discipline'")
        st.markdown(_example_note("palette"), unsafe_allow_html=True)
        layers["palette"] = st.text_area("s7", height=100,
            placeholder=_PLACEHOLDERS["palette"],
            label_visibility="collapsed", key="vd_s7")

    # ── Layer 8 — Glitch ──────────────────────────────────────────────────────
    with st.expander("08 — GLITCH / EFFECTS  (optional)", expanded=False):
        _layer_label("08", "GLITCH / EFFECTS", "max 3 moments · each needs location + magnitude + narrative purpose")
        layers["glitch"] = st.text_area("s8", height=90,
            placeholder=_PLACEHOLDERS["glitch"],
            label_visibility="collapsed", key="vd_s8")

    # ── Layer 9 — Exclusions ──────────────────────────────────────────────────
    with st.expander("09 — EXCLUSIONS", expanded=False):
        _layer_label("09", "EXCLUSIONS", "name specific tropes · not generic 'bad stuff'")
        layers["exclusions"] = st.text_area("s9", height=70,
            placeholder=_PLACEHOLDERS["exclusions"],
            label_visibility="collapsed", key="vd_s9")

    # ── Layer 10 — Narrative Logic ────────────────────────────────────────────
    with st.expander("10 — NARRATIVE LOGIC", expanded=True):
        _layer_label("10", "NARRATIVE LOGIC", "WHY each element works · the most important layer")
        st.markdown(_example_note("narrative"), unsafe_allow_html=True)
        st.markdown(
            '<div style="font-family:IBM Plex Mono,monospace;font-size:9px;'
            'color:rgba(201,168,76,0.6);margin-bottom:5px;">'
            'Don\'t describe what things look like. Explain why they are powerful.<br>'
            '"The single cable is powerful because there is only one."</div>',
            unsafe_allow_html=True,
        )
        layers["narrative"] = st.text_area("s10", height=110,
            placeholder=_PLACEHOLDERS["narrative"],
            label_visibility="collapsed", key="vd_s10")

    # Mood word
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    mc, _ = st.columns([1, 3])
    with mc:
        st.markdown(
            '<div style="font-family:IBM Plex Mono,monospace;font-size:9px;'
            'color:rgba(44,53,69,1);letter-spacing:0.15em;text-transform:uppercase;'
            'margin-bottom:3px;">MOOD WORD (one word)</div>',
            unsafe_allow_html=True,
        )
        layers["mood"] = st.text_input("s_mood", value="",
            placeholder="Mastery",
            label_visibility="collapsed", key="vd_mood")

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # Completeness meter
    required = ["subject", "zone1", "zone2", "zone3",
                "lighting", "lens", "face", "palette", "narrative"]
    filled   = sum(1 for k in required if layers.get(k, "").strip())
    pct      = int((filled / len(required)) * 100)
    bc       = "#4CAF9A" if pct >= 80 else "#C9A84C" if pct >= 50 else "#E57373"

    st.markdown(f"""
    <div style="margin-bottom:12px;">
        <div style="display:flex;justify-content:space-between;
                    font-family:IBM Plex Mono,monospace;font-size:9px;
                    color:rgba(44,53,69,1);margin-bottom:4px;">
            <span>LAYER COMPLETION</span>
            <span style="color:{bc};">{filled}/{len(required)} required layers</span>
        </div>
        <div style="height:2px;background:rgba(255,255,255,0.04);
                    border-radius:1px;overflow:hidden;">
            <div style="height:100%;width:{pct}%;background:{bc};
                         transition:width 0.3s ease;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    compile_clicked = st.button(
        "⚡  COMPILE VISUAL PROMPT",
        type="primary",
        use_container_width=True,
        key="vd_compile",
        disabled=(filled < 3),
    )

    if filled < 3:
        st.markdown(
            '<div style="font-family:IBM Plex Mono,monospace;font-size:9px;'
            'color:rgba(44,53,69,1);text-align:center;margin-top:4px;">'
            'Minimum: Subject + one Zone + Palette</div>',
            unsafe_allow_html=True,
        )

    if compile_clicked:
        brief   = _assemble_brief(layers, target)
        dna_ctx = make_dna_context(
            ink    = str(st.session_state.get(K.INK_DNA)   or ""),
            intel  = str(st.session_state.get(K.INTEL_DNA) or ""),
            hikmah = str(st.session_state.get(K.HIKMAH_DNA) or ""),
        )
        cfg = {
            "target_model":    target,
            "framework":       "Visual Director",
            "source_lang":     "English",
            "hikmah_style":    "None",
            "aesthetic_choice": st.session_state.get(K.AESTHETIC_CHOICE, "Default"),
            "active_persona":  st.session_state.get(K.ACTIVE_PERSONA),
        }
        payload = assemble_master_payload(brief, cfg, dna_ctx)

        t0 = time.time()
        result: dict = {}

        # Consume stream silently — user never sees raw tokens
        with st.spinner("❖ Compiling..."):
            for _ in stream_refinement(
                master_payload   = payload,
                target           = target,
                framework        = "Visual Director",
                lang             = "English",
                aesthetic_choice = cfg["aesthetic_choice"],
                hikmah_style     = "None",
                skip_security    = True,
                result           = result,
            ):
                pass

        latency_ms = int((time.time() - t0) * 1000)
        raw        = result.get("refined", "")
        audit      = result.get("audit",   {})
        error      = result.get("error")

        if error and not raw:
            st.error(error)
            return

        clean = extract_clean_output(raw)
        score = (audit or {}).get("score", 0)

        st.session_state["vd_last_output"]  = clean
        st.session_state["vd_last_audit"]   = audit
        st.session_state["vd_last_latency"] = latency_ms
        st.session_state["vd_last_corrected"] = result.get("corrected", False)
        st.session_state[K.PROMPT_COUNT] = st.session_state.get(K.PROMPT_COUNT, 0) + 1

        history = st.session_state.get(K.HISTORY, [])
        history.append({
            "id":         f"VD_{len(history)+1:03d}",
            "time":       datetime.now(UTC).strftime("%H:%M:%S"),
            "timestamp":  datetime.now(UTC).isoformat(),
            "title":      f"[{target}] {layers.get('subject','Visual')[:35]}",
            "input":      brief[:200],
            "output":     clean,
            "intent":     f"Visual Director — {target}",
            "asset":      clean,
            "target":     target,
            "framework":  "Visual Director",
            "aesthetic":  "Visual Director Mode",
            "score":      score,
            "latency":    f"{latency_ms}ms",
            "density":    "N/A",
            "word_count": str(len(clean.split())),
            "tone":       "VISUAL",
            "icon":       "◈",
            "pattern":    "VISUAL_DIRECTOR",
            "palette":    [],
        })
        st.session_state[K.HISTORY] = history[-50:]

    # Output panel
    output   = st.session_state.get("vd_last_output")
    audit    = st.session_state.get("vd_last_audit", {})
    lat      = st.session_state.get("vd_last_latency", 0)
    corrected = st.session_state.get("vd_last_corrected", False)

    if not output:
        st.markdown("""
        <div style="border:1px dashed rgba(255,255,255,0.06);border-radius:8px;
                    padding:40px 20px;text-align:center;margin-top:16px;">
            <div style="font-family:'IBM Plex Mono',monospace;font-size:0.65rem;
                        color:rgba(44,53,69,1);letter-spacing:0.15em;
                        text-transform:uppercase;">
                [ ◈ ]  Compiled prompt will appear here
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    st.markdown("""
    <div style="display:flex;align-items:center;gap:8px;margin:16px 0 10px;">
        <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;
                    color:#C9A84C;letter-spacing:0.2em;text-transform:uppercase;">
            COMPILED OUTPUT
        </div>
        <div style="flex:1;height:1px;background:linear-gradient(90deg,
                    rgba(201,168,76,0.28),transparent);"></div>
    </div>
    """, unsafe_allow_html=True)

    _audit_score_component(audit)

    if corrected:
        st.markdown(
            '<div style="font-family:IBM Plex Mono,monospace;font-size:9px;'
            'color:#4CAF9A;margin-bottom:8px;">'
            '✓ Format auto-corrected for target model</div>',
            unsafe_allow_html=True,
        )

    st.text_area(
        "vd_out", value=output, height=340,
        key="vd_out_area", label_visibility="collapsed",
    )

    st.markdown(
        f'<div style="font-family:IBM Plex Mono,monospace;font-size:10px;'
        f'color:rgba(44,53,69,1);margin-top:-4px;margin-bottom:10px;">'
        f'{len(output.split()):,} words · {len(output):,} chars · {lat}ms</div>',
        unsafe_allow_html=True,
    )


# ── GUIDE CONTENT (used by guide.py) ─────────────────────────────────────────
VISUAL_DIRECTOR_GUIDE = {
    "what": (
        "A 10-layer structured image prompt compiler. "
        "Instead of typing a description and hoping CIPHER applies the right layers, "
        "you fill each layer explicitly — zones, Kelvin temps, hex codes, narrative logic — "
        "and CIPHER compiles it into production-grade syntax for your target model."
    ),
    "why": (
        "Most image prompt tools treat all models the same. They are not. "
        "Midjourney needs :: separators and photometric specs. "
        "DALL-E needs prose paragraphs with an Avoid: close. "
        "Stable Diffusion needs keyword tags and a Negative prompt: block. "
        "Visual Director enforces the correct format for each."
    ),
    "layers": [
        ("01 SUBJECT",        "Anatomy-level. Behavioral expression. No adjectives."),
        ("02 ENVIRONMENT",    "Three named zones: immediate / mid / far. Each has a role."),
        ("03 LIGHTING",       "Kelvin temperatures required. No mood adjectives."),
        ("04 LENS",           "Focal length + aperture + camera angle in degrees."),
        ("05 COMPOSITION",    "Named framing rule. Eye movement path. Negative space location."),
        ("06 STYLE",          "Per-region: face treatment, clothing treatment, hands treatment."),
        ("07 PALETTE",        "Hex codes only. Max 4 colors. Role of each stated."),
        ("08 GLITCH",         "Optional. Max 3 moments. Each needs narrative purpose."),
        ("09 EXCLUSIONS",     "Named aesthetic tropes. Not generic 'bad stuff'."),
        ("10 NARRATIVE LOGIC","WHY each element works. The most important layer."),
    ],
    "tip": (
        "Layer 10 is the difference between a visual description and a creative director's "
        "vision. 'The single cable is powerful because there is only one.' "
        "Give the model the reasoning and it handles every unspecified detail correctly."
    ),
}
