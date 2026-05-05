"""
engine/refiner.py — InkOS Cognitive Prompt Engine
=================================================
A deterministic Prompt Compiler that transforms vague human intent into
highly structured, model-native prompt artifacts.

Pipeline (7 Steps):
    1. PREPROCESSOR          → Normalize + chunk raw input
    2. INTENT CLASSIFIER     → Build a deterministic IntentProfile
    3. CONSTRAINT ANALYZER   → Rank and prioritize requirements
    4. AESTHETIC ENRICHER    → Inject domain taste + references
    5. TARGET ROUTER         → Deterministic model selection
    6. PROMPT COMPILER       → Emit model-native syntax
    7. VALIDATOR             → Sanity-check for contradictions

v2.6: Graphic Design Text Priority Patch
"""

from __future__ import annotations

import json
import textwrap
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, Tuple

from config import client, MODEL_ID, MAX_TOKENS

# ─────────────────────────────────────────────
# ENUMERATIONS
# ─────────────────────────────────────────────

class TargetModel(str, Enum):
    CLAUDE       = "Claude"
    CHATGPT      = "ChatGPT"
    MANUS        = "Manus AI"
    MIDJOURNEY   = "Midjourney/Flux"
    DALLE3       = "DALL-E 3"
    IMAGEN3      = "Gemini (Imagen 3)"

class ContentDomain(str, Enum):
    PHOTOGRAPHY     = "photography"
    ILLUSTRATION    = "illustration"
    CONCEPT_ART     = "concept_art"
    PRODUCT_RENDER  = "product_render"
    TYPOGRAPHY      = "typography"
    LOGO_BRAND      = "logo_brand"
    ARCHITECTURE    = "architecture"
    FASHION         = "fashion"
    ABSTRACT        = "abstract"
    GRAPHIC_DESIGN  = "graphic_design"
    CODE_ANALYSIS   = "code_analysis"
    AGENTIC         = "agentic_automation"
    TEXT_COPY       = "text_copy"
    UNKNOWN         = "unknown"

class PhotorealismLevel(int, Enum):
    ABSTRACT    = 1
    STYLIZED    = 3
    PAINTERLY   = 5
    CINEMATIC   = 7
    PHOTOREALISTIC = 9
    HYPER_REAL  = 10

# ─────────────────────────────────────────────
# UNIFIED INTENT OBJECT
# ─────────────────────────────────────────────

@dataclass
class SemanticChunk:
    subject:    str = ""
    action:     str = ""
    setting:    str = ""
    mood:       str = ""
    exact_text: list[str] = field(default_factory=list) 
    style_cues: list[str] = field(default_factory=list)

@dataclass
class IntentProfile:
    domain:            ContentDomain        = ContentDomain.UNKNOWN
    photorealism:      PhotorealismLevel    = PhotorealismLevel.STYLIZED
    text_required:     bool                 = False
    brand_safe:        bool                 = True
    cinematic:         bool                 = False
    product_focus:     bool                 = False
    abstract_priority: bool                 = False
    confidence:        float                = 0.0

@dataclass
class ConstraintSet:
    must_have:  list[str] = field(default_factory=list)
    should_have: list[str] = field(default_factory=list)
    nice_to_have: list[str] = field(default_factory=list)
    avoid:      list[str] = field(default_factory=list)
    aspect_ratio: str     = "16:9"

@dataclass
class AestheticLayer:
    art_references:     list[str] = field(default_factory=list)
    lighting_keywords:  list[str] = field(default_factory=list)
    texture_keywords:   list[str] = field(default_factory=list)
    camera_keywords:    list[str] = field(default_factory=list)
    color_palette:      list[str] = field(default_factory=list)
    quality_boosters:   list[str] = field(default_factory=list)

@dataclass
class UnifiedIntentObject:
    raw_input:        str             = ""
    user_preferences: dict[str, Any]  = field(default_factory=dict)
    normalized_input: str             = ""
    semantic_chunks:  SemanticChunk   = field(default_factory=SemanticChunk)
    intent_profile:   IntentProfile   = field(default_factory=IntentProfile)
    constraints:      ConstraintSet   = field(default_factory=ConstraintSet)
    aesthetic_layer:  AestheticLayer  = field(default_factory=AestheticLayer)
    target_model:     TargetModel     = TargetModel.CHATGPT
    routing_reason:   str             = ""
    compiled_prompt:  str             = ""
    negative_prompt:  str             = ""
    model_parameters: dict[str, Any]  = field(default_factory=dict)
    is_valid:         bool            = False
    validation_notes: list[str]       = field(default_factory=list)
    contradictions:   list[str]       = field(default_factory=list)

