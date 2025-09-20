from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


db = SQLAlchemy()


class TokenBlocklist(db.Model):
    __tablename__ = 'token_blocklist'
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    documents = db.relationship('Document', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'


class Document(db.Model):
    __tablename__ = 'documents'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    filename = db.Column(db.String(255), nullable=False)
    mime_type = db.Column(db.String(128), nullable=True)
    text = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    concepts = db.relationship('Concept', backref='document', lazy=True, cascade='all, delete-orphan')


class Concept(db.Model):
    __tablename__ = 'concepts'
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False, index=True)
    category = db.Column(db.String(64), nullable=True)  # grammar, vocabulary, skill
    importance = db.Column(db.Float, nullable=True)
    difficulty = db.Column(db.String(32), nullable=True)  # easy/medium/hard
    description = db.Column(db.Text, nullable=True)

    exercises = db.relationship('Exercise', backref='concept', lazy=True, cascade='all, delete-orphan')


class Exercise(db.Model):
    __tablename__ = 'exercises'
    id = db.Column(db.Integer, primary_key=True)
    concept_id = db.Column(db.Integer, db.ForeignKey('concepts.id'), nullable=False)
    type = db.Column(db.String(64), nullable=False)  # flashcard, quiz, grammar_practice, vocabulary_practice, skill_practice
    question = db.Column(db.Text, nullable=True)
    answer = db.Column(db.Text, nullable=True)
    estimated_time = db.Column(db.Integer, nullable=True)  # minutes
    difficulty = db.Column(db.String(32), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
