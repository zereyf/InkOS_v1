from types import MappingProxyType

AUTO_SELECT_LABEL = "✦ AUTO_SELECT"

TARGET_SELECTION_GUIDE = "Auto-routes based on detected intent. Select manually to override."

# ── TARGET GUIDELINES ────────────────────────────────────────────────────────
TARGET_GUIDES = MappingProxyType({
    'ChatGPT': (
        'Direct, conversational, and highly creative. '
        'Best for brainstorming, storytelling, and rapid copy drafting.'
    ),
    'Claude': (
        'Structure output using XML tags: <role>, <task>, <constraints>, <output_format>. '
        'Analytical, precise tone. State evaluation criteria before the task.'
    ),
    'Midjourney/Flux': (
        'Visual production prompts. Use :: separators. '
        'Include lighting, lens, and style slots. No conversational filler.'
    ),
    'Gemini (Imagen 3)': (
        'Best for text-integrated visuals and signage. '
        'Describe the exact text to be rendered within the image.'
    ),
    'DALL-E 3': (
        'Requires rich natural language, cinematic scene descriptions, full sentences, NO :: separators.'
    ),
    'Manus AI': (
        'Agentic workflows. Optimized for multi-step reasoning and tool-use simulation via Claude.'
    )
})

# ── ROUTING TABLE ────────────────────────────────────────────────────────────
# Pre-normalized Arabic substrings to match v4.2 router logic.
TARGET_ROUTING_TABLE: list = [
  # ── CODE & TECHNICAL ──────────────────────────────────────────────
  { 
    'category': 'code', 'target': 'Claude', 'score': 10,
    'rationale': 'Technical implementation/Logic — Anthropic Core',
    'en_patterns': [
        r'\bpython\b', r'\bjavascript\b', r'\bsql\b', r'\bprogramming\b',
        r'\bscripting\b', r'\bdebug\b', r'\brefactor\b', r'\bapi\b',
        r'\bhtml\b', r'\bcss\b', r'\breact\b', r'\bnode\b',
        r'\bfunction\b', r'\bclass\b', r'\balgorithm\b',
        r'\bbackend\b', r'\bfrontend\b', r'\bjson\b'
    ],
    'ar_substrings': ['برمجه', 'كود', 'سكربت', 'خوارزميه', 'مطور', 'برنامج', 'بايثون'] 
  },

  # ── RESEARCH & ANALYSIS ───────────────────────────────────────────
  { 
    'category': 'research', 'target': 'Claude', 'score': 8,
    'rationale': 'Deep analysis and scholarly formatting — Anthropic Core',
    'en_patterns': [
        r'\bessay\b', r'\breport\b', r'\banalysis\b', r'\bresearch\b',
        r'\bacademic\b', r'\bthesis\b', r'\bcritique\b',
        r'\bsummarize\b', r'\bcompare\b', r'\bevaluate\b'
    ],
    'ar_substrings': ['بحث', 'تحليل', 'دراسه', 'مقارنه', 'اكاديمي'] 
  },

  # ── ARABIC / ISLAMIC ──────────────────────────────────────────────
  { 
    'category': 'arabic_islamic', 'target': 'Claude', 'score': 9,
    'rationale': 'Linguistic depth and cultural nuance — Anthropic Core',
    'en_patterns': [
        r'\bisla[mn]ic?\b', r'\bsharia\b', r'\bquran\b',
        r'\bhadith\b', r'\barabic\b', r'\bfiqh\b'
    ],
    'ar_substrings': ['اسلام', 'شريعه', 'قران', 'حديث', 'فقه', 'عربي', 'عربيه'] 
  },

  # ── MARKETING & SOCIAL ───────────────────────────────────────────
  { 
    'category': 'marketing', 'target': 'ChatGPT', 'score': 8,
    'rationale': 'Persuasive copywriting and social hooks — GPT-4o',
    'en_patterns': [
        r'\btweet\b', r'\bcaption\b', r'\badvertisement\b', r'\bslogan\b',
        r'\bhook\b', r'\bheadline\b', r'\bemail\b',
        r'\bmarketing\b', r'\bcampaign\b', r'\bseo\b', r'\bviral\b'
    ],
    'ar_substrings': ['اعلان', 'تسويق', 'محتوي', 'كابشن', 'تغريده'] 
  },

  # ── CREATIVE WRITING ──────────────────────────────────────────────
  { 
    'category': 'creative', 'target': 'ChatGPT', 'score': 7,
    'rationale': 'Creative narrative and brainstorming — GPT-4o',
    'en_patterns': [
        r'\bstory\b', r'\bscript\b', r'\bnarrative\b', r'\bfiction\b',
        r'\bbrainstorm\b', r'\bcreative\b', r'\bpoem\b', r'\bdialogue\b'
    ],
    'ar_substrings': ['قصه', 'سكريبت', 'ابداع', 'خيال', 'افكار', 'حوار'] 
  },

  # ── AUTOMATION & AGENTS ───────────────────────────────────────────
  { 
    'category': 'agentic', 'target': 'Manus AI', 'score': 10,
    'rationale': 'Agentic multi-step task execution — Manus AI',
    'en_patterns': [
        r'\bautomation?\b', r'\bagent\b', r'\bworkflow\b',
        r'\bpipeline\b', r'\bscrape\b', r'\bcrawl\b',
        r'\bscheduled?\b', r'\bbatch\b', r'\bbrowser\b'
    ],
    'ar_substrings': ['اتمته', 'وكيل', 'سير عمل', 'مهمه متعدده'] 
  },

  # ── IMAGE: STYLIZED ───────────────────────────────────────────────
  { 
    'category': 'image_stylized', 'target': 'Midjourney/Flux', 'score': 9,
    'rationale': 'Aesthetic artistic production — Diffusion Matrix',
    'en_patterns': [
        r'\banime\b', r'\billustrat\b', r'\bconcept\s+art\b',
        r'\bcinematic\b', r'\bwallpaper\b', r'\bcharacter\s+design\b',
        r'\bfantasy\b', r'\btech.?noir\b', r'\bsci.?fi\b',
        r'\bartistic\b', r'\bstylized\b'
    ],
    'ar_substrings': ['انمي', 'رسوم', 'تصوير فني', 'خيال علمي', 'شخصيه'] 
  },

  # ── IMAGE: PHOTOREALISTIC ─────────────────────────────────────────
  { 
    'category': 'image_photo', 'target': 'DALL-E 3', 'score': 9,
    'rationale': 'High-fidelity photorealistic scene generation — DALL-E 3',
    'en_patterns': [
        r'\bphoto\b', r'\bphotograph\b', r'\bphoto.?realistic\b',
        r'\bportrait\b', r'\bproduct\s+shot\b', r'\bhyperrealistic\b'
    ],
    'ar_substrings': ['صوره واقعيه', 'تصوير', 'بورتريه'] 
  },

  # ── IMAGE: TEXT IN IMAGE ──────────────────────────────────────────
  { 
    'category': 'image_text', 'target': 'Gemini (Imagen 3)', 'score': 10,
    'rationale': 'Precise text-in-image and signage — Gemini Imagen 3',
    'en_patterns': [
        r'\blogo\b', r'\bbanner\b', r'\bsignage\b',
        r'\btypography\b', r'\btext\s+in\b', r'\bwith\s+text\b',
        r'\bwith\s+the\s+word\b', r'\blabel\b', r'\bui\s+mock\b'
    ],
    'ar_substrings': ['شعار', 'بنر', 'خط', 'كتابه داخل', 'لافته'] 
  }
]
