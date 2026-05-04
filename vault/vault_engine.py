"""
vault/vault_engine.py — Prompt Memory Vault Engine
====================================================
All database operations for the Vault feature.
UI never touches Supabase directly — it calls these functions.

Design principles:
  - Every function returns (data, error_string_or_None)
  - Caller decides how to surface errors — no silent failures
  - All operations scoped to user_hash — no cross-user data leaks
  - Tags stored as comma-separated string — simple, searchable, no JSON overhead

User identity:
  Anonymous hash derived from a session UUID stored in st.session_state.
  No login required. Consistent within a session, resets on clear.
  Good enough for a solo/small-team professional tool.
"""

import hashlib
from datetime import datetime
from typing import Optional, Tuple, List
from vault.supabase_client import sb, SUPABASE_MISSING

TABLE = "vault"


def _require_sb() -> Optional[str]:
    """Returns error string if Supabase is unavailable, None if ready."""
    if SUPABASE_MISSING or sb is None:
        return "Vault unavailable — SUPABASE_URL or SUPABASE_KEY not configured."
    return None


def save_prompt(
    user_hash:  str,
    title:      str,
    tags:       str,
    content:    str,
    target:     str,
    framework:  str,
    score:      int,
    pattern:    str,
    islamic:    bool,
    aesthetic:  str,
) -> Tuple[Optional[dict], Optional[str]]:
    """
    Save a refined prompt to the vault.
    Returns (saved_record, error).
    Deduplicates by content hash — same prompt cannot be saved twice.
    """
    if err := _require_sb():
        return None, err

    # Content-based ID — prevents duplicate saves of identical prompts
    record_id = hashlib.md5(f"{user_hash}{content}".encode()).hexdigest()[:16]

    record = {
        "id":         record_id,
        "user_hash":  user_hash,
        "title":      title.strip()[:120],   # hard cap on title length
        "tags":       tags.strip().lower(),  # normalized for consistent search
        "content":    content,
        "target":     target,
        "framework":  framework,
        "score":      min(max(int(score), 0), 100),
        "pattern":    pattern or "",
        "islamic":    islamic,
        "aesthetic":  aesthetic or "",
        "created_at": datetime.utcnow().isoformat(),
    }

    try:
        # upsert = update if exists, insert if not
        res = sb.table(TABLE).upsert(record).execute()
        return res.data[0] if res.data else record, None
    except Exception as e:
        return None, f"Save failed: {str(e)}"


def search_vault(
    user_hash:  str,
    query:      str = "",
    tag_filter: str = "",
    target_filter: str = "",
    min_score:  int = 0,
    limit:      int = 50,
) -> Tuple[List[dict], Optional[str]]:
    """
    Search vault entries for a user.
    Filters: free-text query (title + tags), tag, target AI, minimum score.
    Returns newest-first.
    """
    if err := _require_sb():
        return [], err

    try:
        q = (
            sb.table(TABLE)
            .select("*")
            .eq("user_hash", user_hash)
            .gte("score", min_score)
            .order("created_at", desc=True)
            .limit(limit)
        )

        # Tag filter — substring match on comma-separated tag string
        if tag_filter:
            q = q.ilike("tags", f"%{tag_filter.lower()}%")

        # Target AI filter
        if target_filter and target_filter != "All":
            q = q.eq("target", target_filter)

        # Free-text: filter client-side after fetch
        # WHY: Supabase free tier doesn't expose full-text search on arbitrary columns
        # without additional setup. Client-side filter on small result sets is fine.
        res = q.execute()
        results: List[dict] = res.data or []

        if query.strip():
            q_lower = query.strip().lower()
            results = [
                r for r in results
                if q_lower in r["title"].lower()
                or q_lower in r["tags"].lower()
                or q_lower in r["content"].lower()
            ]

        return results, None

    except Exception as e:
        return [], f"Search failed: {str(e)}"


def delete_prompt(
    user_hash: str,
    record_id: str,
) -> Tuple[bool, Optional[str]]:
    """
    Delete a vault entry by ID.
    Scoped to user_hash — users can only delete their own prompts.
    Returns (success, error).
    """
    if err := _require_sb():
        return False, err

    try:
        sb.table(TABLE)\
            .delete()\
            .eq("id", record_id)\
            .eq("user_hash", user_hash)\
            .execute()
        return True, None
    except Exception as e:
        return False, f"Delete failed: {str(e)}"


def get_vault_stats(user_hash: str) -> Tuple[dict, Optional[str]]:
    """
    Returns aggregate stats for sidebar display.
    count, avg_score, top_target, top_tag.
    """
    if err := _require_sb():
        return {"count": 0, "avg_score": 0, "top_target": "—", "top_tag": "—"}, err

    try:
        res = sb.table(TABLE)\
            .select("score, target, tags")\
            .eq("user_hash", user_hash)\
            .execute()

        entries: List[dict] = res.data or []
        if not entries:
            return {"count": 0, "avg_score": 0, "top_target": "—", "top_tag": "—"}, None

        count     = len(entries)
        avg_score = round(sum(e["score"] for e in entries) / count)

        # Top target
        from collections import Counter
        target_counts = Counter(e["target"] for e in entries)
        top_target = target_counts.most_common(1)[0][0] if target_counts else "—"

        # Top tag — flatten all tags, count individually
        all_tags = []
        for e in entries:
            all_tags.extend([t.strip() for t in e["tags"].split(",") if t.strip()])
        tag_counts = Counter(all_tags)
        top_tag = tag_counts.most_common(1)[0][0] if tag_counts else "—"

        return {
            "count":      count,
            "avg_score":  avg_score,
            "top_target": top_target,
            "top_tag":    top_tag,
        }, None

    except Exception as e:
        return {"count": 0, "avg_score": 0, "top_target": "—", "top_tag": "—"}, f"Stats failed: {str(e)}"


def get_all_tags(user_hash: str) -> List[str]:
    """Returns sorted list of unique tags for filter dropdowns."""
    if SUPABASE_MISSING or sb is None:
        return []
    try:
        res = sb.table(TABLE).select("tags").eq("user_hash", user_hash).execute()
        all_tags = []
        for row in (res.data or []):
            all_tags.extend([t.strip() for t in row["tags"].split(",") if t.strip()])
        return sorted(set(all_tags))
    except Exception:
        return []

