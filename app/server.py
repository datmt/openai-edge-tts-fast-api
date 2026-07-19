# server.py

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response, StreamingResponse
from dotenv import load_dotenv
import os
import json
import base64

from config import DEFAULT_CONFIGS
from handle_text import prepare_tts_input_with_context
from tts_handler import generate_speech, generate_speech_stream, get_models_formatted, get_voices, get_voices_formatted
from utils import AUDIO_FORMAT_MIME_TYPES, DETAILED_ERROR_LOGGING, getenv_bool
from models import SpeechRequest, ModelListResponse, VoiceListResponse, VoiceDetailListResponse

app = FastAPI(title="Edge TTS - OpenAI Compatible API", openapi_url="/openapi.json", docs_url="/docs")
load_dotenv()

API_KEY = os.getenv('API_KEY', DEFAULT_CONFIGS["API_KEY"])
PORT = int(os.getenv('PORT', str(DEFAULT_CONFIGS["PORT"])))
HOST = os.getenv('HOST', DEFAULT_CONFIGS["HOST"])

DEFAULT_VOICE = os.getenv('DEFAULT_VOICE', DEFAULT_CONFIGS["DEFAULT_VOICE"])
DEFAULT_RESPONSE_FORMAT = os.getenv('DEFAULT_RESPONSE_FORMAT', DEFAULT_CONFIGS["DEFAULT_RESPONSE_FORMAT"])
DEFAULT_SPEED = float(os.getenv('DEFAULT_SPEED', str(DEFAULT_CONFIGS["DEFAULT_SPEED"])))


async def generate_sse_audio_stream(text, voice, speed):
    """Async generator function for SSE streaming with JSON events."""
    try:
        for chunk in generate_speech_stream(text, voice, speed):
            encoded_audio = base64.b64encode(chunk).decode('utf-8')
            event_data = {
                "type": "speech.audio.delta",
                "audio": encoded_audio,
            }
            yield f"data: {json.dumps(event_data)}\n\n"

        completion_event = {
            "type": "speech.audio.done",
            "usage": {
                "input_tokens": len(text.split()),
                "output_tokens": 0,
                "total_tokens": len(text.split()),
            },
        }
        yield f"data: {json.dumps(completion_event)}\n\n"

    except Exception as e:
        print(f"Error during SSE streaming: {e}")
        error_event = {"type": "error", "error": str(e)}
        yield f"data: {json.dumps(error_event)}\n\n"


# === /v1/audio/speech ===
@app.post('/v1/audio/speech')
async def text_to_speech_v1(request: Request, body: SpeechRequest):
    text = body.input

    if not REMOVE_FILTER:
        text = prepare_tts_input_with_context(text)

    voice = body.voice or DEFAULT_VOICE
    response_format = body.response_format or DEFAULT_RESPONSE_FORMAT
    speed = body.speed or DEFAULT_SPEED
    stream_format = body.stream_format or 'audio'

    mime_type = AUDIO_FORMAT_MIME_TYPES.get(response_format, "audio/mpeg")

    if stream_format == 'sse':
        return StreamingResponse(
            generate_sse_audio_stream(text, voice, speed),
            media_type='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no',
            },
        )
    else:
        output_file_path = generate_speech(text, voice, response_format, speed)

        with open(output_file_path, 'rb') as audio_file:
            audio_data = audio_file.read()

        try:
            os.unlink(output_file_path)
        except OSError:
            pass

        return Response(
            content=audio_data,
            media_type=mime_type,
            headers={'Content-Length': str(len(audio_data))},
        )


@app.post('/audio/speech')
async def text_to_speech(request: Request, body: SpeechRequest):
    text = body.input

    if not REMOVE_FILTER:
        text = prepare_tts_input_with_context(text)

    voice = body.voice or DEFAULT_VOICE
    response_format = body.response_format or DEFAULT_RESPONSE_FORMAT
    speed = body.speed or DEFAULT_SPEED
    stream_format = body.stream_format or 'audio'

    mime_type = AUDIO_FORMAT_MIME_TYPES.get(response_format, "audio/mpeg")

    if stream_format == 'sse':
        return StreamingResponse(
            generate_sse_audio_stream(text, voice, speed),
            media_type='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no',
            },
        )
    else:
        output_file_path = generate_speech(text, voice, response_format, speed)

        with open(output_file_path, 'rb') as audio_file:
            audio_data = audio_file.read()

        try:
            os.unlink(output_file_path)
        except OSError:
            pass

        return Response(
            content=audio_data,
            media_type=mime_type,
            headers={'Content-Length': str(len(audio_data))},
        )


# === /models ===
@app.get('/v1/models')
async def list_models_v1():
    return {"models": get_models_formatted()}


@app.post('/v1/models')
async def list_models_v2():
    return {"models": get_models_formatted()}


