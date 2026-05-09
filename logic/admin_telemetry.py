"""
logic/admin_telemetry.py
========================
v1.0: Real-time database telemetry for Overwatch.
"""
from vault.supabase_client import supabase, SUPABASE_MISSING

def get_global_metrics():
    """Fetches high-level system stats from Supabase."""
    if SUPABASE_MISSING:
        return {"users": 0, "personas": 0, "logs": 0}
    
    # 1. Count Total Identities
    users = supabase.table("identities").select("user_hash", count="exact").execute()
    # 2. Count Total Personas
    personas = supabase.table("personas").select("id", count="exact").execute()
    # 3. Count Security Anomalies (Failed Logins)
    logs = supabase.table("security_logs").select("id", count="exact").execute()
    
    return {
        "users": users.count if users.count else 0,
        "personas": personas.count if personas.count else 0,
        "logs": logs.count if logs.count else 0
    }

def get_recent_activity(limit=10):
    """Retrieves the latest system events."""
    if SUPABASE_MISSING:
        return []
    response = supabase.table("security_logs").select("*").order("created_at", desc=True).limit(limit).execute()
    return response.data
