"""
engine/refiner.py - InkOS Cognitive Prompt Engine
=================================================
v7.1: THE TYPOGRAPHY & EXTRACTION PATCH
- Fixed: Python string `.join()` bug causing spaced out letters.
- Fixed: LLM hallucination extracting the entire prompt as text.
- Added: Hardcoded Identity Protection for "Ameer".

"""

from __future__ import annotations
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, Tuple

from config import client, MODEL_ID, MAX_TOKENS, STYLE_LIBRARY, QUALITY_TIERS, TARGET_GUIDES, DOMAIN_KNOWLEDGE
from engine.cognitive_map import detect_arabic_pattern
from i18n.translations import t

# ---------------------------------------------
# DATA MODELS
# ---------------------------------------------

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
    GRAPHIC_DESIGN  = "graphic_design"
    TEXT_COPY       = "text_copy"
    CODE_ANALYSIS   = "code_analysis"
    MARKETING       = "marketing"
    DATA_ANALYSIS   = "data_analysis"
    ACADEMIC        = "academic_research"
    PRODUCTIVITY    = "productivity"
    UNKNOWN         = "unknown"

@dataclass
class UnifiedIntentObject:
    raw_input: str = ""
    user_preferences: dict = field(default_factory=dict)
    subject: str = ""
    exact_text: list[str] = field(default_factory=list)
    domain: ContentDomain = ContentDomain.UNKNOWN
    target_model: TargetModel = TargetModel.CHATGPT
    style_dna: dict = field(default_factory=dict)
    is_visual_task: bool = False
    compiled_prompt: str = ""
    negative_prompt: str = ""
    intelligence_score: int = 0

# ---------------------------------------------
# DOMAIN EXPERT MODULES (Strategy Pattern)
# ---------------------------------------------

class BaseExpert:
    def assemble(self, uio: UnifiedIntentObject) -> str:
        raise NotImplementedError

class VisualExpert(BaseExpert):
    def assemble(self, uio: UnifiedIntentObject) -> str:
        dna = uio.style_dna
        quality = ", ".join(QUALITY_TIERS.get("studio", []))
        
        # The spacing bug is fixed here because exact_text is strictly a list now
        txt = f'EXACT TEXT: "{" ".join(uio.exact_text)}"' if uio.exact_text else ""
        
        if uio.target_model == TargetModel.IMAGEN3:
            h = "[GRAPHIC DESIGN LAYOUT]" if uio.domain == ContentDomain.GRAPHIC_DESIGN else "[SPATIAL BLUEPRINT]"
            details = [f"Subject: {uio.subject}", txt, f"Style: {dna.get('art_medium', 'Anime')}", f"FX: {', '.join(dna.get('fx_elements', []))}" if dna.get('fx_elements') else "", f"Fidelity: {quality}"]
            return f"{h} " + ". ".join(filter(None, details)) + "."
        
        elif uio.target_model == TargetModel.MIDJOURNEY:
            parts = [uio.subject, txt, dna.get("art_medium"), quality]
            return " :: ".join(filter(None, parts)) + " --ar 16:9"
        
        else: # DALLE-3
            return f"Create a highly detailed visual of {uio.subject}. {txt} Style inspired by {dna.get('art_medium', 'premium concepts')}. Quality: {quality}."

class CodeExpert(BaseExpert):
    def assemble(self, uio: UnifiedIntentObject) -> str:
        framework = uio.user_preferences.get("framework", "Technical (Zero-Shot)")
        rules = DOMAIN_KNOWLEDGE["code_analysis"]
        return (
            f"<role>Senior Staff Software Engineer</role>\n"
            f"<objective>{uio.raw_input}</objective>\n"
            f"<technical_requirements>\n{rules}\n</technical_requirements>\n"
            f"<framework>{framework}</framework>\n"
            f"<instructions>Execute the request. Provide production-ready code followed by complexity analysis.</instructions>"
        )

class CopywritingExpert(BaseExpert):
    def assemble(self, uio: UnifiedIntentObject) -> str:
        framework = uio.user_preferences.get("framework", "Professional (RACE)")
        rules = DOMAIN_KNOWLEDGE["text_copy"]
        return (
            f"You are an Elite Copywriter & Content Strategist.\n\n"
            f"### OBJECTIVE\n{uio.raw_input}\n\n"
            f"### PROFESSIONAL STANDARDS\n{rules}\n\n"
            f"### FRAMEWORK: {framework}\nApply this logical framework to structure your response.\n\n"
            f"### EXECUTION\nDeliver a comprehensive, perfectly formatted output."
        )

