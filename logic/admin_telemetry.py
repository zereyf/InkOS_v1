"""
logic/admin_telemetry.py — Overwatch Data Engine
"""
from vault.supabase_client import supabase, SUPABASE_MISSING # 🟢 Changed sb to supabase

def get_global_metrics():
    """Fetches stats from the database safely."""
    stats = {"users": 0, "personas": 0, "logs": 0}
    if SUPABASE_MISSING or not supabase:
        return stats
    
    try:
        # Changed 'sb' to 'supabase' below
        u_res = supabase.table("users").select("id", count="exact").execute()
        stats["users"] = u_res.count if u_res.count else 0
        
        p_res = supabase.table("personas").select("id", count="exact").execute()
        stats["personas"] = p_res.count if p_res.count else 0
        
        v_res = supabase.table("vault").select("id", count="exact").execute()
        stats["logs"] = v_res.count if v_res.count else 0
    except Exception:
        pass
    return stats

def get_recent_activity(limit=10):
    if SUPABASE_MISSING or not supabase:
        return []
    try:
        # Changed 'sb' to 'supabase' below
        res = supabase.table("security_logs").select("*").order("created_at", desc=True).limit(limit).execute()
        return res.data
    except Exception:
        return []
