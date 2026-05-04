
"""
i18n/translations.py — UI Translation System
==============================================
Three-language support: English, Arabic, French.

Usage:
    from i18n.translations import t
    st.button(t("execute_btn"))

Arabic layout:
    When lang == "ar", inject CSS class "rtl-mode" on stApp
    via st.markdown — this flips text direction and font.

Adding a new language:
    1. Add a new dict to TRANSLATIONS with your lang code
    2. Add the language to LANGUAGES list
    3. All existing t() calls work automatically

Adding a new string:
    Add the key to all three dicts.
    If a key is missing from a non-English dict,
    t() falls back to English silently.
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
        # App
        "app_name":             "InkOS",
        "app_subtitle":         "Arabic Cognitive Prompt Engine",
        "app_tagline":          "حبر وفكرة. Ink & Ideas.",

        # Sidebar sections
        "logic_config":         "⚙️ Logic Configuration",
        "target_dialect":       "Target Dialect",
        "target_help":          "Which AI you are prompting. InkOS adapts its output syntax for each one.",
        "logic_framework":      "Logic Framework",
        "framework_help":       "RACE is best for professional tasks. Debugger works for code and technical prompts.",
        "linguistic_source":    "Linguistic Source",
        "lang_help":            "Arabic triggers the cognitive mapping engine — your phrasing is mapped to AI paradigms, not translated.",
        "active_persona":       "🎭 Active Persona",
        "persona_help":         "Persona is injected into every refinement. Build your own in the FORGE tab.",
        "aesthetic_dir":        "🎨 Aesthetic Direction",
        "aesthetic_preset":     "Aesthetic Preset",
        "aesthetic_help":       "Select 'Raw' for literal interpretation or a preset for branded styling.",
        "islamic_mode":         "☪️ Islamic Professional Mode",
        "islamic_active":       "ACTIVE",
        "islamic_sharia":       "Sharia-aware framing enabled",
        "islamic_citation":     "Arabic scholarly citation style",
        "session_runs":         "Runs",
        "session_remaining":    "Remaining",
        "reset_session":        "Reset Session",
        "export_archive":       "Export Archive",
        "persona_active_badge": "PERSONA ACTIVE",

        # Tabs
        "tab_workspace":        "WORKSPACE",
        "tab_archive":          "ARCHIVE",
        "tab_security":         "SECURITY",
        "tab_cognitive_map":    "COGNITIVE MAP",
        "tab_vault":            "🔒 VAULT",
        "tab_forge":            "🎭 FORGE",
        "tab_guide":            "📖 GUIDE",

        # Workspace
        "workspace_header":     "System Input",
        "workspace_hint":       "Write your raw intent in plain English or Arabic. InkOS restructures it into a precision prompt for your selected AI. No format required — just say what you want.",
        "workspace_placeholder":"English: Act as a senior analyst. Review this pitch deck and flag every assumption that lacks supporting evidence.\n\nعربي: اشرح لي هذا المفهوم تدريجياً بأسلوب تقني للمحترفين",
        "execute_btn":          "⚡  Execute Refinement",
        "execute_help":         "Refine your intent into a precision prompt. Takes 5–15 seconds.",
        "status_processing":    "Refining prompt — takes 5–15 seconds...",
        "status_mapping":       "🗺️ Mapping cognitive pattern and building prompt...",
        "status_compiling":     "✅ Refinement complete. Compiling audit scores...",
        "status_done":          "📊 Done.",
        "status_complete":      "Complete",
        "status_error":         "Error",
        "empty_input":          "Intent stream is empty.",
        "injection_blocked":    "BLOCKED — Injection pattern detected. Request logged.",
        "rate_limit":           "Rate limit reached — 10 calls per 60 seconds.",
        "pattern_identified":   "Pattern Identified",
        "engine_applied":       "Engine Applied",
        "refinement_quality":   "Refinement Quality",
        "precision":            "Precision",
        "alignment":            "Alignment",
        "efficiency":           "Efficiency",
        "original_intent":      "Original Intent",
        "refined_asset":        "Refined Asset",
        "refined_help":         "Select all and copy. Drag the bottom-right corner to resize.",
        "download_prompt":      "Download Prompt",
        "save_to_vault":        "Save to Vault",
        "vault_title_ph":       "Give this prompt a name...",
        "vault_tags_ph":        "tags, comma, separated",
        "save_vault_btn":       "🔒 Save to Vault",
        "save_vault_warning":   "⚠ Give this prompt a title before saving.",
        "saving_vault":         "Saving to Vault...",
        "save_vault_success":   "✓ Saved '{title}' to Vault. Find it in the 🔒 VAULT tab.",
        "save_vault_error":     "✗ Save failed: {error}",

        # Archive
        "archive_header":       "Neural Archive",
        "archive_empty":        "Archive is empty. Execute a refinement to populate.",
        "filter_target":        "Filter Target",
        "filter_pattern":       "Filter Pattern",
        "entries_found":        "{count} ENTRIES",
        "original_input":       "Original Input",
        "download":             "Download",
        "export_full":          "Export Full Archive (JSON)",

        # Security
        "security_header":      "Security Ledger",
        "no_threats":           "NO THREATS DETECTED THIS SESSION",
        "threats_blocked":      "{count} ATTEMPT{plural} BLOCKED",

        # Vault
        "vault_header":         "Prompt Memory Vault",
        "vault_offline":        "⚠ VAULT OFFLINE",
        "vault_offline_msg":    "Supabase credentials not found. Add SUPABASE_URL and SUPABASE_KEY to your environment.",
        "vault_empty":          "No prompts found. Execute a refinement and save it to populate your vault.",
        "vault_saved":          "{count} PROMPT{plural} FOUND",
        "search_ph":            "Search title, tags, or content...",
        "all_tags":             "All Tags",
        "all_targets":          "All",
        "min_score":            "Min%",
        "deploy_workspace":     "⚡ Deploy to Workspace",
        "deployed_success":     "Deployed '{title}' to workspace. Switch to WORKSPACE tab.",
        "vault_stats_saved":    "Saved Prompts",
        "vault_stats_avg":      "Avg Score",
        "vault_stats_target":   "Top Target",
        "vault_stats_tag":      "Top Tag",
        "confirm_delete":       "✓ Confirm",
        "delete_btn":           "🗑 Delete",

        # Forge
        "forge_header":         "Persona Forge",
        "forge_subtitle":       "Build reusable AI personas. Activate one from the sidebar and it injects into every refinement automatically.",
        "forge_active":         "Active: {name} — injecting into all refinements",
        "browse_personas":      "Browse Personas",
        "create_new":           "Create New",
        "builtin_starters":     "Built-in Starters",
        "your_personas":        "Your Personas",
        "no_personas":          "No saved personas yet. Create one below.",
        "activate_btn":         "⚡ Activate",
        "active_btn":           "✓ Active",
        "preview_injection":    "👁 Preview Injection",
        "preview_for":          "Injection preview for {target}",
        "persona_name_ph":      "e.g. Islamic Finance Consultant",
        "optimised_for":        "Optimised For",
        "role_definition":      "Role Definition",
        "role_ph":              "Describe who this persona is and their expertise...",
        "constraints_label":    "Constraints",
        "constraints_ph":       "What must this persona never do? What must it always consider?",
        "style_label":          "Communication Style",
        "style_ph":             "How should this persona write and speak?",
        "tags_label":           "Tags",
        "tags_ph":              "finance, arabic, technical...",
        "save_activate":        "⚡ Save & Activate Persona",
        "persona_name_warn":    "Give this persona a name.",
        "persona_role_warn":    "Role definition cannot be empty.",
        "persona_session_ok":   "Persona '{name}' activated for this session. Connect Supabase to persist it.",
        "persona_saved_ok":     "Persona '{name}' saved and activated.",
        "persona_save_err":     "Save failed: {error}",
        "supabase_hint":        "Connect Supabase to save custom personas across sessions.",

        # Guide
        "guide_quick_start":    "⚡ Quick Start",
        "guide_feature":        "📖 Feature Guide",
        "guide_arabic":         "🗺️ Arabic Engine",
        "guide_running":        "Get Running in 2 Minutes",
        "guide_good_input":     "What Makes a Good Input",
        "guide_features":       "Every Feature Explained",
        "guide_detection":      "How Detection Works",
        "guide_patterns":       "Eight Rhetorical Devices → Eight Prompting Paradigms",
        "guide_engine_title":   "The Arabic Cognitive Engine",
                "auto_analysing":       "🎯 CIPHER analysing best target...",
        "auto_selected":        "CIPHER selected: {target} — {reason}",
        "auto_hint":            "CIPHER will analyse your input and select the best AI automatically.",
        "sidebar_controls":     "Sidebar Controls",
    },

    # ── ARABIC ────────────────────────────────────────────────────────────────
    "ar": {
        # App
        "app_name":             "إنك أو إس",
        "app_subtitle":         "محرك الخرائط المعرفية العربية",
        "app_tagline":          "حبر وفكرة.",

        # Sidebar
        "logic_config":         "⚙️ إعدادات المنطق",
        "target_dialect":       "اللهجة المستهدفة",
        "target_help":          "أي ذكاء اصطناعي تستهدف؟ يكيّف InkOS مخرجاته لكل واحد.",
        "logic_framework":      "إطار المنطق",
        "framework_help":       "RACE الأفضل للمهام المهنية. Debugger للمهام التقنية.",
        "linguistic_source":    "المصدر اللغوي",
        "lang_help":            "المدخل العربي يُفعّل محرك الخرائط المعرفية — لا ترجمة، بل تحويل مفاهيمي.",
        "active_persona":       "🎭 الشخصية النشطة",
        "persona_help":         "تُحقن الشخصية في كل عملية تحسين. أنشئ شخصيتك في تبويب FORGE.",
        "aesthetic_dir":        "🎨 التوجه الجمالي",
        "aesthetic_preset":     "الإعداد المسبق الجمالي",
        "aesthetic_help":       "اختر 'خام' للتفسير الحرفي أو إعداداً مسبقاً لأسلوب مميز.",
        "islamic_mode":         "☪️ وضع الاحتراف الإسلامي",
        "islamic_active":       "مُفعَّل",
        "islamic_sharia":       "الإطار الشرعي مُفعَّل",
        "islamic_citation":     "أسلوب الاستشهاد الأكاديمي العربي",
        "session_runs":         "التشغيلات",
        "session_remaining":    "المتبقي",
        "reset_session":        "إعادة تعيين الجلسة",
        "export_archive":       "تصدير الأرشيف",
        "persona_active_badge": "الشخصية نشطة",

        # Tabs
        "tab_workspace":        "مساحة العمل",
        "tab_archive":          "الأرشيف",
        "tab_security":         "الأمان",
        "tab_cognitive_map":    "الخريطة المعرفية",
        "tab_vault":            "🔒 الخزينة",
        "tab_forge":            "🎭 المصنع",
        "tab_guide":            "📖 الدليل",

        # Workspace
        "workspace_header":     "مدخل النظام",
        "workspace_hint":       "اكتب ما تريده بالعربية أو الإنجليزية. سيعيد InkOS هيكلته إلى أمر دقيق لذكائك الاصطناعي المختار.",
        "workspace_placeholder":"مثال: اشرح لي هذا المفهوم تدريجياً بأسلوب تقني للمحترفين\n\nEnglish: Act as a senior analyst and review this pitch deck.",
        "execute_btn":          "⚡  تنفيذ التحسين",
        "execute_help":         "تحسين نيتك إلى أمر دقيق. يستغرق من 5 إلى 15 ثانية.",
        "status_processing":    "جارٍ تحسين الأمر — من 5 إلى 15 ثانية...",
        "status_mapping":       "🗺️ تحديد النمط المعرفي وبناء الأمر...",
        "status_compiling":     "✅ اكتمل التحسين. جارٍ تجميع نتائج التدقيق...",
        "status_done":          "📊 تم.",
        "status_complete":      "مكتمل",
        "status_error":         "خطأ",
        "empty_input":          "مدخل النظام فارغ.",
        "injection_blocked":    "محظور — تم اكتشاف نمط حقن. تم تسجيل الطلب.",
        "rate_limit":           "تم الوصول إلى حد المعدل — 10 مكالمات كل 60 ثانية.",
        "pattern_identified":   "النمط المُكتشف",
        "engine_applied":       "المحرك المُطبَّق",
        "refinement_quality":   "جودة التحسين",
        "precision":            "الدقة",
        "alignment":            "التوافق",
        "efficiency":           "الكفاءة",
        "original_intent":      "النية الأصلية",
        "refined_asset":        "الأصل المحسَّن",
        "refined_help":         "حدد الكل وانسخ. اسحب الزاوية اليمنى السفلية لتغيير الحجم.",
        "download_prompt":      "تحميل الأمر",
        "save_to_vault":        "حفظ في الخزينة",
        "vault_title_ph":       "أعطِ هذا الأمر اسماً...",
        "vault_tags_ph":        "وسوم، مفصولة بفواصل",
        "save_vault_btn":       "🔒 حفظ في الخزينة",
        "save_vault_warning":   "⚠ أعطِ هذا الأمر عنواناً قبل الحفظ.",
        "saving_vault":         "جارٍ الحفظ في الخزينة...",
        "save_vault_success":   "✓ تم حفظ '{title}' في الخزينة.",
        "save_vault_error":     "✗ فشل الحفظ: {error}",

        # Archive
        "archive_header":       "الأرشيف العصبي",
        "archive_empty":        "الأرشيف فارغ. نفّذ تحسيناً لتعبئته.",
        "filter_target":        "تصفية حسب الهدف",
        "filter_pattern":       "تصفية حسب النمط",
        "entries_found":        "{count} إدخال",
        "original_input":       "المدخل الأصلي",
        "download":             "تحميل",
        "export_full":          "تصدير الأرشيف كاملاً (JSON)",

        # Security
        "security_header":      "سجل الأمان",
        "no_threats":           "لا تهديدات مكتشفة في هذه الجلسة",
        "threats_blocked":      "تم حظر {count} محاولة",

        # Vault
        "vault_header":         "خزينة الذاكرة",
        "vault_offline":        "⚠ الخزينة غير متصلة",
        "vault_offline_msg":    "بيانات Supabase غير موجودة. أضف SUPABASE_URL و SUPABASE_KEY.",
        "vault_empty":          "لا أوامر محفوظة. نفّذ تحسيناً واحفظه.",
        "vault_saved":          "{count} أمر موجود",
        "search_ph":            "ابحث في العناوين والوسوم أو المحتوى...",
        "all_tags":             "كل الوسوم",
        "all_targets":          "الكل",
        "min_score":            "أدنى نسبة",
        "deploy_workspace":     "⚡ نشر في مساحة العمل",
        "deployed_success":     "تم نشر '{title}' في مساحة العمل.",
        "vault_stats_saved":    "الأوامر المحفوظة",
        "vault_stats_avg":      "متوسط الدرجة",
        "vault_stats_target":   "الهدف الأكثر استخداماً",
        "vault_stats_tag":      "الوسم الأكثر استخداماً",
        "confirm_delete":       "✓ تأكيد",
        "delete_btn":           "🗑 حذف",

        # Forge
        "forge_header":         "مصنع الشخصيات",
        "forge_subtitle":       "أنشئ شخصيات ذكاء اصطناعي قابلة لإعادة الاستخدام. فعّل واحدة من الشريط الجانبي وستُحقن في كل تحسين تلقائياً.",
        "forge_active":         "نشطة: {name} — تُحقن في جميع التحسينات",
        "browse_personas":      "تصفح الشخصيات",
        "create_new":           "إنشاء جديد",
        "builtin_starters":     "الشخصيات المدمجة",
        "your_personas":        "شخصياتك",
        "no_personas":          "لا شخصيات محفوظة بعد. أنشئ واحدة أدناه.",
        "activate_btn":         "⚡ تفعيل",
        "active_btn":           "✓ نشطة",
        "preview_injection":    "👁 معاينة الحقن",
        "preview_for":          "معاينة الحقن لـ {target}",
        "persona_name_ph":      "مثال: محلل التمويل الإسلامي",
        "optimised_for":        "محسَّنة لـ",
        "role_definition":      "تعريف الدور",
        "role_ph":              "صف هذه الشخصية وخبرتها...",
        "constraints_label":    "القيود",
        "constraints_ph":       "ما الذي يجب ألا تفعله هذه الشخصية أبداً؟",
        "style_label":          "أسلوب التواصل",
        "style_ph":             "كيف يجب أن تكتب هذه الشخصية وتتحدث؟",
        "tags_label":           "الوسوم",
        "tags_ph":              "مالية، عربية، تقنية...",
        "save_activate":        "⚡ حفظ وتفعيل الشخصية",
        "persona_name_warn":    "أعطِ هذه الشخصية اسماً.",
        "persona_role_warn":    "لا يمكن أن يكون تعريف الدور فارغاً.",
        "persona_session_ok":   "تم تفعيل الشخصية '{name}' لهذه الجلسة.",
        "persona_saved_ok":     "تم حفظ الشخصية '{name}' وتفعيلها.",
        "persona_save_err":     "فشل الحفظ: {error}",
        "supabase_hint":        "اربط Supabase لحفظ الشخصيات عبر الجلسات.",

        # Guide
        "guide_quick_start":    "⚡ البداية السريعة",
        "guide_feature":        "📖 دليل الميزات",
        "guide_arabic":         "🗺️ المحرك العربي",
        "guide_running":        "ابدأ في دقيقتين",
        "guide_good_input":     "ما الذي يجعل المدخل جيداً؟",
        "guide_features":       "شرح كل ميزة",
        "guide_detection":      "كيف يعمل الاكتشاف؟",
        "guide_patterns":       "ثمانية أساليب بلاغية → ثمانية نماذج إرشادية",
        "guide_engine_title":   "المحرك المعرفي العربي",
        "sidebar_controls":     "أدوات التحكم في الشريط الجانبي",
    },

    # ── FRENCH ────────────────────────────────────────────────────────────────
    "fr": {
        # App
        "app_name":             "InkOS",
        "app_subtitle":         "Moteur de Cartographie Cognitive Arabe",
        "app_tagline":          "حبر وفكرة. Encre & Idées.",

        # Sidebar
        "logic_config":         "⚙️ Configuration Logique",
        "target_dialect":       "Dialecte Cible",
        "target_help":          "Quel IA visez-vous? InkOS adapte sa syntaxe de sortie pour chacun.",
        "logic_framework":      "Cadre Logique",
        "framework_help":       "RACE convient aux tâches professionnelles. Debugger pour les tâches techniques.",
        "linguistic_source":    "Source Linguistique",
        "lang_help":            "L'arabe active le moteur de cartographie cognitive — vos formulations sont mappées à des paradigmes IA, non traduites.",
        "active_persona":       "🎭 Persona Active",
        "persona_help":         "La persona est injectée dans chaque refinement. Créez la vôtre dans l'onglet FORGE.",
        "aesthetic_dir":        "🎨 Direction Esthétique",
        "aesthetic_preset":     "Préréglage Esthétique",
        "aesthetic_help":       "Sélectionnez 'Brut' pour une interprétation littérale ou un préréglage pour un style de marque.",
        "islamic_mode":         "☪️ Mode Professionnel Islamique",
        "islamic_active":       "ACTIF",
        "islamic_sharia":       "Cadrage conforme à la charia activé",
        "islamic_citation":     "Style de citation académique arabe",
        "session_runs":         "Exécutions",
        "session_remaining":    "Restantes",
        "reset_session":        "Réinitialiser la Session",
        "export_archive":       "Exporter l'Archive",
        "persona_active_badge": "PERSONA ACTIVE",

        # Tabs
        "tab_workspace":        "ESPACE DE TRAVAIL",
        "tab_archive":          "ARCHIVE",
        "tab_security":         "SÉCURITÉ",
        "tab_cognitive_map":    "CARTE COGNITIVE",
        "tab_vault":            "🔒 COFFRE",
        "tab_forge":            "🎭 FORGE",
        "tab_guide":            "📖 GUIDE",

        # Workspace
        "workspace_header":     "Entrée Système",
        "workspace_hint":       "Écrivez votre intention brute en anglais, arabe ou français. InkOS la restructure en prompt de précision pour votre IA cible.",
        "workspace_placeholder":"Exemple: Agissez en tant qu'analyste senior. Examinez ce pitch deck et signalez chaque hypothèse sans preuve.\n\nعربي: اشرح لي هذا المفهوم تدريجياً",
        "execute_btn":          "⚡  Exécuter le Refinement",
        "execute_help":         "Affinez votre intention en prompt de précision. Prend 5 à 15 secondes.",
        "status_processing":    "Refinement en cours — 5 à 15 secondes...",
        "status_mapping":       "🗺️ Cartographie du pattern cognitif...",
        "status_compiling":     "✅ Refinement terminé. Compilation des scores d'audit...",
        "status_done":          "📊 Terminé.",
        "status_complete":      "Terminé",
        "status_error":         "Erreur",
        "empty_input":          "Le flux d'intention est vide.",
        "injection_blocked":    "BLOQUÉ — Pattern d'injection détecté. Requête enregistrée.",
        "rate_limit":           "Limite de taux atteinte — 10 appels par 60 secondes.",
        "pattern_identified":   "Pattern Identifié",
        "engine_applied":       "Moteur Appliqué",
        "refinement_quality":   "Qualité du Refinement",
        "precision":            "Précision",
        "alignment":            "Alignement",
        "efficiency":           "Efficacité",
        "original_intent":      "Intention Originale",
        "refined_asset":        "Prompt Affiné",
        "refined_help":         "Sélectionnez tout et copiez. Faites glisser le coin inférieur droit pour redimensionner.",
        "download_prompt":      "Télécharger le Prompt",
        "save_to_vault":        "Sauvegarder dans le Coffre",
        "vault_title_ph":       "Donnez un nom à ce prompt...",
        "vault_tags_ph":        "tags, séparés, par virgule",
        "save_vault_btn":       "🔒 Sauvegarder dans le Coffre",
        "save_vault_warning":   "⚠ Donnez un titre à ce prompt avant de sauvegarder.",
        "saving_vault":         "Sauvegarde dans le Coffre...",
        "save_vault_success":   "✓ '{title}' sauvegardé dans le Coffre.",
        "save_vault_error":     "✗ Échec de la sauvegarde: {error}",

        # Archive
        "archive_header":       "Archive Neurale",
        "archive_empty":        "Archive vide. Exécutez un refinement pour la remplir.",
        "filter_target":        "Filtrer par Cible",
        "filter_pattern":       "Filtrer par Pattern",
        "entries_found":        "{count} ENTRÉES",
        "original_input":       "Entrée Originale",
        "download":             "Télécharger",
        "export_full":          "Exporter l'Archive Complète (JSON)",

        # Security
        "security_header":      "Registre de Sécurité",
        "no_threats":           "AUCUNE MENACE DÉTECTÉE CETTE SESSION",
        "threats_blocked":      "{count} TENTATIVE{plural} BLOQUÉE{plural}",

        # Vault
        "vault_header":         "Coffre Mémoire",
        "vault_offline":        "⚠ COFFRE HORS LIGNE",
        "vault_offline_msg":    "Identifiants Supabase introuvables. Ajoutez SUPABASE_URL et SUPABASE_KEY.",
        "vault_empty":          "Aucun prompt trouvé. Exécutez un refinement et sauvegardez-le.",
        "vault_saved":          "{count} PROMPT{plural} TROUVÉ{plural}",
        "search_ph":            "Rechercher dans les titres, tags ou contenu...",
        "all_tags":             "Tous les Tags",
        "all_targets":          "Tous",
        "min_score":            "Min%",
        "deploy_workspace":     "⚡ Déployer dans l'Espace de Travail",
        "deployed_success":     "'{title}' déployé dans l'espace de travail.",
        "vault_stats_saved":    "Prompts Sauvegardés",
        "vault_stats_avg":      "Score Moyen",
        "vault_stats_target":   "Cible Principale",
        "vault_stats_tag":      "Tag Principal",
        "confirm_delete":       "✓ Confirmer",
        "delete_btn":           "🗑 Supprimer",

        # Forge
        "forge_header":         "Forge de Personas",
        "forge_subtitle":       "Créez des personas IA réutilisables. Activez-en une dans la barre latérale et elle s'injecte automatiquement dans chaque refinement.",
        "forge_active":         "Active: {name} — injection dans tous les refinements",
        "browse_personas":      "Parcourir les Personas",
        "create_new":           "Créer Nouvelle",
        "builtin_starters":     "Personas Intégrées",
        "your_personas":        "Vos Personas",
        "no_personas":          "Aucune persona sauvegardée. Créez-en une ci-dessous.",
        "activate_btn":         "⚡ Activer",
        "active_btn":           "✓ Active",
        "preview_injection":    "👁 Aperçu de l'Injection",
        "preview_for":          "Aperçu pour {target}",
        "persona_name_ph":      "ex. Analyste Finance Islamique",
        "optimised_for":        "Optimisée Pour",
        "role_definition":      "Définition du Rôle",
        "role_ph":              "Décrivez qui est cette persona et son expertise...",
        "constraints_label":    "Contraintes",
        "constraints_ph":       "Que ne doit jamais faire cette persona?",
        "style_label":          "Style de Communication",
        "style_ph":             "Comment cette persona doit-elle écrire et parler?",
        "tags_label":           "Tags",
        "tags_ph":              "finance, arabe, technique...",
        "save_activate":        "⚡ Sauvegarder et Activer",
        "persona_name_warn":    "Donnez un nom à cette persona.",
        "persona_role_warn":    "La définition du rôle ne peut pas être vide.",
        "persona_session_ok":   "Persona '{name}' activée pour cette session.",
        "persona_saved_ok":     "Persona '{name}' sauvegardée et activée.",
        "persona_save_err":     "Échec de la sauvegarde: {error}",
        "supabase_hint":        "Connectez Supabase pour sauvegarder les personas entre sessions.",

        # Guide
        "guide_quick_start":    "⚡ Démarrage Rapide",
        "guide_feature":        "📖 Guide des Fonctionnalités",
        "guide_arabic":         "🗺️ Moteur Arabe",
        "guide_running":        "Démarrez en 2 Minutes",
        "guide_good_input":     "Ce qui fait une bonne entrée",
        "guide_features":       "Chaque Fonctionnalité Expliquée",
        "guide_detection":      "Comment Fonctionne la Détection",
        "guide_patterns":       "Huit Dispositifs Rhétoriques → Huit Paradigmes",
        "guide_engine_title":   "Le Moteur Cognitif Arabe",
        "sidebar_controls":     "Contrôles de la Barre Latérale",
    },
}


def get_lang() -> str:
    """Returns current UI language code. Defaults to 'en' if not set."""
    return st.session_state.get(K.UI_LANG, DEFAULT_LANG)


def set_lang(code: str) -> None:
    """Sets the UI language. Triggers rerun to apply across all components."""
    if code in {lg["code"] for lg in LANGUAGES}:
        st.session_state[K.UI_LANG] = code


def t(key: str, **kwargs) -> str:
    """
    Translate a key to the current UI language.
    Falls back to English if key missing in target language.
    Falls back to key string if missing in English too.

    Supports string formatting:
        t("save_vault_success", title="My Prompt")
        → "✓ Saved 'My Prompt' to Vault."
    """
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
    """Returns True when current language is RTL (Arabic)."""
    lang = get_lang()
    for lg in LANGUAGES:
        if lg["code"] == lang:
            return lg["dir"] == "rtl"
    return False
