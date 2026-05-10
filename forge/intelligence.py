"""
forge/intelligence.py — Proactive Routing Engine
===================================================
v1.1: Autonomous Resolver.
"""
import re
from state import K
from config import TARGET_GUIDES, AUTO_SELECT_LABEL

def evaluate_mission_complexity(user_input: str) -> dict:
    """Heuristic scan of input complexity."""
    length = len(user_input)
    
    # Priority 1: High Context / Long-form Arabic
    if length > 5000 or re.search(r"[\u0600-\u06FF]{50,}", user_input):
        return {"target": "Claude 3.5 Sonnet", "reason": "LINGUISTIC_HIKMAH: High-fidelity Arabic/Context depth."}
    
    # Priority 2: Technical/Coding Syntax
    if any(word in user_input for word in ["def ", "class ", "git ", "patch", "sql"]):
        return {"target": "GPT-4o", "reason": "LOGIC_DENSITY: Structural code optimization required."}
    
    # Priority 3: Default Efficiency
    return {"target": "GPT-4o mini", "reason": "EFFICIENCY_MODE: Rapid low-latency execution."}

def resolve_target_model(user_selection: str, user_input: str) -> tuple[str, str]:
    """
    Final decision gate. 
    Returns: (Actual Model Name, Reasoning String)
    """
    if user_selection != AUTO_SELECT_LABEL:
        return user_selection, "MANUAL_OVERRIDE: User selected specific node."
    
    suggestion = evaluate_mission_complexity(user_input)
    return suggestion["target"], suggestion["reason"]
