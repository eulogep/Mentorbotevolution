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
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, send_from_directory
from flask_cors import CORS
from datetime import timedelta
from flask_jwt_extended import JWTManager
from src.models.user import db, TokenBlocklist
from src.routes.user import user_bp
from src.routes.learning import learning_bp
from src.routes.mastery import mastery_bp
from src.routes.analysis import analysis_bp
from src.routes.spaced_repetition import spaced_repetition_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
# Secrets et JWT
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'please-change-in-production')
app.config['JWT_SECRET_KEY'] = os.environ.get('SECRET_KEY', app.config['SECRET_KEY'])
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

# Configuration CORS pour permettre les requêtes cross-origin
CORS(app)

# Enregistrement des blueprints existants
app.register_blueprint(user_bp, url_prefix='/api/user')
app.register_blueprint(learning_bp, url_prefix='/api/learning')
app.register_blueprint(mastery_bp, url_prefix='/api/mastery')

# Enregistrement des nouveaux blueprints v2.0
app.register_blueprint(analysis_bp, url_prefix='/api/analysis')
app.register_blueprint(spaced_repetition_bp, url_prefix='/api/spaced-repetition')

# Configuration base de données SQLite (compatible Vercel serverless)
# - En prod Vercel, utiliser /tmp (writable)
# - En local, utiliser ./database/app.db
use_db_uri = os.environ.get('DATABASE_URL')
if not use_db_uri:
    if os.environ.get('VERCEL'):
        tmp_dir = '/tmp'
        use_db_uri = f"sqlite:///{os.path.join(tmp_dir, 'app.db')}"
    else:
        db_dir = os.path.join(os.path.dirname(__file__), 'database')
        os.makedirs(db_dir, exist_ok=True)
        use_db_uri = f"sqlite:///{os.path.join(db_dir, 'app.db')}"
app.config['SQLALCHEMY_DATABASE_URI'] = use_db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialisation DB et JWT
jwt = JWTManager(app)

db.init_app(app)
with app.app_context():
    try:
        db.create_all()
    except Exception:
        pass

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload.get('jti')
    if not jti:
        return True
    return db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar() is not None

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
