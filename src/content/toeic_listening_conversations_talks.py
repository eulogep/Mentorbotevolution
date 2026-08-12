"""Original formative Listening content for conversations and short talks.

All scripts, questions, options, explanations, and remediations are original.
They must not be exposed before the learner has completed the matching attempt.
No ETS audio, script, item, visual, answer key, or score conversion is used.
"""

from copy import deepcopy
from functools import lru_cache
import json
from pathlib import Path


TOEIC_LISTENING_CONVERSATIONS_TALKS_ID = "toeic-listening-conversations-talks-v1"
ASSET_MANIFEST_PATH = Path(__file__).with_name("listening_conversations_talks_assets.json")
PRIVATE_AUDIO_DIR = Path(__file__).with_name("listening_audio")

TOEIC_LISTENING_CONVERSATIONS_TALKS = {
    "id": TOEIC_LISTENING_CONVERSATIONS_TALKS_ID,
    "content_version": "1.0.0",
    "title": "Diagnostic écoute — conversations et présentations",
    "description": (
        "Quatre extraits audio originaux d’anglais professionnel. Chaque extrait "
        "est écouté une fois puis sert à deux questions."
    ),
    "learning_domain": "language",
    "source": "editorial_original",
    "disclaimer": (
        "Cette activité formative originale ne constitue pas un test TOEIC officiel "
        "et ne fournit aucune estimation de score ou de niveau."
    ),
    "max_plays_per_stimulus": 1,
    "stimuli": [
        {
            "id": "conversation-01",
            "task_type": "listening_conversation",
            "scenario": "delivery-installation",
            "audio_id": "lct-01",
            "asset_filename": "lct-01.wav",
            "audio_status": "available",
            "script_version": "1.0.0",
            "audio_duration_seconds": None,
            "max_plays": 1,
            "speaker_transcript": [
                {
                    "speaker": "Marissa",
                    "text": "Hi Daniel, the delivery for the Northgate office has been moved to Wednesday morning.",
                },
                {
                    "speaker": "Daniel",
                    "text": "Thanks for letting me know. Should I update the installation team?",
                },
                {
                    "speaker": "Marissa",
                    "text": "Yes, please. They need the new time before today's briefing.",
                },
            ],
        },
        {
            "id": "conversation-02",
            "task_type": "listening_conversation",
            "scenario": "client-briefing",
            "audio_id": "lct-02",
            "asset_filename": "lct-02.wav",
            "audio_status": "available",
            "script_version": "1.0.0",
            "audio_duration_seconds": None,
            "max_plays": 1,
            "speaker_transcript": [
                {
                    "speaker": "Evan",
                    "text": "Could we reserve the small meeting room for the client briefing?",
                },
                {
                    "speaker": "Priya",
                    "text": "It is free from two until four. I will book it under your name.",
                },
                {
                    "speaker": "Evan",
                    "text": "Great. Please add a video link in case the client joins remotely.",
                },
            ],
        },
        {
            "id": "talk-01",
            "task_type": "listening_talk",
            "scenario": "building-safety-notice",
            "audio_id": "lct-03",
            "asset_filename": "lct-03.wav",
            "audio_status": "available",
            "script_version": "1.0.0",
            "audio_duration_seconds": None,
            "max_plays": 1,
            "speaker_transcript": [
                {
                    "speaker": "Facilities announcement",
                    "text": (
                        "Good morning. Exit C will be closed from nine until noon while "
                        "the door mechanism is repaired. Please use Exit B on the east side "
                        "of the lobby. The fire drill has been rescheduled to Friday at ten."
                    ),
                },
            ],
        },
        {
            "id": "talk-02",
            "task_type": "listening_talk",
            "scenario": "returns-process-update",
            "audio_id": "lct-04",
            "asset_filename": "lct-04.wav",
            "audio_status": "available",
            "script_version": "1.0.0",
            "audio_duration_seconds": None,
            "max_plays": 1,
            "speaker_transcript": [
                {
                    "speaker": "Customer service announcement",
                    "text": (
                        "Attention customer service colleagues. The updated return form will "
                        "be available in the portal from Monday. A short online demonstration "
                        "will take place at three o'clock today. Please continue using the current "
                        "form until the new one appears."
                    ),
                },
            ],
        },
    ],
    "items": [
        {
            "id": "lct-01-q1",
            "stimulus_id": "conversation-01",
            "task_type": "listening_conversation",
            "target": "listening_detail",
            "scenario": "delivery-installation",
            "choices": [
                "The Northgate office reception desk.",
                "The installation team.",
                "The finance department.",
            ],
            "choice_labels": ["A", "B", "C"],
            "correct_index": 1,
            "explanation": "Daniel asks whether he should update the installation team, and Marissa confirms this.",
            "remediation": None,
        },
        {
            "id": "lct-01-q2",
            "stimulus_id": "conversation-01",
            "task_type": "listening_conversation",
            "target": "listening_inference",
            "scenario": "delivery-installation",
            "choices": [
                "The delivery has been cancelled.",
                "The office is closed on Wednesday.",
                "The team needs the revised time before a briefing.",
            ],
            "choice_labels": ["A", "B", "C"],
            "correct_index": 2,
            "explanation": "Marissa says the installation team needs the new time before today's briefing.",
            "remediation": None,
        },
        {
            "id": "lct-02-q1",
            "stimulus_id": "conversation-02",
            "task_type": "listening_conversation",
            "target": "listening_detail",
            "scenario": "client-briefing",
            "choices": [
                "Move a delivery appointment.",
                "Reserve a meeting room.",
                "Prepare a budget report.",
            ],
            "choice_labels": ["A", "B", "C"],
            "correct_index": 1,
            "explanation": "Priya says she will book the small meeting room under Evan's name.",
            "remediation": {
                "front": "Comment dire que l’on réserve une salle pour quelqu’un ?",
                "back": "I will book it under your name. — Cette formulation confirme une réservation au nom d’une personne.",
                "concept_name": "Réserver une salle au nom d’une personne",
                "tags": ["toeic", "diagnostic", "listening", "meeting", "booking"],
            },
        },
        {
            "id": "lct-02-q2",
            "stimulus_id": "conversation-02",
            "task_type": "listening_conversation",
            "target": "listening_inference",
            "scenario": "client-briefing",
            "choices": [
                "The client may attend without being in the room.",
                "The briefing has been postponed.",
                "The meeting room has no internet connection.",
            ],
            "choice_labels": ["A", "B", "C"],
            "correct_index": 0,
            "explanation": "Evan requests a video link in case the client joins remotely.",
            "remediation": None,
        },
        {
            "id": "lct-03-q1",
            "stimulus_id": "talk-01",
            "task_type": "listening_talk",
            "target": "listening_detail",
            "scenario": "building-safety-notice",
            "choices": [
                "Exit C near the parking area.",
                "The staff entrance on the ground floor.",
                "Exit B on the east side of the lobby.",
            ],
            "choice_labels": ["A", "B", "C"],
            "correct_index": 2,
            "explanation": "The announcement directs staff to use Exit B on the east side of the lobby.",
            "remediation": None,
        },
        {
            "id": "lct-03-q2",
            "stimulus_id": "talk-01",
            "task_type": "listening_talk",
            "target": "listening_main_idea",
            "scenario": "building-safety-notice",
            "choices": [
                "A new staff recruitment process.",
                "A change to building access and safety arrangements.",
                "A request to order office equipment.",
            ],
            "choice_labels": ["A", "B", "C"],
            "correct_index": 1,
            "explanation": "The message announces a temporary exit closure and a rescheduled fire drill.",
            "remediation": None,
        },
        {
            "id": "lct-04-q1",
            "stimulus_id": "talk-02",
            "task_type": "listening_talk",
            "target": "listening_detail",
            "scenario": "returns-process-update",
            "choices": [
                "A revised delivery schedule.",
                "A customer feedback survey.",
                "The updated return form.",
            ],
            "choice_labels": ["A", "B", "C"],
            "correct_index": 2,
            "explanation": "The announcement says the updated return form will be available from Monday.",
            "remediation": {
                "front": "Comment annoncer qu’une ressource sera disponible à une date donnée ?",
                "back": "The updated return form will be available in the portal from Monday. — Cette formulation annonce une mise à disposition future.",
                "concept_name": "Annoncer une disponibilité future",
                "tags": ["toeic", "diagnostic", "listening", "customer-service", "future"],
            },
        },
        {
            "id": "lct-04-q2",
            "stimulus_id": "talk-02",
            "task_type": "listening_talk",
            "target": "listening_inference",
            "scenario": "returns-process-update",
            "choices": [
                "Keep using the current form for now.",
                "Stop accepting returns today.",
                "Send the return form by email immediately.",
            ],
            "choice_labels": ["A", "B", "C"],
            "correct_index": 0,
            "explanation": "Staff are asked to continue using the current form until the new form appears.",
            "remediation": None,
        },
    ],
}


