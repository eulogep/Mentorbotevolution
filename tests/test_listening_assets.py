import hashlib
import json
import wave
from pathlib import Path

from src.content.toeic_listening_question_response import (
    get_toeic_listening_question_response_diagnostic,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "src" / "content" / "listening_assets.json"
STATIC_AUDIO_DIR = PROJECT_ROOT / "public" / "listening"


def test_listening_manifest_matches_available_original_audio_assets():
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    diagnostic = get_toeic_listening_question_response_diagnostic()

    assert manifest["module"] == diagnostic["id"]
    assert manifest["origin"] == "editorial_original"
    assert len(manifest["items"]) == 4
    assert len(diagnostic["items"]) == 4

    manifest_by_id = {asset["audio_id"]: asset for asset in manifest["items"]}
    assert set(manifest_by_id) == {item["audio_id"] for item in diagnostic["items"]}

    for item in diagnostic["items"]:
        asset = manifest_by_id[item["audio_id"]]
        audio_path = STATIC_AUDIO_DIR / Path(asset["path"]).name
        assert item["audio_status"] == "available"
        assert asset["path"] == item["audio_url"]
        assert asset["status"] == "available"
        assert asset["script_id"] == item["id"]
        assert asset["script_version"] == item["script_version"]
        assert asset["sha256"]
        assert audio_path.is_file()
        assert hashlib.sha256(audio_path.read_bytes()).hexdigest() == asset["sha256"]
        with wave.open(str(audio_path)) as audio_file:
            measured_duration = audio_file.getnframes() / audio_file.getframerate()
        assert abs(measured_duration - asset["duration_seconds"]) < 0.5

    assert not list(STATIC_AUDIO_DIR.glob("*transcription*"))
