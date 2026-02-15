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

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), "static"))
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "default-dev-key-please-change")
app.config["JWT_SECRET_KEY"] = os.environ.get(
    "JWT_SECRET_KEY", os.environ.get("SECRET_KEY", "jwt-secret-key")
)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)

# Configuration CORS pour permettre les requêtes cross-origin
CORS(app)
jwt = JWTManager(app)

# Enregistrement des blueprints existants
app.register_blueprint(user_bp, url_prefix="/api/user")
app.register_blueprint(learning_bp, url_prefix="/api/learning")
app.register_blueprint(mastery_bp, url_prefix="/api/mastery")

# Enregistrement des nouveaux blueprints v2.0
app.register_blueprint(analysis_bp, url_prefix="/api/analysis")
app.register_blueprint(spaced_repetition_bp, url_prefix="/api/spaced-repetition")

# Configuration base de données SQLite (compatible Vercel serverless)
# - En prod Vercel, utiliser /tmp (writable)
# - En local, utiliser ./database/app.db
use_db_uri = os.environ.get("DATABASE_URL")
if not use_db_uri:
    if os.environ.get("VERCEL"):
        tmp_dir = "/tmp"
        use_db_uri = f"sqlite:///{os.path.join(tmp_dir, 'app.db')}"
    else:
        db_dir = os.path.join(os.path.dirname(__file__), "database")
        os.makedirs(db_dir, exist_ok=True)
        use_db_uri = f"sqlite:///{os.path.join(db_dir, 'app.db')}"
app.config["SQLALCHEMY_DATABASE_URI"] = use_db_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialisation DB (création des tables si nécessaire)
db.init_app(app)
with app.app_context():
    try:
        db.create_all()
    except Exception:
        # En environnement serverless, échouer silencieusement si non nécessaire
        pass


@app.route("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "fastapi-gateway",  # Keeping original name for compatibility with tests
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
