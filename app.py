import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional

from core import (
    GeminiTTSClient,
    PRESET_VOICES,
    SUPPORTED_MODELS,
    OUTPUT_DIR,
    APP_DIR,
    convert_wav_to_mp3
)

app = FastAPI(title="Gemini TTS Deck", version="1.0.0")

# Mount static assets directory
STATIC_DIR = APP_DIR / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

tts_client = GeminiTTSClient()


class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text content to synthesize")
    voice: str = Field(default="Puck", description="Voice preset name")
    model: str = Field(default="gemini-3.8-flash-tts", description="Gemini model ID")
    style_prompt: Optional[str] = Field(default="", description="Speech style and delivery instruction")
    api_key: Optional[str] = Field(default="", description="Optional Gemini API key override")


@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="Frontend page not found")
    with open(index_file, "r", encoding="utf-8") as f:
        return f.read()


@app.get("/api/config")
async def get_config():
    """Get available voices, supported models, and API key configuration status."""
    has_env_key = bool(os.environ.get("GEMINI_API_KEY", "").strip())
    return {
        "voices": PRESET_VOICES,
        "male_voices": [v for v in PRESET_VOICES if v.get("gender_en") == "Male" or v["gender"] == "男声"],
        "female_voices": [v for v in PRESET_VOICES if v.get("gender_en") == "Female" or v["gender"] == "女声"],
        "models": SUPPORTED_MODELS,
        "has_env_key": has_env_key,
        "default_voice": "Puck",
        "default_model": "gemini-3.8-flash-tts"
    }



@app.get("/api/history")
async def get_history():
    """Retrieve historical speech generation records."""
    return tts_client.load_history()


@app.delete("/api/history")
async def clear_history():
    """Clear all recording history records."""
    tts_client.clear_history()
    return {"success": True, "message": "History cleared"}


@app.post("/api/tts")
async def convert_tts(req: TTSRequest):
    """Convert input text to speech using Gemini TTS API."""
    try:
        result = await tts_client.generate_speech(
            text=req.text,
            voice=req.voice,
            model=req.model,
            style_prompt=req.style_prompt,
            custom_api_key=req.api_key
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/audio/{filename}")
async def get_audio_file(filename: str):
    """Serve generated audio files (.wav and .mp3)."""
    safe_name = Path(filename).name
    file_path = OUTPUT_DIR / safe_name

    # If .mp3 is requested and does not exist locally, transcode on-the-fly from .wav
    if safe_name.endswith(".mp3") and (not file_path.exists() or file_path.stat().st_size == 0):
        wav_path = file_path.with_suffix(".wav")
        if wav_path.exists():
            try:
                convert_wav_to_mp3(wav_path)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"MP3 transcoding failed: {e}")
        else:
            raise HTTPException(status_code=404, detail="Audio source file not found")

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")

    media_type = "audio/mpeg" if safe_name.endswith(".mp3") else "audio/wav"
    return FileResponse(
        path=str(file_path),
        media_type=media_type,
        filename=safe_name
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