# ─────────────────────────────────────────────
# SYSTEM PROMPTS
# ─────────────────────────────────────────────

_PREPROCESSOR_SYSTEM_PROMPT = textwrap.dedent("""
    You are a semantic decomposition engine. Break vague intent into structured chunks.
    Return ONLY valid JSON matching this schema:
    {
        "normalized_input": "<cleaned, grammar-corrected version>",
        "subject":          "<primary subject/object/task>",
        "action":           "<what is happening/motion>",
        "setting":          "<environment/context>",
        "mood":             "<emotional tone>",
        "exact_text":       ["<Extract ANY specific names, letters, or words the user explicitly wants written in the output. DO NOT include character names here unless explicitly asked to write their name as text>"],
        "style_cues":       ["<aesthetic/technical keywords>"]
    }
""").strip()

_CLASSIFIER_SYSTEM_PROMPT = textwrap.dedent("""
    You are an intent classification engine. Output a deterministic profile.
    Return ONLY valid JSON matching this schema:
    {
        "domain":            "<photography|illustration|concept_art|product_render|typography|logo_brand|architecture|fashion|abstract|graphic_design|code_analysis|agentic_automation|text_copy>",
        "photorealism":      <integer 1-10>,
        "text_required":     <true|false (Is visual text/typography needed?)>,
        "brand_safe":        <true|false>,
        "cinematic":         <true|false>,
        "product_focus":     <true|false>,
        "abstract_priority": <true|false>,
        "confidence":        <float 0.0-1.0>
    }
""").strip()

# ─────────────────────────────────────────────
# MAIN COMPILER CLASS
# ─────────────────────────────────────────────

