from types import MappingProxyType

AUTO_SELECT_LABEL = "✦ AUTO_SELECT"

TARGET_SELECTION_GUIDE = "Auto-routes based on detected intent. Select manually to override."

TARGET_GUIDES = MappingProxyType({
    'ChatGPT': (
        'Direct, conversational, and highly creative. '
        'Best for brainstorming, storytelling, and rapid copy drafting.'
    ),
    'Claude': (
        'Structure output using XML tags: <role>, <task>, <constraints>, <output_format>. '
        'Analytical, precise tone. State the evaluation criterion before the task.'
    ),
    'Midjourney/Flux': (
        'Visual production prompts. Use comma-separated descriptors. '
        'Include lighting, lens, and style slots. No conversational filler.'
    ),
    'Gemini (Imagen 3)': (
        'Best for text-integrated visuals and signage. '
        'Describe the exact text to be rendered within the image.'
    ),
    'Manus AI': (
        'Multi-step agentic workflows. Routing to Claude fallback for local processing.'
    )
})

TARGET_ROUTING_TABLE: list = [
  # ── CODE & TECHNICAL ──────────────────────────────────────────────
  { 'category': 'code', 'target': 'Claude', 'score': 10,
    'rationale': 'Technical implementation — Anthropic Core',
    'en_patterns': [r'\bpython\b', r'\bjavascript\b', r'\bsql\b', r'\bcode\b',
                    r'\bscript\b', r'\bdebug\b', r'\brefactor\b', r'\bapi\b',
                    r'\bhtml\b', r'\bcss\b', r'\breact\b', r'\bnode\b',
                    r'\bfunction\b', r'\bclass\b', r'\balgorithm\b',
                    r'\barchitecture\b', r'\boptimize\b', r'\bbig-?o\b'],
    'ar_substrings': ['برمجة','كود','سكربت','خوارزمية','مطور','برنامج','بايثون'] },

  # ── RESEARCH & ANALYSIS ───────────────────────────────────────────
  { 'category': 'research', 'target': 'Claude', 'score': 8,
    'rationale': 'Deep analysis, long-form — Anthropic Core',
    'en_patterns': [r'\bessay\b', r'\breport\b', r'\banalysis\b', r'\bresearch\b',
                    r'\bacademic\b', r'\bthesis\b', r'\bcritique\b',
                    r'\bexplain\b', r'\bcompare\b', r'\bevaluate\b'],
    'ar_substrings': ['بحث','تحليل','دراسة','مقارنة','أكاديمي'] },

  # ── ARABIC / ISLAMIC ──────────────────────────────────────────────
  { 'category': 'arabic_islamic', 'target': 'Claude', 'score': 9,
    'rationale': 'Arabic scholarly depth — Anthropic Core',
    'en_patterns': [r'\bisla[mn]ic?\b', r'\bsharia\b', r'\bquran\b',
                    r'\bhadith\b', r'\barabic\b'],
    'ar_substrings': ['إسلام','شريعة','قرآن','حديث','فقه','عربي','عربية'] },

  # ── MARKETING & SOCIAL ───────────────────────────────────────────
  { 'category': 'marketing', 'target': 'ChatGPT', 'score': 8,
    'rationale': 'Copywriting, hooks, social — GPT-4o',
    'en_patterns': [r'\btweet\b', r'\bcaption\b', r'\bad\b', r'\bslogan\b',
                    r'\bhook\b', r'\bheadline\b', r'\bemail\b',
                    r'\bmarketing\b', r'\bcampaign\b', r'\bseo\b', r'\bviral\b'],
    'ar_substrings': ['إعلان','تسويق','محتوى','كابشن','تغريدة'] },

  # ── CREATIVE WRITING ──────────────────────────────────────────────
  { 'category': 'creative', 'target': 'ChatGPT', 'score': 7,
    'rationale': 'Storytelling, scripts, brainstorming — GPT-4o',
    'en_patterns': [r'\bstory\b', r'\bscript\b', r'\bnarrative\b', r'\bfiction\b',
                    r'\bbrainstorm\b', r'\bcreative\b', r'\bpoem\b', r'\bdialogue\b'],
    'ar_substrings': ['قصة','سكريبت','إبداع','خيال','أفكار','حوار'] },

  # ── AUTOMATION & AGENTS ───────────────────────────────────────────
  { 'category': 'agentic', 'target': 'Manus AI', 'score': 10,
    'rationale': 'Multi-step agentic workflow — Manus AI',
    'en_patterns': [r'\bautomation?\b', r'\bagent\b', r'\bworkflow\b',
                    r'\bpipeline\b', r'\bscrape\b', r'\bcrawl\b',
                    r'\bscheduled?\b', r'\bbatch\b', r'\bbrowser\b'],
    'ar_substrings': ['أتمتة','وكيل','سير عمل','مهمة متعددة'] },

  # ── IMAGE: STYLIZED ───────────────────────────────────────────────
  { 'category': 'image_stylized', 'target': 'Midjourney/Flux', 'score': 9,
    'rationale': 'Artistic, illustrated, anime — Diffusion Matrix',
    'en_patterns': [r'\banime\b', r'\billustrat\b', r'\bconcept\s+art\b',
                    r'\bcinematic\b', r'\bwallpaper\b', r'\bcharacter\s+design\b',
                    r'\bfantasy\b', r'\btech.?noir\b', r'\bsci.?fi\b',
                    r'\bartistic\b', r'\bstylized\b'],
    'ar_substrings': ['أنمي','رسوم','تصوير فني','خيال علمي','شخصية'] },

  # ── IMAGE: PHOTOREALISTIC ─────────────────────────────────────────
  { 'category': 'image_photo', 'target': 'DALL-E 3', 'score': 9,
    'rationale': 'Photorealistic, portrait, product — DALL-E 3',
    'en_patterns': [r'\bphoto\b', r'\bphotograph\b', r'\bphoto.?realistic\b',
                    r'\bportrait\b', r'\bproduct\s+shot\b', r'\bhyperrealistic\b'],
    'ar_substrings': ['صورة واقعية','تصوير','بورتريه'] },

  # ── IMAGE: TEXT IN IMAGE ──────────────────────────────────────────
  { 'category': 'image_text', 'target': 'Gemini (Imagen 3)', 'score': 10,
    'rationale': 'Text-in-image, logo, signage — Gemini Imagen 3',
    'en_patterns': [r'\blogo\b', r'\bbanner\b', r'\bsignage\b',
                    r'\btypography\b', r'\btext\s+in\b', r'\bwith\s+text\b',
                    r'\bwith\s+the\s+word\b', r'\blabel\b', r'\bui\s+mock\b'],
    'ar_substrings': ['شعار','بنر','خط','كتابة داخل','لافتة'] }
]
