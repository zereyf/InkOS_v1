from types import MappingProxyType

QUALITY_TIERS = MappingProxyType({
    "standard": [],
    "premium":  ["ultra polished rendering", "professional composition"],
    "studio":   ["masterpiece quality", "artstation featured", "studio-grade rendering"],
})

STYLE_LIBRARY = MappingProxyType({
    "anime_banner": {
        "art_medium":        "2D anime illustration",
        "render_type":       "high contrast composited wallpaper design",
        "composition_style": "collage banner composition with layered character framing",
        "design_language":   ["esports branding", "anime edit aesthetic", "gaming banner"],
    },
    "dark_editorial": {
        "art_medium":        "stylized manga illustration",
        "render_type":       "graphic poster composite",
        "composition_style": "hero portrait with oversized typography",
        "design_language":   ["streetwear poster", "editorial graphic design"],
    },
    "cinematic_anime": {
        "art_medium":        "premium anime cel-shaded illustration",
        "render_type":       "high fidelity manga colorization",
        "composition_style": "centered portrait framing",
        "design_language":   ["official anime frame", "studio key visual"],
    },
})

AESTHETIC_PRESETS = MappingProxyType({
    "Raw (No Preset)": (
        "No aesthetic filter applied. Follow user description with literal interpretation."
    ),
    "Velvet (Signature)": (
        "AESTHETIC: Tech-Noir Minimalism. PALETTE: Obsidian black #0A0A0A, matte charcoal #1C1C1C, "
        "deep gold #C9A84C, warm amber #D4860A. LIGHTING: Chiaroscuro — single strong key light, hard shadows. "
        "TEXTURE: Brushed metal surfaces, subtle grain overlay. MOOD: Quiet authority."
    ),
    "Scholar (Traditional)": (
        "AESTHETIC: Arabic Heritage and Classical Calligraphy. PALETTE: Aged parchment #F5E6C8, "
        "sandstone #C4A882, emerald green #2D6A4F, deep burgundy #6B2D30. LIGHTING: Natural diffused sunlight. "
        "TEXTURE: Weathered paper grain, geometric Islamic pattern overlays at 10% opacity."
    ),
    "Cyber-Radiant": (
        "AESTHETIC: High-energy cyberpunk technology. PALETTE: Pure black #000000, electric blue #00BFFF, "
        "cyber lime #ADFF2F. LIGHTING: Volumetric neon, colored shadows. TEXTURE: Carbon fiber weave, glitch overlays."
    ),
    "Shonen (Combat)": (
        "AESTHETIC: High-intensity anime action. PALETTE: Deep navy #0A0F1E, electric blue #0066FF, white, cyan. "
        "LIGHTING: Energy emanating from character, impact flash lighting. TEXTURE: Ink splash, speed line motion blur."
    ),
    "Crimson Protocol": (
        "AESTHETIC: Dark tech-noir with crimson dominance. PALETTE: Pure black, blood red #8B0000, crimson. "
        "LIGHTING: Red underlighting, harsh shadows. TEXTURE: HUD interface elements, binary data, signal waves."
    ),
    "Velvet Anime": (
        "AESTHETIC: Premium anime portrait. PALETTE: Cold blue #B0C4DE ambient, warm ivory skin tones, deep shadow. "
        "LIGHTING: Rim lighting from above-right, chiaroscuro contrast. TEXTURE: Clean cel-shading, sharp linework."
    ),
})
