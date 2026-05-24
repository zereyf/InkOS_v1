from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from engine.refiner import run_refinement_and_audit
from vault.vault_engine import authenticate_terminal, get_user_profile
from security.token import create_access_token

app = FastAPI(title="InkOS Intelligence API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Schemas ---
class LoginRequest(BaseModel):
    user_hash: str
    pin: str
    is_new: bool = False

class RefinementRequest(BaseModel):
    intent: str
    target_model: str
    framework: str
    source_lang: str
    aesthetic_choice: str = "Default"
    hikmah_style: str = "None"
    skip_security: bool = False
    token: str  # The VIP Keycard

class RefinementResponse(BaseModel):
    refined_prompt: str
    audit: dict
    error: Optional[str] = None

# --- Endpoints ---
@app.get("/health")
def health_check():
    return {"status": "Uplink Active", "system": "InkOS Backend"}

@app.post("/api/auth")
def terminal_login(req: LoginRequest):
    # Route directly into your custom PBKDF2 vault logic
    success, message = authenticate_terminal(req.user_hash, req.pin, is_new=req.is_new)
    
    if not success:
        raise HTTPException(status_code=401, detail=message)
        
    # If successful, pull their clearance level
    profile = get_user_profile(req.user_hash)
    is_admin = profile.get("is_admin", False)
    
    # Mint the keycard
    token = create_access_token(req.user_hash, is_admin)
    
    return {
        "status": "Authenticated", 
        "token": token, 
        "is_admin": is_admin,
        "message": message
    }

@app.post("/api/refine", response_model=RefinementResponse)
def refine_endpoint(req: RefinementRequest):
    # Verify the keycard before spending any compute
    from security.token import verify_token
    user_data = verify_token(req.token)
    
    if not user_data:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid or expired uplink token.")

    refined, audit, error = run_refinement_and_audit(
        master_payload=req.intent, 
        target=req.target_model,
        framework=req.framework,
        lang=req.source_lang,
        aesthetic_choice=req.aesthetic_choice,
        hikmah_style=req.hikmah_style,
        skip_security=req.skip_security
    )
    
    if error:
        raise HTTPException(status_code=500, detail=str(error))
        
    return RefinementResponse(
        refined_prompt=refined,
        audit=audit
    )