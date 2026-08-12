import hashlib
import json
import wave
from pathlib import Path

from src.content.toeic_listening_conversations_talks import (
    get_toeic_listening_conversations_talks_diagnostic,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "src" / "content" / "listening_conversations_talks_assets.json"
STATIC_AUDIO_DIR = PROJECT_ROOT / "public" / "listening"


def test_shared_listening_manifest_matches_original_audio_assets():
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    diagnostic = get_toeic_listening_conversations_talks_diagnostic()

    assert manifest["module"] == diagnostic["id"]
    assert manifest["origin"] == "editorial_original"
    assert len(manifest["items"]) == 4
    assert len(diagnostic["stimuli"]) == 4
    assert len(diagnostic["items"]) == 8

    assets_by_stimulus = {asset["stimulus_id"]: asset for asset in manifest["items"]}
    assert set(assets_by_stimulus) == {stimulus["id"] for stimulus in diagnostic["stimuli"]}

    for stimulus in diagnostic["stimuli"]:
        asset = assets_by_stimulus[stimulus["id"]]
        audio_path = STATIC_AUDIO_DIR / Path(asset["path"]).name
        assert stimulus["audio_status"] == "available"
        assert stimulus["audio_id"] == asset["audio_id"]
        assert stimulus["audio_url"] == asset["path"]
        assert stimulus["script_version"] == asset["script_version"]
        assert stimulus["audio_duration_seconds"] == asset["duration_seconds"]
        assert asset["status"] == "available"
        assert asset["script_id"] == stimulus["id"]
        assert audio_path.is_file()
        assert hashlib.sha256(audio_path.read_bytes()).hexdigest() == asset["sha256"]
        with wave.open(str(audio_path)) as audio_file:
            measured_duration = audio_file.getnframes() / audio_file.getframerate()
            assert audio_file.getframerate() == asset["sample_rate_hz"] == 24000
            assert audio_file.getnchannels() == asset["channels"] == 1
            assert audio_file.getsampwidth() * 8 == asset["sample_width_bits"] == 16
        assert abs(measured_duration - asset["duration_seconds"]) < 0.01

    assert not list(STATIC_AUDIO_DIR.glob("*transcription*"))
    assert not list(STATIC_AUDIO_DIR.glob("*.vtt"))
    assert not list(STATIC_AUDIO_DIR.glob("*.srt"))
