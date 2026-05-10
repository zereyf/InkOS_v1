"""
i18n/translations.py — UI Translation System
==============================================
v20.2: Linguistic Parity Patch.
       - FIXED: Added missing Optional import from typing.
       - FIXED: Deduplicated translation keys in English dictionary.
       - ADDED: Zenith Edition keys (Hikmah Style, Aesthetics, Personas).
       - STABLE: Armored translation helper with recursive fallback.
"""

import streamlit as st
from typing import Optional # 🟢 RESTORED
from state import K

# ── LANGUAGE REGISTRY ─────────────────────────────────────────────────────────
LANGUAGES: list = [
    {"code": "en", "label": "EN", "flag": "🇬🇧", "name": "English",  "dir": "ltr"},
    {"code": "ar", "label": "AR", "flag": "🇸🇦", "name": "العربية",  "dir": "rtl"},
    {"code": "fr", "label": "FR", "flag": "🇫🇷", "name": "Français", "dir": "ltr"},
]

DEFAULT_LANG = "en"

# ── TRANSLATION DICTIONARIES ──────────────────────────────────────────────────
TRANSLATIONS: dict = {

    # ── ENGLISH ───────────────────────────────────────────────────────────────
    "en": {
        "app_name":             "InkOS",
        "app_subtitle":         "Arabic Cognitive Prompt Engine",
        "app_tagline":          "حبر وفكرة. Ink & Ideas.",

        # Sidebar HUD & Tabs
        "session_runs":         "Runs",
        "session_remaining":    "Remaining",
        "last_saved":           "Last Saved",
        "reset_session":        "Reset Session",
        "tab_workspace":        "WORKSPACE",
        "tab_vault":            "🔒 VAULT",
        "tab_forge":            "🎭 FORGE",
        "tab_archive":          "ARCHIVE",
        "tab_security":         "SECURITY LOG",
        "tab_cognitive_map":    "COGNITIVE MAP",
        "tab_guide":            "GUIDE",
        
        # Logic Configuration
        "logic_config":         "⚙️ Logic Configuration",
        "logic_framework":      "Framework",
        "active_persona":       "Active Persona",
        "aesthetic_preset":     "Aesthetic",
        "hikmah_style":         "Hikmah Style",
        
        # Workspace HUD
        "execute_btn":          "⚡  Execute Refinement",
        "precision":            "Precision",
        "alignment":            "Alignment",
        "efficiency":           "Efficiency",
    },

    # ── ARABIC ────────────────────────────────────────────────────────────────
    "ar": {
        "app_name":             "إنك أو إس",
        "app_subtitle":         "محرك الخرائط المعرفية العربية",
        "app_tagline":          "حبر وفكرة.",

        # Sidebar HUD & Tabs
        "session_runs":         "التشغيلات",
        "session_remaining":    "المتبقي",
        "last_saved":           "آخر حفظ",
        "reset_session":        "إعادة تعيين الجلسة",
        "tab_workspace":        "مساحة العمل",
        "tab_vault":            "🔒 الخزينة",
        "tab_forge":            "🎭 المصنع",
        "tab_archive":          "الأرشيف",
        "tab_security":         "سجل الأمان",
        "tab_cognitive_map":    "الخريطة المعرفية",
        "tab_guide":            "الدليل",

        # Logic Configuration
        "logic_config":         "⚙️ إعدادات المنطق",
        "logic_framework":      "إطار العمل",
        "active_persona":       "الشخصية النشطة",
        "aesthetic_preset":     "الجمالية",
        "hikmah_style":         "نمط الحكمة",

        # Workspace HUD
        "execute_btn":          "⚡  تنفيذ التحسين",
        "precision":            "الدقة",
        "alignment":            "التوافق",
        "efficiency":           "الكفاءة",
    },

    # ── FRENCH ────────────────────────────────────────────────────────────────
    "fr": {
        "app_name":             "InkOS",
        "app_subtitle":         "Moteur de Cartographie Cognitive Arabe",
        "app_tagline":          "حبر وفكرة. Encre & Idées.",

        # Sidebar HUD & Tabs
        "session_runs":         "Exécutions",
        "session_remaining":    "Restantes",
        "last_saved":           "Dernière Sauvegarde",
        "reset_session":        "Réinitialiser la Session",
        "tab_workspace":        "ESPACE DE TRAVAIL",
        "tab_vault":            "🔒 COFFRE",
        "tab_forge":            "🎭 FORGE",
        "tab_archive":          "ARCHIVE",
        "tab_security":         "LOG DE SÉCURITÉ",
        "tab_cognitive_map":    "CARTE COGNITIVE",
        "tab_guide":            "GUIDE",

        # Logic Configuration
        "logic_config":         "⚙️ Configuration Logique",
        "logic_framework":      "Cadre de travail",
        "active_persona":       "Persona Actif",
        "aesthetic_preset":     "Esthétique",
        "hikmah_style":         "Style Hikmah",

        # Workspace HUD
        "execute_btn":          "⚡  Exécuter le Refinement",
        "precision":            "Précision",
        "alignment":            "Alignement",
        "efficiency":           "Efficacité",
    },
}

# ── HELPER LOGIC ──────────────────────────────────────────────────────────────

def get_lang() -> str:
    # Ensure UI_LANG is in K constants
    return st.session_state.get(K.UI_LANG if hasattr(K, 'UI_LANG') else 'ui_lang', DEFAULT_LANG)

def set_lang(code: str) -> None:
    if code in {lg["code"] for lg in LANGUAGES}:
        st.session_state[K.UI_LANG if hasattr(K, 'UI_LANG') else 'ui_lang'] = code

def t(key: str, fallback: Optional[str] = None, **kwargs) -> str:
    """
    🟢 ARMORED: UI Translation with explicit fallback support.
    Priority: Current Lang -> English -> Fallback Arg -> Key Name
    """
    if not key: return fallback or ""
    
    lang = get_lang()
    lang_dict = TRANSLATIONS.get(lang, {})
    en_dict = TRANSLATIONS.get("en", {})
    
    raw = lang_dict.get(key) or en_dict.get(key) or fallback or key
    
    if kwargs and isinstance(raw, str):
        try:
            return raw.format(**kwargs)
        except (KeyError, ValueError):
            return raw
    return str(raw)

def is_rtl() -> bool:
    lang = get_lang()
    for lg in LANGUAGES:
        if lg["code"] == lang:
            return lg["dir"] == "rtl"
    return False