class MarketingExpert(BaseExpert):
    def assemble(self, uio: UnifiedIntentObject) -> str:
        rules = DOMAIN_KNOWLEDGE["marketing"]
        return (
            f"You are a Chief Marketing Officer & SEO Expert.\n\n"
            f"### OBJECTIVE\n{uio.raw_input}\n\n"
            f"### CONVERSION & HOOK STRATEGY\n{rules}\n\n"
            f"### EXECUTION\nFocus on scroll-stopping hooks, high engagement, and psychological triggers."
        )

class DataScienceExpert(BaseExpert):
    def assemble(self, uio: UnifiedIntentObject) -> str:
        rules = DOMAIN_KNOWLEDGE["data_analysis"]
        return (
            f"<role>Lead Data Scientist & Systems Architect</role>\n"
            f"<objective>{uio.raw_input}</objective>\n"
            f"<data_standards>\n{rules}\n</data_standards>\n"
            f"<instructions>Execute with strict mathematical rigor. Explain formulas and schemas step-by-step.</instructions>"
        )

class ResearchExpert(BaseExpert):
    def assemble(self, uio: UnifiedIntentObject) -> str:
        rules = DOMAIN_KNOWLEDGE["academic_research"]
        return (
            f"<role>Tenured Academic Researcher & Analyst</role>\n"
            f"<objective>{uio.raw_input}</objective>\n"
            f"<scholarly_standards>\n{rules}\n</scholarly_standards>\n"
            f"<instructions>Synthesize information objectively. Use formal academic structuring. Provide empirical backing.</instructions>"
        )

class ProductivityExpert(BaseExpert):
    def assemble(self, uio: UnifiedIntentObject) -> str:
        rules = DOMAIN_KNOWLEDGE["productivity"]
        return (
            f"You are an Elite Executive Coach & Productivity Engineer.\n\n"
            f"### OBJECTIVE\n{uio.raw_input}\n\n"
            f"### OPTIMIZATION RULES\n{rules}\n\n"
            f"### EXECUTION\nOutput highly actionable, frictionless steps. Eliminate overwhelm."
        )

# ---------------------------------------------
# THE CORE ENGINE
# ---------------------------------------------

