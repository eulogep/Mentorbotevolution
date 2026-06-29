from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from src.models.user import db, Subject, Concept

mastery_bp = Blueprint('mastery', __name__)

@mastery_bp.route('/subjects', methods=['GET'])
@jwt_required()
def get_subjects():
    try:
        user_id = int(get_jwt_identity())
        subjects = Subject.query.filter_by(user_id=user_id).all()
        return jsonify([s.to_dict() for s in subjects])
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@mastery_bp.route('/get-subjects', methods=['GET'])
@jwt_required()
def get_subjects_enhanced():
    """Endpoint attendu par le frontend: retourne {status, subjects: [...]} depuis la base de données"""
    try:
        user_id = int(get_jwt_identity())
        subjects = Subject.query.filter_by(user_id=user_id).all()

        # Si l'utilisateur n'a aucun plan de maîtrise, on crée un plan TOEIC par défaut pour l'accueil
        if not subjects:
            default_subject = Subject(
                user_id=user_id,
                name="TOEIC Preparation",
                description="Préparation complète au test du TOEIC (IA & Neurosciences)",
                target_score=800,
                current_score=620,
                progress=35.0,
                status="in_progress"
            )
            db.session.add(default_subject)
            db.session.flush()

            default_concepts = [
                Concept(subject_id=default_subject.id, name="Conditional Sentences", status="in-progress", mastery=45),
                Concept(subject_id=default_subject.id, name="Business Vocabulary", status="in-progress", mastery=65),
                Concept(subject_id=default_subject.id, name="Listening Accents", status="not-started", mastery=0),
                Concept(subject_id=default_subject.id, name="Reading Speed", status="not-started", mastery=0)
            ]
            db.session.add_all(default_concepts)
            db.session.commit()
            subjects = [default_subject]

        return jsonify({
            'status': 'success',
            'subjects': [s.to_dict() for s in subjects]
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@mastery_bp.route('/plan', methods=['POST'])
@jwt_required()
def create_plan():
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json() or {}

        subject_name = data.get('subject', 'TOEIC')
        subject = Subject(
            user_id=user_id,
            name=subject_name,
            description=f"Plan de maîtrise pour {subject_name}",
            target_score=800,
            status="in_progress"
        )
        db.session.add(subject)
        db.session.commit()

        return jsonify(subject.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500
 