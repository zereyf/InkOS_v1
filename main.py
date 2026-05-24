"""
main.py — InkOS FastAPI Backend
=================================
Headless entry point for the CIPHER engine.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# Import your existing engine
from engine.refiner import run_refinement_and_audit

app = FastAPI(title="InkOS Intelligence API")

# Crucial for decoupled architecture: Allow the frontend to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # We will lock this down to your Vercel domain later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RefinementRequest(BaseModel):
    intent: str
    target_model: str
    framework: str
    source_lang: str
    aesthetic_choice: str = "Default"
    hikmah_style: str = "None"
    skip_security: bool = False

class RefinementResponse(BaseModel):
    refined_prompt: str
    audit: dict
    error: Optional[str] = None

@app.get("/health")
def health_check():
    return {"status": "Uplink Active", "system": "InkOS Backend"}

@app.post("/api/refine", response_model=RefinementResponse)
def refine_endpoint(req: RefinementRequest):
    try:
        # In a real setup, we'd assemble the payload here using forge.prompt_assembler
        # For now, we pass the raw intent to test the wiring
        
        refined, audit, error = run_refinement_and_audit(
            master_payload=req.intent, # You'll swap this with assemble_master_payload later
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
    except Exception as e:
        # A senior engineer never swallows this blindly in an API
        print(f"[API_FAULT] {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Neural Refraction Error")