"""
Euloge Learning Platform - Backend API
=====================================

@author: EULOGE MABIALA
@description: Serveur Flask pour la plateforme d'apprentissage IA
@version: 2.0.0
@license: MIT

Ce serveur fournit les API nécessaires pour la plateforme d'apprentissage
basée sur l'IA et les neurosciences pour optimiser la préparation au TOEIC.
"""

import os
import sys
import logging

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(__file__))  # noqa: E402

from dotenv import load_dotenv  # noqa: E402
from flask import Flask, send_from_directory  # noqa: E402
from flask_cors import CORS  # noqa: E402
from flask_jwt_extended import JWTManager  # noqa: E402
from datetime import timedelta  # noqa: E402
from src.models.user import db  # noqa: E402
from src.routes.user import user_bp  # noqa: E402
from src.routes.learning import learning_bp  # noqa: E402
from src.routes.mastery import mastery_bp  # noqa: E402
from src.routes.analysis import analysis_bp  # noqa: E402
from src.routes.spaced_repetition import spaced_repetition_bp  # noqa: E402

# Load environment variables from .env file
load_dotenv()


def get_database_uri():
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        if database_url.startswith("postgres://"):
            return database_url.replace("postgres://", "postgresql://", 1)
        return database_url

    if os.environ.get("VERCEL"):
        logging.warning(
            "DATABASE_URL is not set on Vercel; falling back to ephemeral SQLite in /tmp."
        )
        return "sqlite:////tmp/app.db"

    db_dir = os.path.join(os.path.dirname(__file__), "database")
    os.makedirs(db_dir, exist_ok=True)
    return f"sqlite:///{os.path.join(db_dir, 'app.db')}"

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), "static"))
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "default-dev-key-please-change")
app.config["JWT_SECRET_KEY"] = os.environ.get(
    "JWT_SECRET_KEY", os.environ.get("SECRET_KEY", "default-dev-key-please-change")
)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max upload size

# Configuration CORS pour permettre les requêtes cross-origin (restreint aux origines connues)
CORS(app, origins=[
    "https://mentorbotevolution.vercel.app",
    "http://localhost:3000",
    "http://localhost:5000",
])
jwt = JWTManager(app)

# Enregistrement des blueprints existants
app.register_blueprint(user_bp, url_prefix="/api/user")
app.register_blueprint(learning_bp, url_prefix="/api/learning")
app.register_blueprint(mastery_bp, url_prefix="/api/mastery")

# Enregistrement des nouveaux blueprints v2.0
app.register_blueprint(analysis_bp, url_prefix="/api/analysis")
app.register_blueprint(spaced_repetition_bp, url_prefix="/api/spaced-repetition")

# Database configuration:
# - DATABASE_URL is preferred for PostgreSQL production deployments.
# - SQLite is kept as a local development fallback.
# - Vercel without DATABASE_URL uses ephemeral /tmp SQLite only as a temporary fallback.
app.config["SQLALCHEMY_DATABASE_URI"] = get_database_uri()
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialisation DB (création des tables si nécessaire)
db.init_app(app)
with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        logging.warning(f"Could not create database tables: {e}")


@app.route("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "mentorbot-flask-api",
        "version": "2.0.0",
    }


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, "index.html")
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, "index.html")
        else:
            return "index.html not found", 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
