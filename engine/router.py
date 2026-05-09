"""
engine/router.py — The Cognitive Router
=======================================
v4.0: Hardened Routing Matrix.
      - Dual-Language Intercept (EN Regex + AR Substrings).
      - Zero-Crash Dictionary Lookups.
      - Short-Circuit Empty Payload Handlers.
"""

import re
from typing import Tuple, Dict, Any

# Ensure this path matches your exact config structure
from config.targets import TARGET_ROUTING_TABLE

def route_to_target(user_text: str) -> Tuple[str, str]:
    """
    Evaluates the raw uplink text against the TARGET_ROUTING_TABLE.
    Returns (Optimal_Target, Rationale).
    Tie goes to the first-defined rule (table order = priority).
    """
    # 1. Short-Circuit: Empty Payload Check
    if not user_text or not user_text.strip():
        return "ChatGPT", "Empty payload. Defaulting to general-purpose matrix."

    text = user_text.lower()
    scores: Dict[str, int] = {}
    rationales: Dict[str, str] = {}

    for rule in TARGET_ROUTING_TABLE:
        target = rule.get('target')
        if not target:
            continue
            
        matched = False
        
        # 2. Scan English Regex Patterns
        for pat in rule.get('en_patterns', []):
            if re.search(pat, text):
                matched = True
                break
                
        # 3. Scan Arabic Substrings (Fallback if no EN match)
        if not matched:
            for substr in rule.get('ar_substrings', []):
                if substr in text:
                    matched = True
                    break
                    
        # 4. Apply Scoring Matrix
        if matched:
            score_val = rule.get('score', 0)
            scores[target] = scores.get(target, 0) + score_val
            
            # Lock in the first rationale triggered for this target
            if target not in rationales:
                rationales[target] = rule.get('rationale', 'Pattern matched.')

    # 5. Resolution & Tie-Breaker
    if not scores:
        return "ChatGPT", "No specific signal detected. Defaulting to general-purpose."

    # Python dict insertion order guarantees ties go to the first matched target
    best_target = max(scores, key=scores.get)
    return best_target, rationales[best_target]


def explain_routing(user_text: str) -> Dict[str, Any]:
    """
    Diagnostic mode — returns a full forensic signal breakdown.
    Used exclusively in Expert Diagnostics mode.
    """
    if not user_text or not user_text.strip():
        return {'winner': 'ChatGPT', 'scores': {}, 'signal_breakdown': []}

    text = user_text.lower()
    breakdown = []
    
    for rule in TARGET_ROUTING_TABLE:
        matched_triggers = []
        
        for pat in rule.get('en_patterns', []):
            if re.search(pat, text): 
                matched_triggers.append(pat)
                
        for substr in rule.get('ar_substrings', []):
            if substr in text: 
                matched_triggers.append(substr)
                
        if matched_triggers:
            breakdown.append({
                'category': rule.get('category', 'UNKNOWN'), 
                'target': rule.get('target', 'UNKNOWN'),
                'score': rule.get('score', 0), 
                'matched': matched_triggers
            })
            
    agg_scores: Dict[str, int] = {}
    for e in breakdown:
        tgt = e['target']
        agg_scores[tgt] = agg_scores.get(tgt, 0) + e['score']
        
    winner = max(agg_scores, key=agg_scores.get) if agg_scores else 'ChatGPT'
    
    return {
        'winner': winner, 
        'scores': agg_scores, 
        'signal_breakdown': breakdown
    }
