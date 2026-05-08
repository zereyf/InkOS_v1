from types import MappingProxyType

LOGIC_FRAMEWORKS: tuple = (
    "Professional (RACE)",
    "Technical (Debugger)",
    "Academic",
    "Creative",
    "Visual Director",
)

FRAMEWORK_BLUEPRINTS = MappingProxyType({
    "Professional (RACE)": (
        "STRUCTURAL SKELETON:\n"
        "  [ROLE] Who is the AI acting as?\n"
        "  [ACTION] What is the specific task?\n"
        "  [CONTEXT] What is the background information?\n"
        "  [EXPECTATION] What are the formatting and tone constraints?"
    ),
    "Technical (Debugger)": (
        "STRUCTURAL SKELETON:\n"
        "  [CURRENT STATE] What is happening right now?\n"
        "  [EXPECTED STATE] What should happen?\n"
        "  [ERROR LOGS] Exact stack trace or failure mode.\n"
        "  [ENVIRONMENT] Language, framework, and tool versions."
    ),
    "Academic": (
        "STRUCTURAL SKELETON:\n"
        "  [THESIS] Core argument or research question.\n"
        "  [METHODOLOGY] How the AI should approach the analysis.\n"
        "  [SYNTHESIS] How to combine the evidence.\n"
        "  [CONSTRAINTS] Academic tone, citation style, and logical fallacies to avoid."
    ),
    "Creative": (
        "STRUCTURAL SKELETON:\n"
        "  [PREMISE/HOOK] The core concept or opening hook.\n"
        "  [NARRATIVE ARC] The structure or progression of the output.\n"
        "  [PACING/TONE] The emotional rhythm (e.g., fast-paced, solemn, punchy).\n"
        "  [CLICHES TO AVOID] Specific tropes or overused phrases the AI must NOT use."
    )
})

GOLDEN_FEW_SHOT_BLUEPRINT: str = """
━━━ FRAMEWORK INTEGRATION RULE (CRITICAL) ━━━
You MUST explicitly write out the bracketed tags from the ACTIVE FRAMEWORK (e.g., [PREMISE/HOOK], [CURRENT STATE]) inside your final generated prompt. Do not silently fulfill them—print the actual brackets to structure the prompt.

Example 1: Claude + Technical Framework
<task>
  [CURRENT STATE] The app crashes on load.
  [EXPECTED STATE] It should render the widget.
</task>
"""
