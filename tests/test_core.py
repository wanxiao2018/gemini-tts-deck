import tempfile
from pathlib import Path
from fastapi.testclient import TestClient

from core import build_clean_filename, convert_wav_to_mp3, PRESET_VOICES, SUPPORTED_MODELS
from app import app


def test_build_clean_filename():
    # 1. Normal text with timestamp (truncated to 12 chars snippet)
    fname = build_clean_filename(voice="Puck", text="你好世界，这是一个测试文本", ext="wav", timestamp="20260930_120000")
    assert fname == "20260930_120000_Puck_你好世界这是一个测试文本.wav"

    # 2. Removes emotion tags like <laugh>, <sigh>, <whisper>
    fname_tags = build_clean_filename(voice="Aoede", text="<laugh>哈哈哈哈<sigh>真好听", ext=".mp3", timestamp="20260930_120000")
    assert fname_tags == "20260930_120000_Aoede_哈哈哈哈真好听.mp3"
    assert "<" not in fname_tags
    assert ">" not in fname_tags

    # 3. Filters special symbols and emojis
    fname_special = build_clean_filename(voice="Charon", text="🎙️Hello @World! #123???", ext="wav", timestamp="20260930_120000")
    assert fname_special == "20260930_120000_Charon_HelloWorld12.wav"

    # 4. Fallback when text has only punctuation
    fname_empty = build_clean_filename(voice="Fenrir", text="......？？！！", ext="wav", timestamp="20260930_120000")
    assert fname_empty == "20260930_120000_Fenrir_Speech.wav"


def test_preset_voices_integrity():
    assert len(PRESET_VOICES) >= 8

    ids = set()
    for v in PRESET_VOICES:
        assert "id" in v and v["id"]
        assert "name" in v and v["name"]
        assert "gender" in v and v["gender"] in ("女声", "男声", "中性")
        assert "gender_en" in v and v["gender_en"] in ("Male", "Female", "Neutral")
        assert "tags" in v and isinstance(v["tags"], list) and len(v["tags"]) > 0
        assert "tags_en" in v and isinstance(v["tags_en"], list) and len(v["tags_en"]) > 0
        assert "description" in v and v["description"]
        assert "description_en" in v and v["description_en"]

        # IDs must be strictly unique
        assert v["id"] not in ids
        ids.add(v["id"])

    # Core flagship voices must be present
    for core_voice in ["Puck", "Charon", "Aoede", "Kore", "Fenrir"]:
        assert core_voice in ids


def test_models_integrity():
    assert len(SUPPORTED_MODELS) >= 2
    for m in SUPPORTED_MODELS:
        assert "id" in m and m["id"]
        assert "name" in m and m["name"]
        assert "tag" in m and m["tag"]
        assert "tag_en" in m and m["tag_en"]
        assert "description" in m and m["description"]
        assert "description_en" in m and m["description_en"]


def test_convert_wav_to_mp3_cache():
    # If the mp3 file already exists and is non-empty, convert_wav_to_mp3 must return it directly
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        wav_file = tmp_path / "test.wav"
        mp3_file = tmp_path / "test.mp3"

        wav_file.write_bytes(b"dummy wav data")
        mp3_file.write_bytes(b"cached mp3 data")

        result = convert_wav_to_mp3(wav_file)
        assert result == mp3_file
        assert result.read_bytes() == b"cached mp3 data"


def test_api_routes():
    client = TestClient(app)

    # 1. Root page loads index.html
    res = client.get("/")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert "Gemini TTS" in res.text

    # 2. Config API returns voice list and models
    res = client.get("/api/config")
    assert res.status_code == 200
    data = res.json()
    assert "voices" in data
    assert len(data["voices"]) >= 8
    assert "models" in data
    assert any(m["id"] == "gemini-3.8-flash-tts" for m in data["models"])
    assert data["default_voice"] == "Puck"

    # 3. History API returns list
    res = client.get("/api/history")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

    # 4. Post TTS with empty text returns 422 Unprocessable Entity
    res = client.post("/api/tts", json={"text": ""})
    assert res.status_code == 422

    # 5. Non-existent route returns 404
    res = client.get("/api/non_existent_route")
    assert res.status_code == 404
