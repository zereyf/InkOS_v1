"""
forge/intelligence.py — Proactive Routing Engine
===================================================
v1.2: Neural Resolver with Arabic Bias.
"""
import re
from state import K
from config.targets import AUTO_SELECT_LABEL

def evaluate_mission_complexity(user_input: str) -> dict:
    """Heuristic scan of input to find the optimal Neural Node."""
    length = len(user_input)
    
    # Check for Arabic patterns (Trigger Claude)
    has_arabic = bool(re.search(r"[\u0600-\u06FF]", user_input))
    
    if length > 5000 or (has_arabic and length > 1000):
        return {
            "target": "Claude 3.5 Sonnet",
            "reason": "LINGUISTIC_HIKMAH: High-fidelity Arabic / Context depth required."
        }
    
    if any(word in user_input.lower() for word in ["def ", "class ", "git ", "patch", "refactor"]):
        return {
            "target": "GPT-4o",
            "reason": "LOGIC_DENSITY: Structural code optimization required."
        }
    
    return {
        "target": "GPT-4o mini",
        "reason": "EFFICIENCY_MODE: Rapid low-latency execution."
    }

def resolve_target_model(user_selection: str, user_input: str) -> tuple[str, str]:
    """Resolves 'Auto-Select' into a real model or respects manual override."""
    if user_selection != AUTO_SELECT_LABEL:
        return user_selection, "MANUAL_OVERRIDE: Node locked by user."
    
    suggestion = evaluate_mission_complexity(user_input)
    return suggestion["target"], suggestion["reason"]
