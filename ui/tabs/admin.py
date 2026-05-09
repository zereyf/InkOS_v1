"""
logic/admin_telemetry.py
========================
v1.1: Real-time database telemetry for Overwatch.
      - Hardened against missing tables (APIError Fix).
      - Synced with actual Supabase schema (users, personas, vault).
"""
from vault.supabase_client import supabase, SUPABASE_MISSING

def get_global_metrics():
    """Fetches high-level system stats from Supabase safely."""
    stats = {"users": 0, "personas": 0, "logs": 0}
    
    if SUPABASE_MISSING or not supabase:
        return stats
    
    # 1. Count Total Users (Matches TABLE_USERS in vault_engine)
    try:
        u_res = supabase.table("users").select("id", count="exact").execute()
        stats["users"] = u_res.count if u_res.count else 0
    except Exception:
        pass
        
    # 2. Count Total Personas
    try:
        p_res = supabase.table("personas").select("id", count="exact").execute()
        stats["personas"] = p_res.count if p_res.count else 0
    except Exception:
        pass
        
    # 3. Count Total Vault Assets (Used here as "Security Events" placeholder for now)
    try:
        v_res = supabase.table("vault").select("id", count="exact").execute()
        stats["logs"] = v_res.count if v_res.count else 0
    except Exception:
        pass
        
    return stats

def get_recent_activity(limit=10):
    """Retrieves the latest system events without crashing if table is missing."""
    if SUPABASE_MISSING or not supabase:
        return []
        
    try:
        # Assuming you will create a 'security_logs' table later. 
        # If it doesn't exist, this will safely return an empty list.
        res = supabase.table("security_logs").select("*").order("created_at", desc=True).limit(limit).execute()
        return res.data
    except Exception:
        # Return empty list so Pandas DataFrame in admin.py doesn't crash
        return []