@lru_cache(maxsize=1)
def _load_asset_manifest() -> dict:
    """Parse the versioned private asset manifest once per application process."""
    return json.loads(ASSET_MANIFEST_PATH.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _assets_by_stimulus() -> dict:
    """Index the immutable manifest by shared stimulus identifier."""
    return {asset["stimulus_id"]: asset for asset in _load_asset_manifest()["items"]}


def _attach_asset_metadata(diagnostic: dict) -> dict:
    """Attach provenance-backed availability and durations to a private copy."""
    assets_by_stimulus = _assets_by_stimulus()
    for stimulus in diagnostic["stimuli"]:
        asset = assets_by_stimulus.get(stimulus["id"])
        if not asset:
            stimulus["audio_status"] = "unavailable"
            stimulus["audio_duration_seconds"] = None
            continue
        stimulus["audio_status"] = asset["status"]
        stimulus["audio_duration_seconds"] = asset["duration_seconds"]
    return diagnostic


def get_toeic_listening_conversations_talks_diagnostic() -> dict:
    """Return a defensive copy of the original Listening increment-two package."""
    return _attach_asset_metadata(deepcopy(TOEIC_LISTENING_CONVERSATIONS_TALKS))


def get_toeic_listening_conversations_talks_item(item_id: str) -> dict | None:
    """Return one private Listening item without copying the full package."""
    for item in TOEIC_LISTENING_CONVERSATIONS_TALKS["items"]:
        if item["id"] == item_id:
            return deepcopy(item)
    return None


def get_toeic_listening_conversations_talks_stimulus(stimulus_id: str) -> dict | None:
    """Return one private Listening stimulus with its verified asset metadata."""
    for stimulus in TOEIC_LISTENING_CONVERSATIONS_TALKS["stimuli"]:
        if stimulus["id"] == stimulus_id:
            return _attach_asset_metadata({"stimuli": [deepcopy(stimulus)]})["stimuli"][0]
    return None


def get_toeic_listening_conversations_talks_audio_path(stimulus_id: str) -> Path | None:
    """Resolve a verified private WAV path without accepting a client-provided filename."""
    stimulus = get_toeic_listening_conversations_talks_stimulus(stimulus_id)
    if not stimulus or stimulus.get("audio_status") != "available":
        return None
    path = (PRIVATE_AUDIO_DIR / stimulus["asset_filename"]).resolve()
    if path.parent != PRIVATE_AUDIO_DIR.resolve() or not path.is_file():
        return None
    return path
