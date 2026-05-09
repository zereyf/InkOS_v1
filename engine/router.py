"""
engine/router.py — The Cognitive Router
=======================================
v4.2: Forensic Resilience Patch.
      - Arabic Normalization (Tashkeel/Alif Unification).
      - Score-Weighted Rationale Capture.
"""

import re
from typing import Tuple, Dict, Any
from config.targets import TARGET_ROUTING_TABLE

def _normalize_text(text: str) -> str:
    """Removes diacritics and unifies Arabic characters for resilient matching."""
    text = re.sub(r"[\u064B-\u0652]", "", text) # Strip Tashkeel
    text = re.sub(r"[أإآ]", "ا", text)           # Unify Alif
    text = re.sub(r"ى", "ي", text)               # Unify Ya
    return text.strip().lower()

def route_to_target(user_text: str) -> Tuple[str, str]:
    if not user_text or not user_text.strip():
        return "ChatGPT", "Empty payload. Defaulting to general-purpose matrix."

    raw_lower = user_text.lower()
    norm_lower = _normalize_text(raw_lower)
    
    scores: Dict[str, int] = {}
    rationales: Dict[str, str] = {}
    best_rule_weight: Dict[str, int] = {}

    for rule in TARGET_ROUTING_TABLE:
        target = rule.get('target')
        if not target: continue
        matched = False
        
        # 1. English Pattern Match
        for pat in rule.get('en_patterns', []):
            if re.search(pat, raw_lower):
                matched = True
                break
                
        # 2. Arabic Pattern Match (Normalized)
        if not matched:
            for substr in rule.get('ar_substrings', []):
                if _normalize_text(substr) in norm_lower:
                    matched = True
                    break
                    
        if matched:
            weight = rule.get('score', 0)
            scores[target] = scores.get(target, 0) + weight
            # Lock rationale to the highest-weighted match for this target
            if weight > best_rule_weight.get(target, -1):
                best_rule_weight[target] = weight
                rationales[target] = rule.get('rationale', 'Pattern matched.')

    if not scores:
        return "ChatGPT", "No specific signal detected. Defaulting to general-purpose."

    best_target = max(scores, key=scores.get)
    return best_target, rationales.get(best_target, "Pattern matched.")

def explain_routing(user_text: str) -> Dict[str, Any]:
    """Forensic breakdown for Expert Diagnostics."""
    if not user_text: return {'winner': 'ChatGPT', 'scores': {}, 'signal_breakdown': []}
    
    raw_lower = user_text.lower()
    norm_lower = _normalize_text(raw_lower)
    breakdown = []
    
    for rule in TARGET_ROUTING_TABLE:
        triggers = [f"EN: {p}" for p in rule.get('en_patterns', []) if re.search(p, raw_lower)]
        triggers += [f"AR: {s}" for s in rule.get('ar_substrings', []) if _normalize_text(s) in norm_lower]
        
        if triggers:
            breakdown.append({
                'target': rule.get('target'),
                'score': rule.get('score'),
                'matched': triggers
            })
            
    return {'winner': route_to_target(user_text)[0], 'signal_breakdown': breakdown}