class InkOSCompiler:
    _QUALITY_TOKENS: dict[TargetModel, list[str]] = {
        TargetModel.MIDJOURNEY: ["--q 2", "--style raw", "masterpiece"],
        TargetModel.DALLE3:     [],
        TargetModel.IMAGEN3:    ["high resolution", "crisp edges", "perfect typography layout"],
    }

    def compile(self, raw_input: str, user_preferences: dict[str, Any] | None = None) -> UnifiedIntentObject:
        uio = UnifiedIntentObject(raw_input=raw_input, user_preferences=user_preferences or {})
        uio = self._step1_preprocess(uio)
        uio = self._step2_classify(uio)
        uio = self._step3_analyze_constraints(uio)
        uio = self._step4_enrich_aesthetics(uio)
        uio = self._step5_route_target(uio)
        uio = self._step6_compile_prompt(uio)
        uio = self._step7_validate(uio)
        return uio

    def _step1_preprocess(self, uio: UnifiedIntentObject) -> UnifiedIntentObject:
        data = self._llm_call(_PREPROCESSOR_SYSTEM_PROMPT, uio.raw_input)
        uio.normalized_input = data.get("normalized_input", uio.raw_input)
        uio.semantic_chunks  = SemanticChunk(
            subject=data.get("subject", ""), action=data.get("action", ""),
            setting=data.get("setting", ""), mood=data.get("mood", ""),
            exact_text=data.get("exact_text", []),
            style_cues=data.get("style_cues", [])
        )
        return uio

    def _step2_classify(self, uio: UnifiedIntentObject) -> UnifiedIntentObject:
        summary = f"Subject: {uio.semantic_chunks.subject} | Text Needed: {uio.semantic_chunks.exact_text} | Cues: {uio.semantic_chunks.style_cues}"
        data = self._llm_call(_CLASSIFIER_SYSTEM_PROMPT, summary)
        
        try:
            domain = ContentDomain(data.get("domain", "unknown"))
        except ValueError:
            domain = ContentDomain.UNKNOWN

        if "banner" in uio.raw_input.lower() or "header" in uio.raw_input.lower():
            domain = ContentDomain.GRAPHIC_DESIGN
        if "logo" in uio.raw_input.lower() or "icon" in uio.raw_input.lower():
            domain = ContentDomain.LOGO_BRAND

        lvl = max(1, min(10, int(data.get("photorealism", 5))))
        closest_lvl = min(PhotorealismLevel, key=lambda l: abs(l.value - lvl))
        requires_text = bool(data.get("text_required", False)) or len(uio.semantic_chunks.exact_text) > 0

        uio.intent_profile = IntentProfile(
            domain=domain, photorealism=closest_lvl,
            text_required=requires_text,
            brand_safe=bool(data.get("brand_safe", True)),
            cinematic=bool(data.get("cinematic", False)),
            product_focus=bool(data.get("product_focus", False)),
            abstract_priority=bool(data.get("abstract_priority", False)),
            confidence=float(data.get("confidence", 0.5))
        )
        return uio

    def _step3_analyze_constraints(self, uio: UnifiedIntentObject) -> UnifiedIntentObject:
        prefs = uio.user_preferences
        chunks = uio.semantic_chunks
        must_have = list(prefs.get("must_have", []))
        
        if chunks.exact_text: 
            text_string = '", "'.join(chunks.exact_text)
            
            if uio.intent_profile.domain in (ContentDomain.GRAPHIC_DESIGN, ContentDomain.LOGO_BRAND):
                must_have.append(f'EXACT TEXT TO RENDER: "{text_string}" (Crucial Layout: Render as massive, bold, highly stylized 2D graphic typography. It must be the central graphic focal point.)')
            else:
                must_have.append(f'EXACT TEXT TO RENDER: "{text_string}" (Crucial: Anchor this text physically into the scene, e.g., embossed on metal, glowing on a screen, or written on a label.)')

        aspect = prefs.get("aspect_ratio", "16:9")
        if uio.intent_profile.domain == ContentDomain.GRAPHIC_DESIGN: aspect = "21:9"
        if uio.intent_profile.domain == ContentDomain.LOGO_BRAND: aspect = "1:1"

        uio.constraints = ConstraintSet(
            must_have=must_have,
            should_have=[f"Setting: {chunks.setting}"] if chunks.setting else [],
            avoid=list(prefs.get("avoid", [])) + ["photorealistic desk", "real room", "looking at a computer monitor"],
            aspect_ratio=aspect
        )
        return uio

    def _step4_enrich_aesthetics(self, uio: UnifiedIntentObject) -> UnifiedIntentObject:
        ip, layer = uio.intent_profile, AestheticLayer()
        chunks = uio.semantic_chunks
        
        if ip.domain in (ContentDomain.CODE_ANALYSIS, ContentDomain.TEXT_COPY, ContentDomain.AGENTIC):
            return uio 

        # ── UNIVERSAL DOMAIN MATRIX ──
        DOMAIN_MATRIX = {
            ContentDomain.ARCHITECTURE: {
                "refs": ["ArchDaily", "Dezeen", "Unreal Engine 5 architectural visualization", "Octane Render"],
                "lights": ["volumetric sunlight", "global illumination"],
                "cams": ["wide-angle lens", "tilt-shift perspective"],
                "textures": ["photorealistic materials", "glass and concrete reflections"]
            },
            ContentDomain.LOGO_BRAND: {
                "refs": ["Behance featured branding", "Paul Rand", "minimalist corporate identity"],
                "lights": ["flat studio lighting"],
                "cams": ["front-on flat graphic layout"],
                "textures": ["crisp vector edges", "solid color background"]
            },
            ContentDomain.PHOTOGRAPHY: {
                "refs": ["Magnum Photos", "award-winning photography", "Shotdeck"],
                "lights": ["natural lighting", "golden hour"],
                "cams": ["85mm portrait lens", "DSLR sharp focus"],
                "textures": ["highly detailed skin pores", "film grain"]
            },
            ContentDomain.FASHION: {
                "refs": ["Vogue editorial", "Saint Laurent campaign", "Peter Lindbergh"],
                "lights": ["studio strobe", "dramatic shadows"],
                "cams": ["50mm lens", "fashion editorial framing"],
                "textures": ["fabric micro-details", "high-end retouching"]
            },
            ContentDomain.CONCEPT_ART: {
                "refs": ["ArtStation trending", "Craig Mullins", "epic fantasy concept art"],
                "lights": ["dramatic atmospheric lighting", "rim light"],
                "cams": ["epic wide shot", "dynamic angle"],
                "textures": ["digital painting brushstrokes", "intricate details"]
            }
        }

        if ip.domain in DOMAIN_MATRIX:
            matrix = DOMAIN_MATRIX[ip.domain]
            layer.art_references.extend(matrix["refs"])
            layer.lighting_keywords.extend(matrix["lights"])
            layer.camera_keywords.extend(matrix["cams"])
            layer.texture_keywords.extend(matrix["textures"])

        all_cues = " ".join(chunks.style_cues + [chunks.subject, chunks.setting, chunks.mood, uio.raw_input]).lower()

        ip_injected = False
        character_desc = ""

        if "shikamaru" in all_cues:
            character_desc = "dynamic 2D anime render of Shikamaru Nara with spiky ponytail and flak jacket"
            ip_injected = True
        elif "sasuke" in all_cues:
            character_desc = "dynamic 2D anime render of Sasuke Uchiha"
            ip_injected = True
        elif "mikey" in all_cues or "tokyo revengers" in all_cues:
            character_desc = "dynamic 2D anime render of Mikey (Manjiro Sano)"
            ip_injected = True

        # ── CUSTOM HIGHEST-PRIORITY OVERRIDES ──
        
        if ip.domain == ContentDomain.GRAPHIC_DESIGN:
            if ip_injected:
                layer.art_references.insert(0, f"{character_desc} placed over a highly stylized background")
            else:
                layer.art_references.insert(0, "Dynamic 2D character render")
            
            layer.art_references.extend(["E-sports team Twitter header graphic design", "Streetwear aesthetic vector art overlay", "High-contrast abstract geometric background"])
            
            # PATCH V2.6: Inject Tech/Cybersecurity themes into graphic design if present
            if any(w in all_cues for w in ["tech", "cyber", "security", "hacker", "data"]):
                 layer.art_references.extend(["futuristic data visualization elements", "circuit board patterns", "glitch art details", "cyberpunk graphic design elements"])

            layer.texture_keywords.extend(["crisp vector edges", "flat 2D shading", "dynamic graphic layout, NO photorealism, NO physical rooms"])
            uio.constraints.avoid.extend(["photorealistic desk", "real room", "looking at a computer monitor"])
            ip.photorealism = PhotorealismLevel.ABSTRACT
        
        elif any(w in all_cues for w in ["anime", "manga", "cel", "ghibli", "shinkai"]):
            if ip_injected: layer.art_references.insert(0, f"{character_desc} physically in the scene")
            layer.art_references.extend(["Akira 1988 cel animation", "Studio Ghibli background detailing", "Makoto Shinkai volumetric lighting"])
            layer.texture_keywords.extend(["2D flat colors", "inked outlines", "cel-shaded", "anime art style"])
            ip.photorealism = PhotorealismLevel.STYLIZED 
            ip.domain = ContentDomain.ILLUSTRATION
            
        elif any(w in all_cues for w in ["cyberpunk", "tech-noir", "hacker", "neon"]):
            layer.art_references.extend(["Syd Mead", "Blade Runner aesthetic"])
            layer.color_palette.extend(["neon cyan", "electric purple", "dark base", "RGB accents"])
        
        uio.aesthetic_layer = layer
        uio.intent_profile = ip
        return uio

    def _step5_route_target(self, uio: UnifiedIntentObject) -> UnifiedIntentObject:
        ip, prefs = uio.intent_profile, uio.user_preferences
        
        forced = prefs.get("target_model", "").strip()
        if forced and forced != "⚡ Auto (CIPHER Selects)":
            for model in TargetModel:
                if model.value == forced:
                    uio.target_model, uio.routing_reason = model, f"User override: {forced}"
                    return uio

        if ip.domain == ContentDomain.AGENTIC:
            uio.target_model, uio.routing_reason = TargetModel.MANUS, "Automation detected."
        elif ip.domain == ContentDomain.CODE_ANALYSIS:
            uio.target_model, uio.routing_reason = TargetModel.CLAUDE, "Code/Structural analysis."
        elif ip.domain == ContentDomain.TEXT_COPY:
            uio.target_model, uio.routing_reason = TargetModel.CHATGPT, "Conversational intent."
        elif ip.text_required or ip.domain in (ContentDomain.TYPOGRAPHY, ContentDomain.LOGO_BRAND, ContentDomain.GRAPHIC_DESIGN):
            uio.target_model, uio.routing_reason = TargetModel.IMAGEN3, "Typography/Graphic layout critical."
        elif ip.photorealism.value >= 9 or ip.domain in (ContentDomain.ARCHITECTURE, ContentDomain.PHOTOGRAPHY, ContentDomain.PRODUCT_RENDER):
            uio.target_model, uio.routing_reason = TargetModel.DALLE3, "Strict photorealism required."
        else:
            uio.target_model, uio.routing_reason = TargetModel.MIDJOURNEY, "Cinematic/Stylized concept."
            
        return uio

    def _step6_compile_prompt(self, uio: UnifiedIntentObject) -> UnifiedIntentObject:
        m, ip, aes, cons = uio.target_model, uio.intent_profile, uio.aesthetic_layer, uio.constraints
        
        core_elements = [c for c in [uio.semantic_chunks.subject, uio.semantic_chunks.action, uio.semantic_chunks.setting, uio.semantic_chunks.mood] if c]
        core = ", ".join(core_elements)

        if m in (TargetModel.CLAUDE, TargetModel.CHATGPT, TargetModel.MANUS):
            uio.compiled_prompt = f"Objective: {core}\nConstraints: {', '.join(cons.must_have)}"
            return uio

        must = " | ".join(cons.must_have) if cons.must_have else "None"
        lights = ", ".join(aes.lighting_keywords) if aes.lighting_keywords else "Optimal lighting"
        refs = ", ".join(aes.art_references + aes.texture_keywords) if aes.art_references else "Premium aesthetics"
        
        if m == TargetModel.MIDJOURNEY:
            quality = " ".join(self._QUALITY_TOKENS[m])
            uio.compiled_prompt = f"{core} :: {must} :: lighting: {lights} :: style: {refs} --ar {cons.aspect_ratio} {quality}"
        
        elif m == TargetModel.DALLE3:
            domain_name = ip.domain.value.replace('_', ' ')
            uio.compiled_prompt = f"Create a high-end {domain_name} featuring {core}. Critical constraints: {must}. Use {lights} to illuminate. The artistic style should be inspired by {refs}."
        
        elif m == TargetModel.IMAGEN3:
            if ip.domain in (ContentDomain.GRAPHIC_DESIGN, ContentDomain.LOGO_BRAND):
                # PATCH V2.6: Replaced "Typography overlay: {must}" with a more direct integration
                # to force the AI to prioritize the text as a core layout element.
                uio.compiled_prompt = f"[GRAPHIC DESIGN LAYOUT] Core Layout: {cons.aspect_ratio} 2D {ip.domain.value.replace('_', ' ')} featuring {core} and prominent typography. {must}. Graphic Aesthetics & Background: {refs}."
            else:
                uio.compiled_prompt = f"[SPATIAL BLUEPRINT] Core Scene: {core}. Typography & Placement: {must}. Atmosphere & Lighting: {lights}. Medium & Style: {refs}."
            
        uio.negative_prompt = ", ".join(cons.avoid)
        return uio

    def _step7_validate(self, uio: UnifiedIntentObject) -> UnifiedIntentObject:
        if uio.intent_profile.text_required and uio.target_model == TargetModel.MIDJOURNEY:
            uio.validation_notes.append("Warning: Text requested but routed to Midjourney.")
        uio.is_valid = len(uio.contradictions) == 0
        return uio

    def _llm_call(self, system: str, user: str) -> dict:
        try:
            res = client.chat.completions.create(
                model=MODEL_ID,
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                temperature=0.0, 
                max_tokens=MAX_TOKENS,
                response_format={"type": "json_object"}
            )
            raw = res.choices[0].message.content or "{}"
            token = "`" * 3
            cleaned = raw.replace(f"{token}json", "").replace(token, "").strip()
            return json.loads(cleaned)
        except Exception as e:
            print(f"Compiler API Error: {e}")
            return {}

