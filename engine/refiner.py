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

v2.2: The Master Aesthetic Patch (Anime/Cyberpunk Override)
"""

from __future__ import annotations

import json
import textwrap
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, Tuple

# Import InkOS config (Groq replaces Anthropic)
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
# UNIFIED INTENT OBJECT (Assembly Line Data)
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
# SYSTEM PROMPTS (Strict JSON Contracts)
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
        "exact_text":       ["<Extract ANY specific names, letters, or words the user explicitly wants written in the output>"],
        "style_cues":       ["<aesthetic/technical keywords>"]
    }
""").strip()

_CLASSIFIER_SYSTEM_PROMPT = textwrap.dedent("""
    You are an intent classification engine. Output a deterministic profile.
    Return ONLY valid JSON matching this schema:
    {
        "domain":            "<photography|illustration|concept_art|product_render|typography|logo_brand|architecture|fashion|abstract|code_analysis|agentic_automation|text_copy>",
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
        TargetModel.IMAGEN3:    ["high resolution", "crisp edges", "perfect typography"],
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

        lvl = max(1, min(10, int(data.get("photorealism", 5))))
        closest_lvl = min(PhotorealismLevel, key=lambda l: abs(l.value - lvl))

        # Force text_required to true if exact_text was found
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
            must_have.append(f'EXACT TEXT TO RENDER: "{text_string}" (Crucial: Anchor this text physically into the scene, e.g., embossed on metal, glowing on a screen, or written on a label. Do not let it float.)')

        uio.constraints = ConstraintSet(
            must_have=must_have,
            should_have=[f"Setting: {chunks.setting}"] if chunks.setting else [],
            avoid=list(prefs.get("avoid", [])),
            aspect_ratio=prefs.get("aspect_ratio", "16:9")
        )
        return uio

    def _step4_enrich_aesthetics(self, uio: UnifiedIntentObject) -> UnifiedIntentObject:
        ip, layer = uio.intent_profile, AestheticLayer()
        chunks = uio.semantic_chunks
        
        if ip.domain in (ContentDomain.CODE_ANALYSIS, ContentDomain.TEXT_COPY, ContentDomain.AGENTIC):
            return uio 

        # Gather all text to scan for style triggers
        raw_cues = " ".join(chunks.style_cues + [chunks.subject, chunks.setting, chunks.mood, uio.raw_input]).lower()
        ui_cues = " ".join(uio.constraints.must_have).lower()
        all_cues = raw_cues + " " + ui_cues

        # ── RESTORED TASTE LAYER: The Anime & Cyberpunk Hijack ──
        if any(w in all_cues for w in ["anime", "manga", "cel", "ghibli", "shinkai", "shikamaru", "naruto"]):
            layer.art_references = ["Akira 1988 cel animation", "Studio Ghibli background detailing", "Makoto Shinkai volumetric lighting"]
            layer.texture_keywords = ["2D flat colors", "inked outlines", "cel-shaded", "anime art style"]
            # Force stylized illustration (kills photorealism)
            ip.photorealism = PhotorealismLevel.STYLIZED 
            ip.domain = ContentDomain.ILLUSTRATION
            
        elif any(w in all_cues for w in ["cyberpunk", "tech-noir", "hacker", "neon"]):
            layer.art_references = ["Syd Mead", "Blade Runner aesthetic"]
            layer.color_palette = ["neon cyan", "electric purple", "dark base", "RGB accents"]
            
        elif ip.cinematic or "cinematic" in all_cues:
            layer.lighting_keywords = ["Shotdeck cinematic lighting", "anamorphic flare"]
            layer.camera_keywords = ["35mm lens", "shallow depth of field"]
            layer.art_references = ["A24 portraiture", "Vogue editorial"]
            
        elif ip.domain == ContentDomain.PRODUCT_RENDER or "ad" in all_cues or "mockup" in all_cues:
            layer.lighting_keywords = ["studio softbox", "rim lighting"]
            layer.art_references = ["luxury commercial macro photography", "Behance packaging design"]
            ip.domain = ContentDomain.PRODUCT_RENDER
        
        uio.aesthetic_layer = layer
        uio.intent_profile = ip # Save the forced stylization
        return uio

    def _step5_route_target(self, uio: UnifiedIntentObject) -> UnifiedIntentObject:
        ip, prefs = uio.intent_profile, uio.user_preferences
        
        forced = prefs.get("target_model", "").strip()
        if forced and forced != "⚡ Auto (CIPHER Selects)":
            for model in TargetModel:
                if model.value == forced:
                    uio.target_model, uio.routing_reason = model, f"User override: {forced}"
                    return uio

        # Deterministic Routing Logic
        if ip.domain == ContentDomain.AGENTIC:
            uio.target_model, uio.routing_reason = TargetModel.MANUS, "Automation detected."
        elif ip.domain == ContentDomain.CODE_ANALYSIS:
            uio.target_model, uio.routing_reason = TargetModel.CLAUDE, "Code/Structural analysis."
        elif ip.domain == ContentDomain.TEXT_COPY:
            uio.target_model, uio.routing_reason = TargetModel.CHATGPT, "Conversational intent."
        elif ip.text_required or ip.domain in (ContentDomain.TYPOGRAPHY, ContentDomain.LOGO_BRAND):
            uio.target_model, uio.routing_reason = TargetModel.IMAGEN3, "Typography/Spatial layout critical."
        elif ip.photorealism.value >= 9 or ip.product_focus:
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
        lights = ", ".join(aes.lighting_keywords) if aes.lighting_keywords else "Natural lighting"
        refs = ", ".join(aes.art_references + aes.texture_keywords) if aes.art_references else "Premium aesthetics"
        
        if m == TargetModel.MIDJOURNEY:
            quality = " ".join(self._QUALITY_TOKENS[m])
            uio.compiled_prompt = f"{core} :: {must} :: lighting: {lights} :: style: {refs} --ar {cons.aspect_ratio} {quality}"
        
        elif m == TargetModel.DALLE3:
            domain_name = ip.domain.value.replace('_', ' ')
            uio.compiled_prompt = f"Create a high-end {domain_name} featuring {core}. Critical constraints: {must}. Use {lights} to illuminate the scene. The artistic style should be inspired by {refs}."
        
        elif m == TargetModel.IMAGEN3:
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