@app.get('/models')
async def list_models_v3():
    return {"models": get_models_formatted()}


@app.post('/models')
async def list_models_v4():
    return {"models": get_models_formatted()}


@app.get('/v1/audio/models')
async def list_models_v5():
    return {"models": get_models_formatted()}


@app.post('/v1/audio/models')
async def list_models_v6():
    return {"models": get_models_formatted()}


@app.get('/audio/models')
async def list_models_v7():
    return {"models": get_models_formatted()}


@app.post('/audio/models')
async def list_models_v8():
    return {"models": get_models_formatted()}


# === /voices ===
@app.get('/v1/audio/voices')
async def list_voices_formatted_v1():
    return {"voices": get_voices_formatted()}


@app.post('/v1/audio/voices')
async def list_voices_formatted_v2():
    return {"voices": get_voices_formatted()}


@app.get('/audio/voices')
async def list_voices_formatted_v3():
    return {"voices": get_voices_formatted()}


@app.post('/audio/voices')
async def list_voices_formatted_v4():
    return {"voices": get_voices_formatted()}


@app.get('/v1/voices')
async def list_voices(request: Request):
    params = request.query_params
    language = params.get('language') or params.get('locale')
    return {"voices": get_voices(language)}


@app.post('/v1/voices')
async def list_voices_post(request: Request):
    params = request.query_params
    language = params.get('language') or params.get('locale')
    return {"voices": get_voices(language)}


@app.get('/voices')
async def list_voices_v3(request: Request):
    params = request.query_params
    language = params.get('language') or params.get('locale')
    return {"voices": get_voices(language)}


@app.post('/voices')
async def list_voices_v4(request: Request):
    params = request.query_params
    language = params.get('language') or params.get('locale')
    return {"voices": get_voices(language)}


@app.get('/v1/voices/all')
async def list_all_voices_v1(request: Request):
    return {"voices": get_voices('all')}


@app.post('/v1/voices/all')
async def list_all_voices_v2(request: Request):
    return {"voices": get_voices('all')}


@app.get('/voices/all')
async def list_all_voices_v3(request: Request):
    return {"voices": get_voices('all')}


@app.post('/voices/all')
async def list_all_voices_v4(request: Request):
    return {"voices": get_voices('all')}


# === ElevenLabs ===
@app.post('/elevenlabs/v1/text-to-speech/{voice_id}')
async def elevenlabs_tts(voice_id: str, request: Request, body: SpeechRequest):
    if not EXPAND_API:
        raise HTTPException(status_code=500, detail={"error": "Endpoint not allowed"})

    text = body.input

    if not REMOVE_FILTER:
        text = prepare_tts_input_with_context(text)

    try:
        output_file_path = generate_speech(text, voice_id, 'mp3', DEFAULT_SPEED)
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": f"TTS generation failed: {str(e)}"})

    with open(output_file_path, 'rb') as f:
        audio_data = f.read()
    os.unlink(output_file_path)

    return Response(content=audio_data, media_type="audio/mpeg", headers={'Content-Disposition': 'attachment; filename=speech.mp3'})


# === Azure ===
@app.post('/azure/cognitiveservices/v1')
async def azure_tts(request: Request):
    if not EXPAND_API:
        raise HTTPException(status_code=500, detail={"error": "Endpoint not allowed"})

    try:
        ssml_data = await request.text
        if not ssml_data:
            raise HTTPException(status_code=400, detail={"error": "Missing SSML payload"})

        from xml.etree import ElementTree as ET
        root = ET.fromstring(ssml_data)
        text = root.find('.//{http://www.w3.org/2001/10/synthesis}voice').text
        voice = root.find('.//{http://www.w3.org/2001/10/synthesis}voice').get('name')
    except Exception as e:
        raise HTTPException(status_code=400, detail={"error": f"Invalid SSML payload: {str(e)}"})

    if not REMOVE_FILTER:
        text = prepare_tts_input_with_context(text)

    try:
        output_file_path = generate_speech(text, voice, 'mp3', DEFAULT_SPEED)
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": f"TTS generation failed: {str(e)}"})

    with open(output_file_path, 'rb') as f:
        audio_data = f.read()
    os.unlink(output_file_path)

    return Response(content=audio_data, media_type="audio/mpeg", headers={'Content-Disposition': 'attachment; filename=speech.mp3'})


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == '__main__':
    import uvicorn
    print(f" Edge TTS (Free Azure TTS) Replacement for OpenAI's TTS API")
    print(f" ")
    print(f" * Serving OpenAI Edge TTS")
    print(f" * Server running on http://{HOST}:{PORT}")
    print(f" * TTS Endpoint: http://{HOST}:{PORT}/v1/audio/speech")
    print(f" ")
    uvicorn.run(app, host=HOST, port=PORT)
