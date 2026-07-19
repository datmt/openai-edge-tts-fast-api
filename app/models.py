from pydantic import BaseModel
from typing import Optional


class SpeechRequest(BaseModel):
    input: str
    model: Optional[str] = "tts-1"
    voice: Optional[str] = "en-US-AvaNeural"
    response_format: Optional[str] = "mp3"
    speed: Optional[float] = 1.0
    stream_format: Optional[str] = "audio"


class ModelResponse(BaseModel):
    id: str
    name: str


class VoiceResponse(BaseModel):
    id: str


class ModelListResponse(BaseModel):
    models: list[ModelResponse]


class VoiceListResponse(BaseModel):
    voices: list[VoiceResponse]


class VoiceDetail(BaseModel):
    name: str
    gender: str
    language: str


class VoiceDetailListResponse(BaseModel):
    voices: list[VoiceDetail]