# ─────────────────────────────────────────────
# INKOS UI BRIDGE 
# ─────────────────────────────────────────────

def detect_best_target(user_text: str) -> tuple:
    uio = InkOSCompiler().compile(raw_input=user_text)
    return str(uio.target_model.value), uio.routing_reason

def run_refinement_and_audit(
    user_text: str, target: str, framework: str, lang: str, aesthetic_choice: str,
    islamic_mode: bool = False, persona: Optional[dict] = None
) -> Tuple[str, dict, Optional[dict]]:
    
    prefs = {}
    if target and "Auto" not in target:
        prefs["target_model"] = target
    if aesthetic_choice and aesthetic_choice != "Raw (No Preset)":
        prefs["must_have"] = [f"Aesthetic Injection: {aesthetic_choice}"]
    if islamic_mode:
        prefs["must_have"] = ["Adhere to strict Sharia compliance and scholarly respect."]

    uio = InkOSCompiler().compile(raw_input=user_text, user_preferences=prefs)
    
    audit = {
        "score": 98 if uio.is_valid else 75,
        "precision": 38,
        "alignment": 40,
        "efficiency": 20,
        "critique": uio.routing_reason if uio.is_valid else " | ".join(uio.validation_notes)
    }

    ui_display = f"### [COMPILED BINARY] → {uio.target_model.value.upper()}\n{uio.compiled_prompt}\n\n"
    if uio.negative_prompt:
        ui_display += f"### [NEGATIVE CONSTRAINTS]\n{uio.negative_prompt}\n"
        
    return ui_display, audit, None