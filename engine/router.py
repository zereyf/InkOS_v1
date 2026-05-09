"""
engine/router.py — The Cognitive Router
=======================================
v4.1: Linguistic Resilience Patch.
      - Arabic Normalization (Tashkeel/Alif Unification).
      - Score-Weighted Rationale Persistence.
      - Diagnostic Signal Forensic Integrity.
"""

import re
from typing import Tuple, Dict, Any

# Ensure this path matches your exact config structure
from config.targets import TARGET_ROUTING_TABLE

def _normalize_text(text: str) -> str:
    """
    Normalizes Arabic characters to ensure substring matching hits 
    regardless of diacritics (Tashkeel) or Alif variations.
    """
    # Remove Arabic diacritics (Fatha, Damma, Kasra, etc.)
    text = re.sub(r"[\u064B-\u0652]", "", text)
    # Unify Alif variations (أ, إ, آ) to plain Alif (ا)
    text = re.sub(r"[أإآ]", "ا", text)
    # Unify Alif Maqsura (ى) and Ya (ي)
    text = re.sub(r"ى", "ي", text)
    return text

def route_to_target(user_text: str) -> Tuple[str, str]:
    """
    Evaluates raw uplink text against the TARGET_ROUTING_TABLE.
    Returns (Optimal_Target, Rationale).
    """
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
        
        # 1. English Regex Patterns (Raw scan)
        for pat in rule.get('en_patterns', []):
            if re.search(pat, raw_lower):
                matched = True
                break
                
        # 2. Arabic Substrings (Normalized scan)
        if not matched:
            for substr in rule.get('ar_substrings', []):
                if _normalize_text(substr.lower()) in norm_lower:
                    matched = True
                    break
                    
        # 3. Apply Scoring & Rationale Logic
        if matched:
            weight = rule.get('score', 0)
            scores[target] = scores.get(target, 0) + weight
            
            # Update rationale only if this specific rule is more 'authoritative' 
            # than previous matches for the same target.
            if weight > best_rule_weight.get(target, -1):
                best_rule_weight[target] = weight
                rationales[target] = rule.get('rationale', 'Pattern matched.')

    if not scores:
        return "ChatGPT", "No specific signal detected. Defaulting to general-purpose."

    # Tie-breaker: max value. insertion order handles equal scores.
    best_target = max(scores, key=scores.get)
    return best_target, rationales.get(best_target, "Pattern matched.")


def explain_routing(user_text: str) -> Dict[str, Any]:
    """
    Diagnostic mode — returns a full forensic signal breakdown.
    """
    if not user_text or not user_text.strip():
        return {'winner': 'ChatGPT', 'scores': {}, 'signal_breakdown': []}

    raw_lower = user_text.lower()
    norm_lower = _normalize_text(raw_lower)
    breakdown = []
    
    for rule in TARGET_ROUTING_TABLE:
        matched_triggers = []
        
        for pat in rule.get('en_patterns', []):
            if re.search(pat, raw_lower): 
                matched_triggers.append(f"EN_REG: {pat}")
                
        for substr in rule.get('ar_substrings', []):
            if _normalize_text(substr.lower()) in norm_lower: 
                matched_triggers.append(f"AR_SUB: {substr}")
                
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
