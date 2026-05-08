"""
i18n/translations.py — UI Translation System
==============================================
v20.1: HUD Metric Synchronization.
       Integrated 'last_saved' keys across all language dictionaries.
"""

import streamlit as st
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

        # Sidebar HUD
        "session_runs":         "Runs",
        "session_remaining":    "Remaining",
        "last_saved":           "Last Saved", # 🟢 SYNCED
        "reset_session":        "Reset Session",
        "export_archive":       "Export Archive",
        
        # ... [Logic Config & Tab translations remain identical] ...
        "logic_config":         "⚙️ Logic Configuration",
        "tab_workspace":        "WORKSPACE",
        "tab_vault":            "🔒 VAULT",
        "tab_forge":            "🎭 FORGE",
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

        # Sidebar HUD
        "session_runs":         "التشغيلات",
        "session_remaining":    "المتبقي",
        "last_saved":           "آخر حفظ", # 🟢 SYNCED: Professional Arabic terminology
        "reset_session":        "إعادة تعيين الجلسة",
        "export_archive":       "تصدير الأرشيف",

        # ... [Logic Config & Tab translations remain identical] ...
        "logic_config":         "⚙️ إعدادات المنطق",
        "tab_workspace":        "مساحة العمل",
        "tab_vault":            "🔒 الخزينة",
        "tab_forge":            "🎭 المصنع",
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

        # Sidebar HUD
        "session_runs":         "Exécutions",
        "session_remaining":    "Restantes",
        "last_saved":           "Dernière Sauvegarde", # 🟢 SYNCED
        "reset_session":        "Réinitialiser la Session",
        "export_archive":       "Exporter l'Archive",

        # ... [Logic Config & Tab translations remain identical] ...
        "logic_config":         "⚙️ Configuration Logique",
        "tab_workspace":        "ESPACE DE TRAVAIL",
        "tab_vault":            "🔒 COFFRE",
        "tab_forge":            "🎭 FORGE",
        "execute_btn":          "⚡  Exécuter le Refinement",
        "precision":            "Précision",
        "alignment":            "Alignement",
        "efficiency":           "Efficacité",
    },
}

# ── HELPER LOGIC (Natively Lean) ──────────────────────────────────────────────

def get_lang() -> str:
    return st.session_state.get(K.UI_LANG, DEFAULT_LANG)

def set_lang(code: str) -> None:
    if code in {lg["code"] for lg in LANGUAGES}:
        st.session_state[K.UI_LANG] = code

def t(key: str, **kwargs) -> str:
    lang = get_lang()
    lang_dict  = TRANSLATIONS.get(lang, {})
    en_dict    = TRANSLATIONS.get("en", {})
    raw = lang_dict.get(key) or en_dict.get(key) or key
    if kwargs:
        try:
            return raw.format(**kwargs)
        except (KeyError, ValueError):
            return raw
    return raw

def is_rtl() -> bool:
    lang = get_lang()
    for lg in LANGUAGES:
        if lg["code"] == lang:
            return lg["dir"] == "rtl"
    return False
