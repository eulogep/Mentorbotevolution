"""
Database Models for Euloge Learning Platform
=============================================

@author: EULOGE MABIALA
@description: SQLAlchemy models for users, cards, subjects, and study sessions
@version: 2.1.0
"""

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Compromis explicite entre rétention visée et volume quotidien de révisions.
    desired_retention = db.Column(db.Float, default=0.90)

    # Relationships
    cards = db.relationship("Card", backref="owner", lazy=True)
    subjects = db.relationship("Subject", backref="owner", lazy=True)
    study_sessions = db.relationship("StudySession", backref="owner", lazy=True)
    review_logs = db.relationship("ReviewLog", backref="owner", lazy=True, cascade="all, delete-orphan")
    adaptive_profiles = db.relationship("AdaptiveLearningProfile", backref="owner", lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class AdaptiveLearningProfile(db.Model):
    """Explicit FSRS retention preference for one learner and one domain."""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    domain = db.Column(db.String(50), nullable=False)
    desired_retention = db.Column(db.Float, nullable=False, default=0.90)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint("user_id", "domain", name="uq_adaptive_profile_user_domain"),)

    def to_dict(self):
        return {
            "id": self.id,
            "domain": self.domain,
            "desired_retention": self.desired_retention,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Subject(db.Model):
    """A learning subject/topic that the user studies."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default="")
    # Les scores sont conservés pour les parcours d’examen, mais ne servent pas
    # à évaluer arbitrairement les parcours techniques ou professionnels.
    target_score = db.Column(db.Integer, default=None, nullable=True)
    current_score = db.Column(db.Integer, default=None, nullable=True)
    domain = db.Column(db.String(50), default="general", nullable=False)
    objective_type = db.Column(db.String(50), default="competency", nullable=False)
    objective_label = db.Column(db.String(200), default="Compétence visée")
    target_date = db.Column(db.Date, nullable=True)
    weekly_hours = db.Column(db.Float, nullable=True)
    source = db.Column(db.String(50), default="user_created", nullable=False)
    progress = db.Column(db.Float, default=0.0)  # 0.0 to 100.0
    status = db.Column(db.String(30), default="not_started")  # not_started, in_progress, mastered
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    cards = db.relationship("Card", backref="subject", lazy=True)
    concepts = db.relationship("Concept", backref="subject", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "target_score": self.target_score,
            "current_score": self.current_score,
            "domain": self.domain,
            "objective_type": self.objective_type,
            "objective_label": self.objective_label,
            "target_date": self.target_date.isoformat() if self.target_date else None,
            "weekly_hours": self.weekly_hours,
            "source": self.source,
            "progress": self.progress,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "concepts": [c.to_dict() for c in self.concepts],
        }

    def __repr__(self):
        return f"<Subject {self.name}>"


class Concept(db.Model):
    """A specific concept belonging to a Subject."""
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(30), default="not-started")  # not-started, in-progress, completed
    mastery = db.Column(db.Integer, default=0)  # 0 to 100
    competency_type = db.Column(db.String(50), default="knowledge", nullable=False)
    evidence_criterion = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "mastery": self.mastery,
            "competency_type": self.competency_type,
            "evidence_criterion": self.evidence_criterion,
            "subject_id": self.subject_id,
        }

    def __repr__(self):
        return f"<Concept {self.name}>"


class Card(db.Model):
    """A spaced repetition flashcard."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"), nullable=True)
    learning_domain = db.Column(db.String(50), nullable=True)
    concept_name = db.Column(db.String(200), nullable=False)
    front_content = db.Column(db.Text, default="")  # Question / front side
    back_content = db.Column(db.Text, default="")   # Answer / back side
    difficulty = db.Column(db.String(20), default="medium")  # easy, medium, hard
    priority = db.Column(db.String(20), default="normal")    # low, normal, high
    tags = db.Column(db.Text, default="")  # Comma-separated tags

    # SM-2 algorithm fields
    interval = db.Column(db.Integer, default=1)         # Legacy full-day interval
    interval_minutes = db.Column(db.Integer, nullable=True)  # Precise FSRS delay
    easiness_factor = db.Column(db.Float, default=2.5)   # EF (1.3 - 4.0)
    review_count = db.Column(db.Integer, default=0)
    success_count = db.Column(db.Integer, default=0)
    total_response_time = db.Column(db.Float, default=0.0)  # Cumulative seconds

    # État du planificateur (FSRS). Les champs SM-2 précédents restent présents
    # pour une migration progressive et la rétrocompatibilité des cartes existantes.
    scheduler_type = db.Column(db.String(30), default="sm2")
    scheduler_state = db.Column(db.Text, default="")
    scheduler_version = db.Column(db.String(30), default="legacy")

    # Scheduling
    last_reviewed = db.Column(db.DateTime, nullable=True)
    next_review = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    review_logs = db.relationship("ReviewLog", backref="card", lazy=True, cascade="all, delete-orphan")

    @property
    def success_rate(self):
        if self.review_count == 0:
            return 0.0
        return self.success_count / self.review_count

    @property
    def average_response_time(self):
        if self.review_count == 0:
            return 0.0
        return self.total_response_time / self.review_count

    @property
    def days_overdue(self):
        if self.next_review is None:
            return 0
        delta = (datetime.utcnow() - self.next_review).days
        return max(0, delta)

    @property
    def is_due(self):
        return self.next_review is not None and self.next_review <= datetime.utcnow()

    def to_dict(self):
        return {
            "id": self.id,
            "concept_name": self.concept_name,
            "learning_domain": self.learning_domain or (self.subject.domain if self.subject else "general"),
            "front_content": self.front_content,
            "back_content": self.back_content,
            "difficulty": self.difficulty,
            "priority": self.priority,
            "tags": self.tags.split(",") if self.tags else [],
            "interval": self.interval,
            "interval_minutes": self.interval_minutes,
            "easiness_factor": self.easiness_factor,
            "review_count": self.review_count,
            "success_rate": round(self.success_rate, 3),
            "average_response_time": round(self.average_response_time, 1),
            "scheduler_type": self.scheduler_type,
            "scheduler_version": self.scheduler_version,
            "last_reviewed": self.last_reviewed.isoformat() if self.last_reviewed else None,
            "next_review": self.next_review.isoformat() if self.next_review else None,
            "days_overdue": self.days_overdue,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<Card {self.concept_name}>"


class ReviewLog(db.Model):
    """Immutable audit trail for one spaced-repetition review."""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    card_id = db.Column(db.Integer, db.ForeignKey("card.id"), nullable=False, index=True)
    rating = db.Column(db.String(12), nullable=False)  # again, hard, good, easy
    response_time = db.Column(db.Float, default=0.0)
    retrievability_before = db.Column(db.Float, nullable=True)
    # `scheduled_days` is retained for legacy reporting; `scheduled_minutes`
    # preserves FSRS learning steps and is the source of truth for new reviews.
    scheduled_days = db.Column(db.Integer, default=0)
    scheduled_minutes = db.Column(db.Integer, nullable=True)
    scheduler_version = db.Column(db.String(30), default="fsrs-6")
    previous_state = db.Column(db.Text, default="")
    review_log = db.Column(db.Text, default="")
    next_state = db.Column(db.Text, default="")
    reviewed_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "card_id": self.card_id,
            "rating": self.rating,
            "response_time": self.response_time,
            "retrievability_before": self.retrievability_before,
            "scheduled_days": self.scheduled_days,
            "scheduled_minutes": self.scheduled_minutes,
            "scheduler_version": self.scheduler_version,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
        }


class StudySession(db.Model):
    """Tracks individual study sessions for analytics."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"), nullable=True)
    session_type = db.Column(db.String(50), default="review")  # review, deep_work, quiz
    cards_reviewed = db.Column(db.Integer, default=0)
    cards_correct = db.Column(db.Integer, default=0)
    duration_minutes = db.Column(db.Float, default=0.0)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime, nullable=True)

    @property
    def accuracy(self):
        if self.cards_reviewed == 0:
            return 0.0
        return self.cards_correct / self.cards_reviewed

    def to_dict(self):
        return {
            "id": self.id,
            "session_type": self.session_type,
            "cards_reviewed": self.cards_reviewed,
            "cards_correct": self.cards_correct,
            "accuracy": round(self.accuracy, 3),
            "duration_minutes": self.duration_minutes,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
        }

    def __repr__(self):
        return f"<StudySession {self.session_type} @ {self.started_at}>"