class InkOSCompiler:
    def __init__(self):
        self.experts = {
            ContentDomain.CODE_ANALYSIS: CodeExpert(),
            ContentDomain.TEXT_COPY: CopywritingExpert(),
            ContentDomain.MARKETING: MarketingExpert(),
            ContentDomain.DATA_ANALYSIS: DataScienceExpert(),
            ContentDomain.ACADEMIC: ResearchExpert(),
            ContentDomain.PRODUCTIVITY: ProductivityExpert(),
            ContentDomain.UNKNOWN: CopywritingExpert(),
        }
        self.visual_expert = VisualExpert()

    def compile(self, raw_input: str, user_preferences: dict | None = None) -> UnifiedIntentObject:
        uio = UnifiedIntentObject(raw_input=raw_input, user_preferences=user_preferences or {})
        low = raw_input.lower()

        # 1. SEMANTIC EXTRACTION & DOMAIN ROUTING
        system = """Extract 'subject' and 'exact_text' (MUST be a list of strings containing ONLY explicit names, titles, or quoted words meant to be written as typography. Do NOT extract the whole prompt). 
        Determine 'is_visual_task' (bool).
        Determine 'domain' string based on these strict rules:
        - If programming/coding -> 'code_analysis'
        - If ads/social/SEO/sales -> 'marketing'
        - If Excel/SQL/math/data -> 'data_analysis'
        - If studying/summarizing/science -> 'academic_research'
        - If scheduling/routines/advice -> 'productivity'
        - Else -> 'text_copy'. 
        Output strictly JSON."""
        
        data = self._llm_call(system, raw_input)
        
        uio.subject = data.get("subject", raw_input)
        
        # THE FIX: Type Check the exact_text to prevent Python String Join Bugs
        ext_text = data.get("exact_text", [])
        if isinstance(ext_text, str):
            uio.exact_text = [ext_text] if ext_text.strip() else []
        elif isinstance(ext_text, list):
            uio.exact_text = [str(t) for t in ext_text if t.strip()]
        else:
            uio.exact_text = []

        uio.is_visual_task = data.get("is_visual_task", False)
        
        try:
            uio.domain = ContentDomain(data.get("domain", "text_copy"))
        except ValueError:
            uio.domain = ContentDomain.TEXT_COPY

        # Hard Visual Keyword Guardrail
        if any(w in low for w in ["make", "draw", "generate", "image", "banner", "header", "poster", "watch", "logo"]):
            uio.is_visual_task = True

        # 2. VISUAL DNA MAPPING
        if uio.is_visual_task:
            if "banner" in low or "header" in low:
                uio.domain = ContentDomain.GRAPHIC_DESIGN
                uio.style_dna = STYLE_LIBRARY.get("anime_banner", {}).copy()
            elif "editorial" in low or "poster" in low:
                uio.domain = ContentDomain.ILLUSTRATION
                uio.style_dna = STYLE_LIBRARY.get("dark_editorial", {}).copy()
            else:
                uio.domain = ContentDomain.ILLUSTRATION
            
            uio = self._apply_intelligence(uio)

        # 3. ROUTING
        uio = self._route_target(uio)
        
        # 4. EXPERT ASSEMBLY
        if uio.is_visual_task:
            uio.compiled_prompt = self.visual_expert.assemble(uio)
        else:
            expert = self.experts.get(uio.domain, self.experts[ContentDomain.TEXT_COPY])
            uio.compiled_prompt = expert.assemble(uio)
            
        return uio

    def _apply_intelligence(self, uio: UnifiedIntentObject) -> UnifiedIntentObject:
        low = uio.raw_input.lower()
        hits = 0
        
        # 1. Identity Protection (Ameer)
        if "ameer" in low and not any("ameer" in t.lower() for t in uio.exact_text):
            uio.exact_text.append("Ameer")
            hits += 1

        # 2. Character Protection (Shikamaru)
        if "shikamaru" in low:
            uio.style_dna["art_medium"] = "Dynamic 2D anime render of Shikamaru Nara (Konoha Vest)"
            uio.exact_text = [t for t in uio.exact_text if t.lower() != "shikamaru"]
            hits += 1
            
        # 3. Theme Protection (Cyber)
        if any(w in low for w in ["tech", "cyber", "security", "hacker"]):
            uio.style_dna["fx_elements"] = ["circuit board patterns", "data streams", "glitch distortion"]
            hits += 1
            
        if uio.exact_text: hits += 1
        uio.intelligence_score = hits
        return uio

    def _route_target(self, uio: UnifiedIntentObject) -> UnifiedIntentObject:
        forced_target = uio.user_preferences.get("target")
        if forced_target and "Auto" not in forced_target:
            try:
                uio.target_model = TargetModel(forced_target)
                return uio
            except ValueError:
                pass

        if not uio.is_visual_task: 
            if uio.domain in [ContentDomain.CODE_ANALYSIS, ContentDomain.DATA_ANALYSIS, ContentDomain.ACADEMIC]:
                uio.target_model = TargetModel.CLAUDE
            else:
                uio.target_model = TargetModel.CHATGPT
        elif uio.domain == ContentDomain.GRAPHIC_DESIGN or uio.exact_text: 
            uio.target_model = TargetModel.IMAGEN3
        else: 
            uio.target_model = TargetModel.MIDJOURNEY
        return uio

    def _llm_call(self, system: str, user: str) -> dict:
        try:
            res = client.chat.completions.create(model=MODEL_ID, messages=[{"role": "system", "content": system}, {"role": "user", "content": user}], temperature=0.0, response_format={"type": "json_object"})
            return json.loads(res.choices[0].message.content or "{}")
        except: return {}

# ---------------------------------------------
# UI BRIDGE 
# ---------------------------------------------

def detect_best_target(user_text: str) -> tuple:
    uio = InkOSCompiler().compile(user_text)
    return str(uio.target_model.value), f"{uio.domain.name.replace('_', ' ').title()} Engine Activated."

def run_refinement_and_audit(user_text: str, target: str, framework: str, lang: str, aesthetic_choice: str, islamic_mode: bool = False, persona: Optional[dict] = None) -> Tuple[str, dict, Optional[dict]]:
    prefs = {
        "target": target,
        "framework": framework,
        "lang": lang,
        "islamic_mode": islamic_mode,
        "persona": persona
    }

    pattern = None
    if lang == "Arabic (العربية)":
        pattern = detect_arabic_pattern(user_text)

    uio = InkOSCompiler().compile(user_text, user_preferences=prefs)
    
    prec = 20 if uio.subject else 0
    prec += 20 if uio.exact_text else 10
    align = 40 if uio.is_visual_task else 35
    eff = min(20, 10 + (uio.intelligence_score * 5))

    audit = {
        "score": 98 if uio.is_visual_task else 95,
        "precision": prec,
        "alignment": align,
        "efficiency": eff,
        "critique": "Visual DNA mapped to layout." if uio.is_visual_task else f"Expert Module active: {uio.domain.value.upper()}"
    }

    ui_display = f"### [COMPILED BINARY] -> {uio.target_model.value.upper()}\n{uio.compiled_prompt}\n\n"
    if uio.negative_prompt:
        ui_display += f"### [NEGATIVE CONSTRAINTS]\n{uio.negative_prompt}\n"
        
    return ui_display, audit, pattern