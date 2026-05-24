from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

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

class RefinementRequest(BaseModel):
    intent: str
    target_model: str
    framework: str = "Professional (RACE)"
    source_lang: str = "English"
    aesthetic_choice: str = "Default"
    hikmah_style: str = "None"
    skip_security: bool = False
    token: str  # The VIP Keycard

class RefinementResponse(BaseModel):
    refined_prompt: str
    audit: dict
    error: Optional[str] = None


# ── ENDPOINTS ──
@app.get("/health")
def health_check():
    return {"status": "Uplink Active", "system": "InkOS Backend"}

@app.post("/api/auth")
def terminal_login(req: LoginRequest):
    success, message = authenticate_terminal(req)