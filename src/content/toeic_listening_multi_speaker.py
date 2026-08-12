"""Original multi-speaker Listening increment for Mentor Evolution.

All scripts, questions, options, explanations, and remediations are original.
They must not be exposed before the learner has completed the matching attempt.
No ETS audio, script, item, visual, answer key, or score conversion is used.
"""

from copy import deepcopy
from functools import lru_cache
import json
from pathlib import Path


TOEIC_LISTENING_MULTI_SPEAKER_ID = "toeic-listening-multi-speaker-v1"
ASSET_MANIFEST_PATH = Path(__file__).with_name("listening_multi_speaker_assets.json")
PRIVATE_AUDIO_DIR = Path(__file__).with_name("listening_audio")

TOEIC_LISTENING_MULTI_SPEAKER = {
    "id": TOEIC_LISTENING_MULTI_SPEAKER_ID,
    "content_version": "1.0.0",
    "title": "Diagnostic écoute — échanges professionnels approfondis",
    "description": (
        "Quatre extraits audio originaux d’anglais professionnel. Chaque extrait "
        "est écouté une fois puis sert à trois questions de compréhension."
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
            "scenario": "shipment-quality-check",
            "audio_id": "lms-01",
            "asset_filename": "lms-01.wav",
            "audio_status": "available",
            "script_version": "1.0.0",
            "audio_duration_seconds": None,
            "max_plays": 1,
            "speaker_transcript": [
                {
                    "speaker": "Lena",
                    "text": (
                        "Hi Marcus. I saw that the April shipment was planned for Monday, "
                        "but the supplier has confirmed delivery for Friday instead."
                    ),
                },
                {
                    "speaker": "Marcus",
                    "text": (
                        "That leaves very little time for the quality check. Can the warehouse "
                        "team start the first inspection on Friday afternoon?"
                    ),
                },
                {
                    "speaker": "Lena",
                    "text": (
                        "Yes. I spoke to the supervisor, and she can assign two people once the "
                        "pallets arrive. I will send the revised schedule before lunch."
                    ),
                },
            ],
        },
        {
            "id": "conversation-02",
            "task_type": "listening_conversation",
            "scenario": "conference-travel",
            "audio_id": "lms-02",
            "asset_filename": "lms-02.wav",
            "audio_status": "available",
            "script_version": "1.0.0",
            "audio_duration_seconds": None,
            "max_plays": 1,
            "speaker_transcript": [
                {
                    "speaker": "Tomas",
                    "text": (
                        "Rina, the presenter has confirmed the conference dates. The flight leaves "
                        "Thursday at seven twenty, but Human Resources still needs to approve the travel costs."
                    ),
                },
                {
                    "speaker": "Rina",
                    "text": (
                        "I understand. Could you check whether that approval will arrive today? "
                        "The hotel near the conference center is nearly full."
                    ),
                },
                {
                    "speaker": "Tomas",
                    "text": (
                        "I will contact Human Resources now and update you by three o'clock. Once "
                        "the costs are confirmed, you can reserve the hotel."
                    ),
                },
            ],
        },
        {
            "id": "talk-01",
            "task_type": "listening_talk",
            "scenario": "client-portal-handover",
            "audio_id": "lms-03",
            "asset_filename": "lms-03.wav",
            "audio_status": "available",
            "script_version": "1.0.0",
            "audio_duration_seconds": None,
            "max_plays": 1,
            "speaker_transcript": [
                {
                    "speaker": "Project announcement",
                    "text": (
                        "Good afternoon, project team. The client portal upgrade will move to maintenance "
                        "on Tuesday morning. Please upload any outstanding test notes by four o'clock Monday, "
                        "using the latest template in the project folder. After handover, the support desk will "
                        "be the primary contact. We will hold a fifteen-minute review call at nine thirty Tuesday "
                        "to confirm that no critical issues remain."
                    ),
                },
            ],
        },
        {
            "id": "talk-02",
            "task_type": "listening_talk",
            "scenario": "monthly-client-report",
            "audio_id": "lms-04",
            "asset_filename": "lms-04.wav",
            "audio_status": "available",
            "script_version": "1.0.0",
            "audio_duration_seconds": None,
            "max_plays": 1,
            "speaker_transcript": [
                {
                    "speaker": "Operations update",
                    "text": (
                        "This is a reminder about the monthly client report. Because the data refresh will finish "
                        "late Tuesday, the report will be released on Thursday rather than Wednesday. The analytics "
                        "team will send a draft on Tuesday evening. Account managers should validate their figures by "
                        "noon Wednesday. If you expect to be away, please notify your team lead by Monday so another "
                        "manager can complete the review."
                    ),
                },
            ],
        },
    ],
    "items": [
        {
            "id": "lms-01-q1",
            "stimulus_id": "conversation-01",
            "task_type": "listening_conversation",
            "target": "listening_detail",
            "scenario": "shipment-quality-check",
            "choices": [
                "Monday.",
                "Friday.",
                "The following Wednesday.",
            ],
            "choice_labels": ["A", "B", "C"],
            "correct_index": 1,
            "explanation": "Lena says that the supplier has confirmed delivery for Friday instead of Monday.",
            "remediation": None,
        },
        {
            "id": "lms-01-q2",
            "stimulus_id": "conversation-01",
            "task_type": "listening_conversation",
            "target": "listening_main_idea",
            "scenario": "shipment-quality-check",
            "choices": [
                "To cancel the April shipment.",
                "To hire a new warehouse supervisor.",
                "To adjust the inspection plan after a delivery change.",
            ],
            "choice_labels": ["A", "B", "C"],
            "correct_index": 2,
            "explanation": "The speakers are adjusting the quality-check plan because delivery has moved to Friday.",
            "remediation": None,
        },
        {
            "id": "lms-01-q3",
            "stimulus_id": "conversation-01",
            "task_type": "listening_conversation",
            "target": "listening_inference",
            "scenario": "shipment-quality-check",
            "choices": [
                "Marcus will receive an updated schedule before lunch.",
                "The supplier will cancel the shipment.",
                "The warehouse will inspect the shipment on Monday.",
            ],
            "choice_labels": ["A", "B", "C"],
            "correct_index": 0,
            "explanation": "Lena says that she will send the revised schedule before lunch.",
            "remediation": {
                "front": "Comment dire que l’inspection peut commencer lorsque les palettes sont arrivées ?",
                "back": "The inspection can begin once the pallets arrive. — Cette formulation situe une action après une livraison.",
                "concept_name": "Déclencher une action après une livraison",
                "tags": ["toeic", "diagnostic", "listening", "logistics", "sequencing"],
            },
        },
        {
            "id": "lms-02-q1",
            "stimulus_id": "conversation-02",
            "task_type": "listening_conversation",
            "target": "listening_detail",
            "scenario": "conference-travel",
            "choices": [
                "The conference organizer.",
                "The hotel manager.",
                "Human Resources.",
            ],
            "choice_labels": ["A", "B", "C"],
            "correct_index": 2,
            "explanation": "Tomas says that Human Resources still needs to approve the travel costs.",
            "remediation": None,
        },
        {
            "id": "lms-02-q2",
            "stimulus_id": "conversation-02",
            "task_type": "listening_conversation",
            "target": "listening_main_idea",
            "scenario": "conference-travel",
            "choices": [
                "To choose a new conference venue.",
                "To coordinate travel after cost approval.",
                "To change the presenter's topic.",
            ],
            "choice_labels": ["A", "B", "C"],
            "correct_index": 1,
            "explanation": "The conversation concerns approval of travel costs before the hotel can be reserved.",
            "remediation": None,
        },
        {
            "id": "lms-02-q3",
            "stimulus_id": "conversation-02",
            "task_type": "listening_conversation",
            "target": "listening_inference",
            "scenario": "conference-travel",
            "choices": [
                "Rina will reserve the hotel after confirmation.",
                "Tomas will cancel the flight.",
                "The presenter will book a different hotel.",
            ],
            "choice_labels": ["A", "B", "C"],
            "correct_index": 0,
            "explanation": "Tomas tells Rina that she can reserve the hotel once the costs are confirmed.",
            "remediation": {
                "front": "Comment dire qu’une réservation sera faite après confirmation ?",
                "back": "Once the costs are confirmed, you can reserve the hotel. — Cette formulation conditionne une action à une validation préalable.",
                "concept_name": "Conditionner une réservation à une confirmation",
                "tags": ["toeic", "diagnostic", "listening", "travel", "confirmation"],
            },
        },
        {
            "id": "lms-03-q1",
            "stimulus_id": "talk-01",
            "task_type": "listening_talk",
            "target": "listening_detail",
            "scenario": "client-portal-handover",
            "choices": [
                "By four o'clock Monday.",
                "At nine thirty Tuesday.",
                "By noon Friday.",
            ],
            "choice_labels": ["A", "B", "C"],
            "correct_index": 0,
            "explanation": "The announcement asks the team to upload outstanding test notes by four o'clock Monday.",
            "remediation": None,
        },
        {
            "id": "lms-03-q2",
            "stimulus_id": "talk-01",
            "task_type": "listening_talk",
            "target": "listening_main_idea",
            "scenario": "client-portal-handover",
            "choices": [
                "To announce a new hiring process.",
                "To provide a guide for travel reimbursement.",
                "To explain the portal handover and required preparation.",
            ],
            "choice_labels": ["A", "B", "C"],
            "correct_index": 2,
            "explanation": "The message explains the move to maintenance, the notes to upload, and the post-handover contact.",
            "remediation": None,
        },
        {
            "id": "lms-03-q3",
            "stimulus_id": "talk-01",
            "task_type": "listening_talk",
            "target": "listening_inference",
            "scenario": "client-portal-handover",
            "choices": [
                "The client portal will close permanently.",
                "The review call will take place before any test notes are uploaded.",
                "The support desk will handle most questions after Tuesday morning.",
            ],
            "choice_labels": ["A", "B", "C"],
            "correct_index": 2,
            "explanation": "The support desk becomes the primary contact after the Tuesday-morning handover.",
            "remediation": None,
        },
        {
            "id": "lms-04-q1",
            "stimulus_id": "talk-02",
            "task_type": "listening_talk",
            "target": "listening_detail",
            "scenario": "monthly-client-report",
            "choices": [
                "The account managers.",
                "The analytics team.",
                "The conference organizer.",
            ],
            "choice_labels": ["A", "B", "C"],
            "correct_index": 1,
            "explanation": "The analytics team will send a draft on Tuesday evening.",
            "remediation": None,
        },
        {
            "id": "lms-04-q2",
            "stimulus_id": "talk-02",
            "task_type": "listening_talk",
            "target": "listening_main_idea",
            "scenario": "monthly-client-report",
            "choices": [
                "To announce a change in the report schedule and review tasks.",
                "To introduce a new customer survey.",
                "To explain how to book travel costs.",
            ],
            "choice_labels": ["A", "B", "C"],
            "correct_index": 0,
            "explanation": "The message moves the report release and explains the draft and validation steps.",
            "remediation": None,
        },
        {
            "id": "lms-04-q3",
            "stimulus_id": "talk-02",
            "task_type": "listening_talk",
            "target": "listening_inference",
            "scenario": "monthly-client-report",
            "choices": [
                "Account managers should validate their figures before noon Wednesday.",
                "The report will be released on Tuesday morning.",
                "The analytics team will review every client account alone.",
            ],
            "choice_labels": ["A", "B", "C"],
            "correct_index": 0,
            "explanation": "The announcement explicitly asks account managers to validate their figures by noon Wednesday.",
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


def get_toeic_listening_multi_speaker_diagnostic() -> dict:
    """Return a defensive copy of the original third Listening increment package."""
    return _attach_asset_metadata(deepcopy(TOEIC_LISTENING_MULTI_SPEAKER))


def get_toeic_listening_multi_speaker_item(item_id: str) -> dict | None:
    """Return one private Listening item without copying the full package."""
    for item in TOEIC_LISTENING_MULTI_SPEAKER["items"]:
        if item["id"] == item_id:
            return deepcopy(item)
    return None


def get_toeic_listening_multi_speaker_stimulus(stimulus_id: str) -> dict | None:
    """Return one private Listening stimulus with its verified asset metadata."""
    for stimulus in TOEIC_LISTENING_MULTI_SPEAKER["stimuli"]:
        if stimulus["id"] == stimulus_id:
            return _attach_asset_metadata({"stimuli": [deepcopy(stimulus)]})["stimuli"][0]
    return None


def get_toeic_listening_multi_speaker_audio_path(stimulus_id: str) -> Path | None:
    """Resolve a verified private WAV path without accepting a client-provided filename."""
    stimulus = get_toeic_listening_multi_speaker_stimulus(stimulus_id)
    if not stimulus or stimulus.get("audio_status") != "available":
        return None
    path = (PRIVATE_AUDIO_DIR / stimulus["asset_filename"]).resolve()
    if path.parent != PRIVATE_AUDIO_DIR.resolve() or not path.is_file():
        return None
    return path
