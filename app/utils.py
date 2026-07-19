# utils.py

from fastapi import Request, HTTPException
from functools import wraps
import os
from dotenv import load_dotenv

from config import DEFAULT_CONFIGS

load_dotenv()


def getenv_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).lower() in ("yes", "y", "true", "1", "t")


API_KEY = os.getenv('API_KEY', DEFAULT_CONFIGS["API_KEY"])
REQUIRE_API_KEY = getenv_bool('REQUIRE_API_KEY', DEFAULT_CONFIGS["REQUIRE_API_KEY"])
DETAILED_ERROR_LOGGING = getenv_bool('DETAILED_ERROR_LOGGING', DEFAULT_CONFIGS["DETAILED_ERROR_LOGGING"])


async def require_api_key(request: Request):
    if not REQUIRE_API_KEY:
        return

    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        raise HTTPException(status_code=401, detail={"error": "Missing or invalid API key"})
    token = auth_header.split('Bearer ', 1)[1]
    if token != API_KEY:
        raise HTTPException(status_code=401, detail={"error": "Invalid API key"})


AUDIO_FORMAT_MIME_TYPES = {
    "mp3": "audio/mpeg",
    "opus": "audio/ogg",
    "aac": "audio/aac",
    "flac": "audio/flac",
    "wav": "audio/wav",
    "pcm": "audio/L16",
}
