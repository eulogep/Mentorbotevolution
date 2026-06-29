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

    # Relationships
    cards = db.relationship("Card", backref="owner", lazy=True)
    subjects = db.relationship("Subject", backref="owner", lazy=True)
    study_sessions = db.relationship("StudySession", backref="owner", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class Subject(db.Model):
    """A learning subject/topic that the user studies."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default="")
    target_score = db.Column(db.Integer, default=800)
    current_score = db.Column(db.Integer, default=0)
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "mastery": self.mastery,
            "subject_id": self.subject_id,
        }

    def __repr__(self):
        return f"<Concept {self.name}>"


class Card(db.Model):
    """A spaced repetition flashcard."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"), nullable=True)
    concept_name = db.Column(db.String(200), nullable=False)
    front_content = db.Column(db.Text, default="")  # Question / front side
    back_content = db.Column(db.Text, default="")   # Answer / back side
    difficulty = db.Column(db.String(20), default="medium")  # easy, medium, hard
    priority = db.Column(db.String(20), default="normal")    # low, normal, high
    tags = db.Column(db.Text, default="")  # Comma-separated tags

    # SM-2 algorithm fields
    interval = db.Column(db.Integer, default=1)         # Current interval in days
    easiness_factor = db.Column(db.Float, default=2.5)   # EF (1.3 - 4.0)
    review_count = db.Column(db.Integer, default=0)
    success_count = db.Column(db.Integer, default=0)
    total_response_time = db.Column(db.Float, default=0.0)  # Cumulative seconds

    # Scheduling
    last_reviewed = db.Column(db.DateTime, nullable=True)
    next_review = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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
            "front_content": self.front_content,
            "back_content": self.back_content,
            "difficulty": self.difficulty,
            "priority": self.priority,
            "tags": self.tags.split(",") if self.tags else [],
            "interval": self.interval,
            "easiness_factor": self.easiness_factor,
            "review_count": self.review_count,
            "success_rate": round(self.success_rate, 3),
            "average_response_time": round(self.average_response_time, 1),
            "last_reviewed": self.last_reviewed.isoformat() if self.last_reviewed else None,
            "next_review": self.next_review.isoformat() if self.next_review else None,
            "days_overdue": self.days_overdue,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<Card {self.concept_name}>"


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
