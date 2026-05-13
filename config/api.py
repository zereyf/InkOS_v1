import os
from typing import Optional

from dotenv import load_dotenv
from groq import Groq

load_dotenv(override=True)


def _env_float(name: str, default: float, *, minimum: float | None = None, maximum: float | None = None) -> float:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        value = float(raw)
    except ValueError:
        return default
    if minimum is not None:
        value = max(minimum, value)
    if maximum is not None:
        value = min(maximum, value)
    return value


def _env_int(name: str, default: int, *, minimum: int | None = None, maximum: int | None = None) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        value = int(raw)
    except ValueError:
        return default
    if minimum is not None:
        value = max(minimum, value)
    if maximum is not None:
        value = min(maximum, value)
    return value


_api_key: str = os.getenv("GROQ_API_KEY", "").strip()
API_KEY_MISSING: bool = not bool(_api_key)
client: Optional[Groq] = Groq(api_key=_api_key) if _api_key else None

# ── MODEL CONFIGURATION (LAUNCH TIER - 8B INSTANT) ───────────────────────────
PRIMARY_MODEL_ID: str = os.getenv("INKOS_PRIMARY_MODEL_ID", "llama3-8b-8192").strip() or "llama3-8b-8192"
FALLBACK_MODEL_ID: str = os.getenv("INKOS_FALLBACK_MODEL_ID", "mixtral-8x7b-32768").strip() or "mixtral-8x7b-32768"
MODEL_ID: str = os.getenv("INKOS_MODEL_ID", PRIMARY_MODEL_ID).strip() or PRIMARY_MODEL_ID
AUDIO_MODEL_ID: str = os.getenv("INKOS_AUDIO_MODEL", "whisper-large-v3-turbo").strip() or "whisper-large-v3-turbo"
TEMPERATURE: float = _env_float("INKOS_TEMPERATURE", 0.7, minimum=0.0, maximum=2.0)
MAX_TOKENS: int = _env_int("INKOS_MAX_TOKENS", 4096, minimum=256, maximum=32768)

WHISPER_CONTEXT_PROMPT: str = (
    "This is a voice command for InkOS. Transcribe English and Arabic exactly. "
    "Maintain casing for: InkOS, CIPHER, A.I.Z.E.N., Tech-Noir, Obsidian."
)


MODEL_PRIORITY: tuple[str, ...] = (PRIMARY_MODEL_ID, FALLBACK_MODEL_ID)

REQUEST_TIMEOUT_SECONDS: int = _env_int("INKOS_REQUEST_TIMEOUT", 30, minimum=5, maximum=60)
