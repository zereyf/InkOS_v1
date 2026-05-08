import os
from typing import Optional
from dotenv import load_dotenv
from groq import Groq

load_dotenv(override=True)

_api_key: str = os.getenv('GROQ_API_KEY', '').strip()
API_KEY_MISSING: bool = not bool(_api_key)
client: Optional[Groq] = Groq(api_key=_api_key) if _api_key else None

MODEL_ID:       str   = os.getenv('INKOS_MODEL_ID', 'llama-3.3-70b-versatile')
AUDIO_MODEL_ID: str   = os.getenv('INKOS_AUDIO_MODEL', 'whisper-large-v3-turbo')
TEMPERATURE:    float = float(os.getenv('INKOS_TEMPERATURE', '0.3'))
MAX_TOKENS:     int   = int(os.getenv('INKOS_MAX_TOKENS', '1536'))

WHISPER_CONTEXT_PROMPT: str = (
    'This is a voice command for InkOS. Transcribe English and Arabic exactly. '
    'Maintain casing for: InkOS, CIPHER, A.I.Z.E.N., Tech-Noir, Obsidian.'
)
