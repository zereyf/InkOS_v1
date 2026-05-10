"""
forge/intelligence.py — Neural Routing Engine
=============================================
v2.0: Data-Driven Resolver.
      - CONSUMES: config.targets.TARGET_ROUTING_TABLE.
      - ENGINE: Regex pattern matching + Arabic substring intercept.
"""

import re
from state import K
from config.targets import AUTO_SELECT_LABEL, TARGET_ROUTING_TABLE

def evaluate_mission_complexity(user_input: str) -> dict:
    """
    Scans the routing table to find the highest-scoring model match.
    """
    scores = {} # { 'Claude': 10, 'ChatGPT': 7 }
    rationales = {}

    for entry in TARGET_ROUTING_TABLE:
        target = entry['target']
        match_found = False
        
        # 1. Check English Patterns (Regex)
        if any(re.search(p, user_input, re.I) for p in entry['en_patterns']):
            match_found = True
            
        # 2. Check Arabic Substrings (Linguistic Intercept)
        if not match_found and any(sub in user_input for sub in entry['ar_substrings']):
            match_found = True
            
        if match_found:
            current_score = entry['score']
            if current_score > scores.get(target, 0):
                scores[target] = current_score
                rationales[target] = entry['rationale']

    # Find the winner
    if not scores:
        return {
            "target": "ChatGPT", 
            "reason": "NEUTRAL_ROUTING: No specific pattern detected. Defaulting to generalist."
        }

    winner = max(scores, key=scores.get)
    return {
        "target": winner,
        "reason": f"PATTERN_MATCH: {rationales[winner]}"
    }

def resolve_target_model(user_selection: str, user_input: str) -> tuple[str, str]:
    """Resolves Auto-Select label or respects manual choice."""
    if user_selection != AUTO_SELECT_LABEL:
        return user_selection, "MANUAL_OVERRIDE: Target locked by user."
    
    suggestion = evaluate_mission_complexity(user_input)
    return suggestion["target"], suggestion["reason"]
