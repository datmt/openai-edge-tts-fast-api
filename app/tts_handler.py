# tts_handler.py

import edge_tts
import asyncio
import tempfile
import subprocess
import os
from pathlib import Path

from utils import DETAILED_ERROR_LOGGING
from config import DEFAULT_CONFIGS

DEFAULT_LANGUAGE = os.getenv('DEFAULT_LANGUAGE', DEFAULT_CONFIGS["DEFAULT_LANGUAGE"])

voice_mapping = {
    'alloy': 'en-US-JennyNeural',
    'ash': 'en-US-AndrewNeural',
    'ballad': 'en-GB-ThomasNeural',
    'coral': 'en-AU-NatashaNeural',
    'echo': 'en-US-GuyNeural',
    'fable': 'en-GB-SoniaNeural',
    'nova': 'en-US-AriaNeural',
    'onyx': 'en-US-EricNeural',
    'sage': 'en-US-JennyNeural',
    'shimmer': 'en-US-EmmaNeural',
    'verse': 'en-US-BrianNeural',
}

model_data = [
    {"id": "tts-1", "name": "Text-to-speech v1"},
    {"id": "tts-1-hd", "name": "Text-to-speech v1 HD"},
    {"id": "gpt-4o-mini-tts", "name": "GPT-4o mini TTS"},
]


def is_ffmpeg_installed():
    try:
        subprocess.run(['ffmpeg', '-version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


async def generate_speech_stream(text, voice, speed=1.0):
    """Async generator that yields audio chunks."""
    edge_tts_voice = voice_mapping.get(voice, voice)

    try:
        speed_rate = speed_to_rate(speed)
    except Exception as e:
        print(f"Error converting speed: {e}. Defaulting to +0%.")
        speed_rate = "+0%"

    communicator = edge_tts.Communicate(text=text, voice=edge_tts_voice, rate=speed_rate)

    async for chunk in communicator.stream():
        if chunk["type"] == "audio":
            yield chunk["data"]


async def generate_speech_async(text, voice, response_format, speed=1.0):
    """Async version of generate_speech. Returns the path of the generated audio file."""
    edge_tts_voice = voice_mapping.get(voice, voice)

    temp_mp3_file_obj = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    temp_mp3_path = temp_mp3_file_obj.name
    temp_mp3_file_obj.close()

    try:
        try:
            speed_rate = speed_to_rate(speed)
        except Exception as e:
            print(f"Error converting speed: {e}. Defaulting to +0%.")
            speed_rate = "+0%"

        communicator = edge_tts.Communicate(text=text, voice=edge_tts_voice, rate=speed_rate)
        await communicator.save(temp_mp3_path)

    except Exception:
        Path(temp_mp3_path).unlink(missing_ok=True)
        raise

    if response_format == "mp3":
        return temp_mp3_path

    if not is_ffmpeg_installed():
        print("FFmpeg is not available. Returning unmodified mp3 file.")
        return temp_mp3_path

    converted_file_obj = tempfile.NamedTemporaryFile(delete=False, suffix=f".{response_format}")
    converted_path = converted_file_obj.name
    converted_file_obj.close()

    ffmpeg_command = [
        "ffmpeg",
        "-i", temp_mp3_path,
        "-c:a", {
            "aac": "aac",
            "mp3": "libmp3lame",
            "wav": "pcm_s16le",
            "opus": "libopus",
            "flac": "flac",
        }.get(response_format, "aac"),
    ]

    if response_format != "wav":
        ffmpeg_command.extend(["-b:a", "192k"])

    ffmpeg_command.extend([
        "-f", {
            "aac": "mp4",
            "mp3": "mp3",
            "wav": "wav",
            "opus": "ogg",
            "flac": "flac",
        }.get(response_format, response_format),
        "-y",
        converted_path,
    ])

    try:
        proc = await asyncio.create_subprocess_exec(
            *ffmpeg_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise subprocess.CalledProcessError(proc.returncode, ffmpeg_command, stderr)
    except subprocess.CalledProcessError as e:
        Path(converted_path).unlink(missing_ok=True)
        Path(temp_mp3_path).unlink(missing_ok=True)

        if DETAILED_ERROR_LOGGING:
            error_message = f"FFmpeg error during audio conversion. Command: '{' '.join(e.cmd)}'. Stderr: {e.stderr.decode('utf-8', 'ignore')}"
            print(error_message)
        else:
            error_message = f"FFmpeg error during audio conversion: {e}"
            print(error_message)
        raise RuntimeError(f"FFmpeg error during audio conversion: {e}")

    Path(temp_mp3_path).unlink(missing_ok=True)
    return converted_path


def get_models():
    return model_data


def get_models_formatted():
    return [{"id": x["id"]} for x in model_data]


def get_voices_formatted():
    return [{"id": k, "name": v} for k, v in voice_mapping.items()]


async def get_voices_async(language=None):
    all_voices = await edge_tts.list_voices()
    language = language or DEFAULT_LANGUAGE
    filtered_voices = [
        {"name": v['ShortName'], "gender": v['Gender'], "language": v['Locale']}
        for v in all_voices if language == 'all' or language is None or v['Locale'] == language
    ]
    return filtered_voices


def speed_to_rate(speed: float) -> str:
    if speed < 0 or speed > 2:
        raise ValueError("Speed must be between 0 and 2 (inclusive).")
    percentage_change = (speed - 1) * 100
    return f"{percentage_change:+.0f}%"
