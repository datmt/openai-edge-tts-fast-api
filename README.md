# openai-edge-tts

A free, OpenAI-compatible text-to-speech API backed by Microsoft Edge Neural TTS. Drop-in replacement for applications using OpenAI's TTS endpoint.

**[Website & Documentation](https://datmt.com)**

## Features

- **OpenAI Compatible API** — Works with any client that supports OpenAI's `/v1/audio/speech` endpoint
- **Free Azure Neural TTS** — Powered by Microsoft Edge's `edge-tts` library, no API keys or credits needed
- **11 Vocal Presets** — alloy, ash, ballad, coral, echo, fable, nova, onyx, sage, shimmer, verse
- **6 Audio Formats** — mp3, opus, aac, flac, wav, pcm
- **SSE Streaming** — Real-time audio streaming via Server-Sent Events
- **Speed Control** — Adjust playback speed from 0.5x to 2.0x
- **Expanded API Support** — ElevenLabs and Azure Cognitive Services compatible endpoints
- **Text Preprocessing** — Automatic markdown, emoji, and HTML cleanup for natural-sounding output
- **Voice Listing** — Query available voices by language/locale

## Quick Start

### Docker

```bash
docker run -d \
  -p 5050:5050 \
  -e DEFAULT_VOICE=en-US-AriaNeural \
  -e DEFAULT_RESPONSE_FORMAT=mp3 \
  -e DEFAULT_SPEED=1.0 \
  --name openai-edge-tts \
  datmt/openai-edge-tts
```

### Install FFmpeg (optional, for non-mp3 formats)

```bash
docker run -d \
  -p 5050:5050 \
  -e INSTALL_FFMPEG_ARG=true \
  --name openai-edge-tts \
  datmt/openai-edge-tts
```

### Docker Compose

```yaml
services:
  tts:
    image: datmt/openai-edge-tts
    container_name: openai-edge-tts
    restart: unless-stopped
    ports:
      - "5050:5050"
    environment:
      DEFAULT_VOICE: en-US-AriaNeural
      DEFAULT_RESPONSE_FORMAT: mp3
      DEFAULT_SPEED: 1.0
```

## API Reference

### Generate Speech

```
POST /v1/audio/speech
```

Generate audio from text. Accepts JSON body.

**Request Body:**

```json
{
  "model": "tts-1",
  "input": "Hello, world!",
  "voice": "nova",
  "response_format": "mp3",
  "speed": 1.0
}
```

| Parameter           | Type   | Default            | Description                          |
|---------------------|--------|--------------------|--------------------------------------|
| `model`             | string | `tts-1`            | TTS model name                       |
| `input`             | string | **(required)**     | Text to synthesize                   |
| `voice`             | string | `en-US-AvaNeural`  | Voice ID or Azure Neural Voice name  |
| `response_format`   | string | `mp3`              | Output audio format                  |
| `speed`             | number | `1.0`              | Playback speed (0.5 – 2.0)           |

**Available Voices (Preset IDs):**

| Preset ID  | Azure Neural Voice       | Language              |
|------------|--------------------------|-----------------------|
| `alloy`    | en-US-JennyNeural        | English (US, Female)  |
| `ash`      | en-US-AndrewNeural       | English (US, Male)    |
| `ballad`   | en-GB-ThomasNeural       | English (GB, Male)    |
| `coral`    | en-AU-NatashaNeural      | English (AU, Female)  |
| `echo`     | en-US-GuyNeural          | English (US, Male)    |
| `fable`    | en-GB-SoniaNeural        | English (GB, Female)  |
| `nova`     | en-US-AriaNeural         | English (US, Female)  |
| `onyx`     | en-US-EricNeural         | English (US, Male)    |
| `sage`     | en-US-JennyNeural        | English (US, Female)  |
| `shimmer`  | en-US-EmmaNeural         | English (US, Female)  |
| `verse`    | en-US-BrianNeural        | English (US, Male)    |

Or use any Azure Neural Voice name directly (e.g. `zh-CN-XiaoxiaoNeural`).

**Response:** Binary audio file with `Content-Type` matching the requested format.

**cURL Example:**

```bash
curl -X POST http://localhost:5050/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello, world!", "voice": "nova", "response_format": "mp3"}' \
  --output speech.mp3
```

**OpenAI Python Client Example:**

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:5050/v1",
    api_key="fake-key"
)

response = client.audio.speech.create(
    model="tts-1",
    voice="nova",
    input="Hello, world!",
    response_format="mp3",
    speed=1.0
)

response.stream_to_file("output.mp3")
```

### SSE Streaming

Add `"stream_format": "sse"` to request body for real-time streaming:

```bash
curl -X POST http://localhost:5050/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello, world!", "voice": "nova", "stream_format": "sse"}'
```

Response format (SSE events):

```json
{"type": "speech.audio.delta", "audio": "base64EncodedChunk"}
{"type": "speech.audio.delta", "audio": "base64EncodedChunk"}
{"type": "speech.audio.done", "usage": {"input_tokens": 3}}
```

### List Available Models

```
GET /v1/models
```

**Response:**

```json
{
  "models": [
    {"id": "tts-1", "name": "Text-to-speech v1"},
    {"id": "tts-1-hd", "name": "Text-to-speech v1 HD"},
    {"id": "gpt-4o-mini-tts", "name": "GPT-4o mini TTS"}
  ]
}
```

### List Voices

```
GET /v1/voices
GET /v1/voices/all
```

Returns available voices filtered by optional `?language=en-US` query parameter.

## Expanded API Endpoints

Compatible with third-party client integrations. Requires `EXPAND_API=True`.

| Endpoint                                    | Method | Description                              |
|---------------------------------------------|--------|------------------------------------------|
| `/elevenlabs/v1/text-to-speech/{voice_id}` | POST   | ElevenLabs-style TTS (expects `text` field) |
| `/azure/cognitiveservices/v1`             | POST   | Azure SSML-style TTS (expects SSML body) |
| `/v1/audio/speech`, `/audio/speech`       | POST   | OpenAI-compatible speech generation      |

## Environment Variables

| Variable                 | Type   | Default             | Description                           |
|--------------------------|--------|---------------------|---------------------------------------|
| `PORT`                   | int    | `5050`              | Server port                           |
| `HOST`                   | string | `0.0.0.0`          | Bind address                          |
| `DEFAULT_VOICE`          | string | `en-US-AvaNeural`  | Default voice                         |
| `DEFAULT_RESPONSE_FORMAT`| string | `mp3`              | Output audio format                   |
| `DEFAULT_SPEED`          | float  | `1.0`              | Playback speed                        |
| `DEFAULT_LANGUAGE`       | string | `en-US`            | Default language for voice listing    |
| `REQUIRE_API_KEY`        | bool   | `False`            | Require `X-API-Key` header            |
| `REMOVE_FILTER`          | bool   | `False`            | Skip markdown/emoji text preprocessing|
| `EXPAND_API`             | bool   | `True`             | Enable ElevenLabs & Azure endpoints   |
| `DETAILED_ERROR_LOGGING` | bool   | `True`             | Verbose error output in logs          |

## License

[Add your license here]

---

Built with [edge-tts](https://github.com/donno2048/edge-tts), [FastAPI](https://fastapi.tiangolo.com/), and ❤️.

[Website & Documentation](https://datmt.com)
