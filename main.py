from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from vault.database import supabase

from engine.refiner import run_refinement_and_audit
from vault.vault_engine import authenticate_terminal, get_user_profile, rehydrate_session, get_vault_items
from security.token import create_access_token, verify_token
from forge.prompt_assembler import assemble_master_payload
from security.sanitizer import sanitize_input

app = FastAPI(title="InkOS Intelligence API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── SCHEMAS ──
class LoginRequest(BaseModel):
    user_hash: str
    pin: str
    is_new: bool = False

class RefineRequest(BaseModel):
    intent: str
    target_model: str
    framework: str
    source_lang: str
    aesthetic_choice: str
    hikmah_style: str
    operator_context: Optional[str] = ""  # The active DNA catcher
    skip_security: bool
    token: str

class RefinementResponse(BaseModel):
    refined_prompt: str
    audit: dict
    error: Optional[str] = None

class ProfileUpdateRequest(BaseModel):
    user_hash: str
    token: str
    alias: str
    age: str
    role: str
    context: str


# ── ENDPOINTS ──
@app.get("/health")
def health_check():
    return {"status": "Uplink Active", "system": "InkOS Backend"}

@app.post("/api/auth")
def terminal_login(req: LoginRequest):
    success, message = authenticate_terminal(req.user_hash, req.pin, is_new=req.is_new)
    if not success:
        raise HTTPException(status_code=401, detail=message)
        
    profile = get_user_profile(req.user_hash)
    is_admin = profile.get("is_admin", False)
    token = create_access_token(req.user_hash, is_admin)
    
    return {"status": "Authenticated", "token": token, "is_admin": is_admin, "message": message}

@app.post("/api/refine", response_model=RefinementResponse)
def refine_endpoint(req: RefineRequest): # [FIXED] Changed RefinementRequest to RefineRequest
    # 1. Vault Check: Verify the Keycard
    user_data = verify_token(req.token)
    if not user_data:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid or expired uplink token.")
    
    user_hash = user_data.get("sub")

    # 2. Context Rehydration: Fetch User DNA from Supabase
    session_data = rehydrate_session(user_hash)
    cached_dna = session_data.get("dna", {})

    # 3. Overwatch Security Intercept: Sanitize raw input BEFORE assembly
    if not req.skip_security:
        cleaned_intent, violations = sanitize_input(req.intent)
        if violations:
            sig = " | ".join(violations)
            return RefinementResponse(
                refined_prompt=f"OVERWATCH INTERCEPT: Hostile patterns detected.\nSIGNATURE: {sig}",
                audit={"score": 0, "critique": f"SECURITY_BREACH: {sig}"}
            )
        req.intent = cleaned_intent

    # 4. Compile Master Payload (Arabic Cognitive Map + Persona Rules)
    config = {
        "target_model": req.target_model,
        "hikmah_style": req.hikmah_style,
        "islamic_mode": False 
    }
    
    # [FIXED] Force the live DNA from the frontend UI into the payload object
    # If the UI sent operator_context, it overrides the database cache.
    active_dna = {"context": req.operator_context} if req.operator_context else cached_dna

    try:
        master_payload = assemble_master_payload(
            user_input=req.intent,
            config=config,
            dna=active_dna # INJECTED LIVE DNA HERE
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Assembler Fault: {str(e)}")

    # 5. Intelligence Core: Fire payload to Groq/Llama-3
    refined, audit, error = run_refinement_and_audit(
        master_payload=master_payload, 
        target=req.target_model,
        framework=req.framework,
        lang=req.source_lang,
        aesthetic_choice=req.aesthetic_choice,
        hikmah_style=req.hikmah_style,
        skip_security=True # Bypass inner check to avoid auto-immune crash
    )
    
    if error:
        raise HTTPException(status_code=500, detail=str(error))
        
    return RefinementResponse(
        refined_prompt=refined,
        audit=audit
    )

@app.get("/api/vault")
def fetch_vault_history(token: str):
    # 1. Verify the Keycard
    user_data = verify_token(token)
    if not user_data:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid or expired uplink token.")
    
    user_hash = user_data.get("sub")

    # 2. Retrieve history from Supabase
    items, error = get_vault_items(user_hash, limit=50)
    
    if error:
        raise HTTPException(status_code=500, detail=f"Database Fault: {error}")
        
    return {"status": "success", "items": items}

@app.post("/api/profile")
async def update_profile(req: ProfileUpdateRequest):
    # 1. Verify the Keycard for the profile update
    user_data = verify_token(req.token)
    if not user_data:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid or expired uplink token.")

    try:
        # [!] Ensure your supabase client is imported at the top of the file to execute this
        response = supabase.table("users").update({
            "alias": req.alias,
            "age": req.age,
            "role": req.role,
            "context": req.context
        }).eq("user_hash", req.user_hash).execute()

        if not response.data:
            raise HTTPException(status_code=400, detail="Operator ID not found in the vault.")

        return {"status": "success", "message": "DNA successfully integrated."}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database synchronization failed: {str(e)}")