import os
import json
import base64
import time
import re
import shutil
import subprocess
import httpx
from pathlib import Path
from typing import Dict, List, Optional, Any

# Base directory paths
APP_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = APP_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
HISTORY_FILE = OUTPUT_DIR / "history.json"


def load_dotenv():
    """Lightweight zero-dependency .env parser for out-of-the-box local setup."""
    env_paths = [APP_DIR / ".env", Path.cwd() / ".env"]
    for env_file in env_paths:
        if env_file.exists():
            try:
                with open(env_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, val = line.split("=", 1)
                            key = key.strip()
                            val = val.strip().strip("'\"")
                            if key and key not in os.environ:
                                os.environ[key] = val
                break
            except Exception:
                pass


load_dotenv()


def build_clean_filename(voice: str, text: str, ext: str = "wav", timestamp: Optional[str] = None) -> str:
    """Build standardized audio filename: {YYYYMMDD_HHMMSS}_{Voice}_{CleanSnippet}.{ext}.
    Date-first ordering, emotion tags stripped, CJK & alphanumeric preserved.
    """
    ts = timestamp or time.strftime("%Y%m%d_%H%M%S")
    # Remove emotion/gesture tags like <laugh>, <sigh>, <whisper>
    clean_text = re.sub(r"<[^>]+>", "", text).strip()
    # Retain alphanumeric & CJK characters, strip special punctuation
    clean_chars = "".join(c for c in clean_text if c.isalnum() or c in ("-", "_")).strip()
    snippet = clean_chars[:12].strip() or "Speech"
    return f"{ts}_{voice}_{snippet}.{ext.lstrip('.')}"


def convert_wav_to_mp3(wav_path: Path) -> Path:
    """Transcode WAV file to 192kbps MP3 with caching."""
    wav_path = Path(wav_path)
    mp3_path = wav_path.with_suffix(".mp3")
    if mp3_path.exists() and mp3_path.stat().st_size > 0:
        return mp3_path

    ffmpeg_bin = shutil.which("ffmpeg") or shutil.which("ffmpeg.exe")
    if not ffmpeg_bin:
        for candidate in [
            Path.home() / ".local" / "bin" / "ffmpeg",
            Path("/opt/homebrew/bin/ffmpeg"),
            Path("/usr/local/bin/ffmpeg"),
        ]:
            if candidate.exists():
                ffmpeg_bin = str(candidate)
                break

    if not ffmpeg_bin:
        hint = "On Windows run: winget install Gyan.FFmpeg; on macOS run: brew install ffmpeg; on Linux run: sudo apt install ffmpeg"
        raise RuntimeError(f"FFmpeg not found. Cannot transcode audio to MP3. {hint}")

    try:
        subprocess.run(
            [str(ffmpeg_bin), "-y", "-i", str(wav_path), "-b:a", "192k", str(mp3_path)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    except Exception as e:
        raise RuntimeError(f"FFmpeg MP3 transcoding failed: {e}")

    return mp3_path

# Supported preset voices
PRESET_VOICES = [
    {
        "id": "Puck",
        "name": "Puck",
        "gender": "男声",
        "gender_en": "Male",
        "tags": ["活泼亲切", "清脆自然", "日常通用"],
        "tags_en": ["Lively & Relatable", "Crisp & Natural", "General Purpose"],
        "description": "声音清脆利落，富有表现力，适合播报、解说和日常互动。",
        "description_en": "Crisp and lively with expressive clarity. Great for commentary, vlogs, and daily dialogue."
    },
    {
        "id": "Aoede",
        "name": "Aoede",
        "gender": "女声",
        "gender_en": "Female",
        "tags": ["温暖典雅", "富有感染力", "情感充沛"],
        "tags_en": ["Warm & Elegant", "Deeply Expressive", "Emotional"],
        "description": "语调温柔有张力，适合散文诗歌、抒情独白与故事讲述。",
        "description_en": "Warm, elegant, and resonant. Perfect for prose, lyrical monologues, and storytelling."
    },
    {
        "id": "Charon",
        "name": "Charon",
        "gender": "男声",
        "gender_en": "Male",
        "tags": ["低沉磁性", "成熟稳重", "纪录片风"],
        "tags_en": ["Deep & Magnetic", "Cinematic", "Gravelly"],
        "description": "厚重低沉的电影感嗓音，适合悬疑、史诗叙事与旁白。",
        "description_en": "Deep, magnetic, cinematic voice. Ideal for epic narratives, suspense, and documentaries."
    },
    {
        "id": "Kore",
        "name": "Kore",
        "gender": "女声",
        "gender_en": "Female",
        "tags": ["柔和平静", "治愈舒缓", "睡前读物"],
        "tags_en": ["Gentle & Soothing", "Healing", "Bedtime Stories"],
        "description": "轻柔放松的治愈嗓音，适合助眠故事、冥想引导与睡前朗读。",
        "description_en": "Soft, relaxing, and therapeutic. Excellent for meditation guidance and bedtime reading."
    },
    {
        "id": "Fenrir",
        "name": "Fenrir",
        "gender": "男声",
        "gender_en": "Male",
        "tags": ["威严有力", "坚定深沉", "新闻播报"],
        "tags_en": ["Authoritative", "Commanding & Deep", "News Broadcast"],
        "description": "铿锵有力、清晰果断，适合权威发布、正剧演播与商务解说。",
        "description_en": "Authoritative, decisive, and commanding. Ideal for formal news, briefings, and presentations."
    },
    {
        "id": "Veda",
        "name": "Veda",
        "gender": "女声",
        "gender_en": "Female",
        "tags": ["知性从容", "专业清晰", "知识科普"],
        "tags_en": ["Intellectual", "Articulate & Clear", "Educational"],
        "description": "条理清晰、发音标准的知性声音，适合学术讲座与科普教程。",
        "description_en": "Clear, articulate, and intellectual. Perfect for lectures, explainers, and audio courses."
    },
    {
        "id": "Zephyr",
        "name": "Zephyr",
        "gender": "男声",
        "gender_en": "Male",
        "tags": ["轻快阳光", "朝气蓬勃", "年轻活力"],
        "tags_en": ["Bright & Sunny", "Youthful", "Energetic"],
        "description": "充满活力的青年音色，适合短视频解说、动漫与游戏角色。",
        "description_en": "Upbeat, youthful, and energetic. Tailored for gaming, animation, and short video clips."
    },
    {
        "id": "Leda",
        "name": "Leda",
        "gender": "女声",
        "gender_en": "Female",
        "tags": ["优雅端庄", "娓娓道来", "有声书"],
        "tags_en": ["Graceful", "Narrative Cadence", "Audiobooks"],
        "description": "优雅沉静，节奏张弛有度，非常适合长篇小说与人物传记。",
        "description_en": "Composed, graceful, with measured pacing. Built for literary novels and biographies."
    }
]

SUPPORTED_MODELS = [
    {
        "id": "gemini-3.8-flash-tts",
        "name": "Gemini 3.8 Flash TTS",
        "tag": "Studio 高保真（推荐）",
        "tag_en": "Studio Hi-Fi (Recommended)",
        "description": "最高声学质量与细腻演技，支持长文本与微表情语气",
        "description_en": "Peak acoustic fidelity & subtle acting. Supports micro-expression tags and style prompts."
    },
    {
        "id": "gemini-3.8-flash-lite-tts",
        "name": "Gemini 3.8 Flash-Lite TTS",
        "tag": "超低延迟 & 高效",
        "tag_en": "Ultra-Low Latency & Fast",
        "description": "响应极快，高吞吐量，适合短句快速即时朗读",
        "description_en": "Instant response with high throughput. Perfect for snappy short-form speech."
    }
]


class GeminiTTSClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "")

    def get_api_key(self, override_key: Optional[str] = None) -> str:
        key = (override_key or "").strip() or self.api_key or os.environ.get("GEMINI_API_KEY", "").strip()
        if not key:
            raise ValueError("Missing Gemini API Key. Please enter it in the settings modal or set GEMINI_API_KEY environment variable.")
        return key

    def load_history(self) -> List[Dict[str, Any]]:
        """Load recording history from file."""
        if not HISTORY_FILE.exists():
            return []
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def save_history_item(self, item: Dict[str, Any]) -> None:
        """Append an audio item to history."""
        history = self.load_history()
        history.insert(0, item)
        # Retain up to 100 recent takes
        history = history[:100]
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save history: {e}")

    def clear_history(self) -> None:
        """Clear recording history."""
        try:
            if HISTORY_FILE.exists():
                with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                    json.dump([], f)
        except Exception as e:
            print(f"Warning: Failed to clear history: {e}")

    async def generate_speech(
        self,
        text: str,
        voice: str = "Puck",
        model: str = "gemini-3.8-flash-tts",
        style_prompt: Optional[str] = None,
        custom_api_key: Optional[str] = None,
        output_filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """Asynchronously call Gemini TTS API and save synthesized audio."""
        api_key = self.get_api_key(custom_api_key)
        clean_text = text.strip()
        if not clean_text:
            raise ValueError("Input text cannot be empty")

        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        params = {"key": api_key}

        payload: Dict[str, Any] = {
            "contents": [
                {
                    "parts": [
                        {"text": clean_text}
                    ]
                }
            ],
            "generationConfig": {
                "responseModalities": ["AUDIO"],
                "speechConfig": {
                    "voiceConfig": {
                        "prebuiltVoiceConfig": {
                            "voiceName": voice
                        }
                    }
                }
            }
        }

        # Add delivery instruction if specified
        if style_prompt and style_prompt.strip():
            payload["systemInstruction"] = {
                "parts": [
                    {"text": f"Instruction for speech delivery: {style_prompt.strip()}"}
                ]
            }

        headers = {"Content-Type": "application/json"}

        # Dispatch synthesis request
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(endpoint, params=params, json=payload, headers=headers)

        if resp.status_code != 200:
            err_msg = f"Gemini API error (status {resp.status_code})"
            try:
                err_data = resp.json()
                if "error" in err_data and "message" in err_data["error"]:
                    err_msg += f": {err_data['error']['message']}"
            except Exception:
                err_msg += f": {resp.text}"
            raise RuntimeError(err_msg)

        data = resp.json()

        # Parse audio stream payload
        try:
            candidates = data.get("candidates", [])
            if not candidates:
                feedback = data.get("promptFeedback", {})
                raise RuntimeError(f"Model returned no audio candidates: {feedback}")

            parts = candidates[0].get("content", {}).get("parts", [])
            audio_base64 = None
            mime_type = "audio/wav"

            for part in parts:
                if "inlineData" in part:
                    audio_base64 = part["inlineData"].get("data")
                    mime_type = part["inlineData"].get("mimeType", "audio/wav")
                    break

            if not audio_base64:
                raise RuntimeError("No inlineData audio stream found in API response")

            audio_bytes = base64.b64decode(audio_base64)
        except Exception as e:
            raise RuntimeError(f"Failed to parse audio response: {str(e)}")

        # Save audio to disk (date-first naming, tags stripped)
        timestamp_str = time.strftime("%Y%m%d_%H%M%S")
        if not output_filename:
            filename = build_clean_filename(voice=voice, text=clean_text, ext="wav", timestamp=timestamp_str)
        else:
            filename = output_filename if output_filename.endswith(".wav") else f"{output_filename}.wav"

        out_path = OUTPUT_DIR / filename
        with open(out_path, "wb") as f:
            f.write(audio_bytes)

        size_kb = round(len(audio_bytes) / 1024, 1)

        # Pre-transcode MP3 version for universal compatibility
        mp3_filename = Path(filename).with_suffix(".mp3").name
        mp3_size_kb = 0.0
        try:
            mp3_path = convert_wav_to_mp3(out_path)
            if mp3_path.exists():
                mp3_size_kb = round(mp3_path.stat().st_size / 1024, 1)
        except Exception as e:
            print(f"Warning: MP3 pre-transcode failed: {e}")

        duration_sec = 0.0
        try:
            import wave
            with wave.open(str(out_path), "rb") as wf:
                frames = wf.getnframes()
                rate = wf.getframerate()
                if rate > 0:
                    duration_sec = round(frames / float(rate), 1)
        except Exception:
            duration_sec = round(len(clean_text) / 4.0, 1)

        result_item = {
            "filename": filename,
            "url": f"/audio/{filename}",
            "mp3_filename": mp3_filename,
            "mp3_url": f"/audio/{mp3_filename}",
            "text": clean_text,
            "voice": voice,
            "model": model,
            "style_prompt": style_prompt or "",
            "size_kb": size_kb,
            "mp3_size_kb": mp3_size_kb or round(size_kb * 0.25, 1),
            "duration_sec": duration_sec,
            "mime_type": mime_type,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        self.save_history_item(result_item)
        return result_item

    def generate_speech_sync(
        self,
        text: str,
        voice: str = "Puck",
        model: str = "gemini-3.8-flash-tts",
        style_prompt: Optional[str] = None,
        custom_api_key: Optional[str] = None,
        output_filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """Synchronous helper for CLI execution."""
        import asyncio
        return asyncio.run(
            self.generate_speech(
                text=text,
                voice=voice,
                model=model,
                style_prompt=style_prompt,
                custom_api_key=custom_api_key,
                output_filename=output_filename
            )
        )
