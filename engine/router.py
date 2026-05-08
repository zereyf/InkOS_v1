import re
from config.targets import TARGET_ROUTING_TABLE

def route_to_target(user_text: str) -> tuple[str, str]:
    """
    Score all routing rules. Return (target_name, rationale).
    Tie goes to first-defined rule (table order = priority).
    """
    text = user_text.lower()
    scores: dict[str, int] = {}
    rationales: dict[str, str] = {}

    for rule in TARGET_ROUTING_TABLE:
        target = rule['target']
        matched = False
        for pat in rule.get('en_patterns', []):
            if re.search(pat, text):
                matched = True
                break
        if not matched:
            for substr in rule.get('ar_substrings', []):
                if substr in text:
                    matched = True
                    break
        if matched:
            scores[target] = scores.get(target, 0) + rule['score']
            if target not in rationales:
                rationales[target] = rule['rationale']

    if not scores:
        return 'ChatGPT', 'No signal detected. Default: general-purpose.'

    best = max(scores, key=lambda t: scores[t])
    return best, rationales[best]


def explain_routing(user_text: str) -> dict:
    """Debug mode — returns full signal breakdown. Use in expert diagnostics."""
    text = user_text.lower()
    breakdown = []
    for rule in TARGET_ROUTING_TABLE:
        matched = []
        for pat in rule.get('en_patterns', []):
            if re.search(pat, text): matched.append(pat)
        for s in rule.get('ar_substrings', []):
            if s in text: matched.append(s)
        if matched:
            breakdown.append({'category': rule['category'], 'target': rule['target'],
                              'score': rule['score'], 'matched': matched})
    agg = {}
    for e in breakdown:
        agg[e['target']] = agg.get(e['target'], 0) + e['score']
    winner = max(agg, key=lambda t: agg[t]) if agg else 'ChatGPT'
    return {'winner': winner, 'scores': agg, 'signal_breakdown': breakdown}
