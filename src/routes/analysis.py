"""
API pour l'analyse de documents avec OCR et NLP
===============================================

@author: EULOGE MABIALA & Manus AI
@description: API pour l'analyse sémantique de documents (OCR réel + NLP)
@version: 2.1.0
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from io import BytesIO
import random
import re

from src.models.user import db, Document, Concept, Exercise

analysis_bp = Blueprint('analysis', __name__)


def ocr_extract_text(file_bytes: bytes, mime_type: str, filename: str) -> str:
    """Extrait du texte à partir d'une image/PDF à l'aide de pytesseract ou pdfminer.
    - Images: PNG/JPG -> pytesseract
    - PDF: extraction texte via pdfminer; si indisponible, tentative OCR page par page si pdf2image dispo
    """
    mime = (mime_type or '').lower()
    name = (filename or '').lower()

    # Images: png/jpg/jpeg
    if any(ext in name for ext in ('.png', '.jpg', '.jpeg')) or mime.startswith('image/'):
        try:
            from PIL import Image
            import pytesseract
            image = Image.open(BytesIO(file_bytes))
            text = pytesseract.image_to_string(image, lang='eng+fra')
            return text.strip()
        except Exception as e:
            raise RuntimeError(f"OCR image failed: {str(e)}")

    # PDF: try pdfminer.six textual extraction first
    if name.endswith('.pdf') or mime == 'application/pdf':
        try:
            from pdfminer.high_level import extract_text
            with BytesIO(file_bytes) as fp:
                text = extract_text(fp)
            if text and text.strip():
                return text.strip()
        except Exception:
            pass
        # Last resort: try OCR via pdf2image + pytesseract
        try:
            import pytesseract
            from pdf2image import convert_from_bytes  # requires poppler
            pages = convert_from_bytes(file_bytes)
            out = []
            for pg in pages:
                out.append(pytesseract.image_to_string(pg, lang='eng+fra'))
            return "\n".join(out).strip()
        except Exception as e:
            raise RuntimeError(
                "PDF extraction failed. Ensure pdfminer.six or poppler+pytesseract are available: " + str(e)
            )

    # Fallback: treat as plain text
    return file_bytes.decode('utf-8', errors='ignore')


def nlp_extract_concepts(text: str):
    """Identifie des concepts clés à partir d'un texte.
    Essaie spaCy FR (ou EN) puis fallback regex simple. Retourne une liste de dicts.
    """
    concepts = []
    used_spacy = False

    try:
        import spacy
        nlp = None
        for model in [
            'fr_core_news_md', 'fr_core_news_sm',
            'en_core_web_md', 'en_core_web_sm'
        ]:
            try:
                nlp = spacy.load(model)
                break
            except Exception:
                continue
        if nlp is None:
            # Minimal pipeline for tokenization
            nlp = spacy.blank('fr')
            nlp.add_pipe('sentencizer')
        doc = nlp(text[:200000])  # safety limit
        used_spacy = True

        # Collect noun chunks and entities
        key_candidates = {}
        if hasattr(doc, 'noun_chunks'):
            for chunk in doc.noun_chunks:
                key = chunk.text.strip().lower()
                if 2 <= len(key) <= 60:
                    key_candidates[key] = key_candidates.get(key, 0) + 1
        if hasattr(doc, 'ents'):
            for ent in doc.ents:
                key = ent.text.strip().lower()
                key_candidates[key] = key_candidates.get(key, 0) + 1

        # Simple scoring by frequency and length
        scored = [
            (k, v * (1.0 + min(len(k) / 20.0, 1.0))) for k, v in key_candidates.items()
        ]
        scored.sort(key=lambda x: x[1], reverse=True)
        top = [k for k, _ in scored[:20]]
        for k in top:
            concepts.append({
                'name': k,
                'difficulty': random.choice(['easy', 'medium', 'hard']),
                'importance': round(random.uniform(0.5, 0.95), 2),
                'category': 'vocabulary' if ' ' not in k else 'skill',
                'description': None,
            })
    except Exception:
        used_spacy = False

    if not used_spacy:
        # Regex-based keywords as safe fallback
        tokens = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ]{3,}", text.lower())
        freq = {}
        for t in tokens:
            freq[t] = freq.get(t, 0) + 1
        common = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:20]
        for k, _ in common:
            concepts.append({
                'name': k,
                'difficulty': random.choice(['easy', 'medium', 'hard']),
                'importance': round(random.uniform(0.5, 0.95), 2),
                'category': 'vocabulary',
                'description': None,
            })

    return concepts


def build_exercises_for_concepts(concepts):
    exercises = []
    for concept in concepts:
        name = concept['name']
        ex_list = []
        ex_list.append({
            'type': 'flashcard',
            'question': f"Définissez: {name}",
            'answer': None,
            'estimated_time': random.randint(1, 3),
            'difficulty': concept.get('difficulty', 'medium')
        })
        ex_list.append({
            'type': 'quiz',
            'question': f"Sélectionnez la meilleure utilisation de: {name}",
            'answer': None,
            'estimated_time': random.randint(2, 4),
            'difficulty': concept.get('difficulty', 'medium')
        })
        exercises.append({'concept': name, 'exercises': ex_list})
    return exercises


@analysis_bp.route('/analyze-document', methods=['POST'])
@jwt_required()
def analyze_document():
    try:
        if 'file' not in request.files:
            return jsonify({'status': 'error', 'message': 'Aucun fichier fourni'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'status': 'error', 'message': 'Nom de fichier vide'}), 400

        file_bytes = file.read()
        user_id = get_jwt_identity()
        text = ocr_extract_text(file_bytes, file.content_type, file.filename)
        if not text:
            return jsonify({'status': 'error', 'message': 'Aucun texte détecté'}), 422

        # NLP concepts
        concepts = nlp_extract_concepts(text)
        exercises = build_exercises_for_concepts(concepts)

        # Persist document + concepts + exercises
        doc = Document(user_id=int(user_id) if user_id else None,
                       filename=file.filename,
                       mime_type=file.content_type,
                       text=text)
        db.session.add(doc)
        db.session.flush()

        for c in concepts:
            concept = Concept(
                document_id=doc.id,
                name=c['name'],
                category=c.get('category'),
                importance=c.get('importance'),
                difficulty=c.get('difficulty'),
                description=c.get('description')
            )
            db.session.add(concept)
            db.session.flush()
            # attach exercises
            for ex in [e for e in exercises if e['concept'] == c['name']][0]['exercises']:
                db.session.add(Exercise(
                    concept_id=concept.id,
                    type=ex['type'],
                    question=ex.get('question'),
                    answer=ex.get('answer'),
                    estimated_time=ex.get('estimated_time'),
                    difficulty=ex.get('difficulty')
                ))
        db.session.commit()

        # Spaced repetition plan skeleton
        spaced_repetition = {}
        for c in concepts:
            name = c['name']
            intervals = [1, 3, 7, 14, 30]
            now = datetime.now()
            spaced_repetition[name] = [
                {
                    'review_number': i + 1,
                    'interval_days': d,
                    'scheduled_date': (now + timedelta(days=d)).isoformat(),
                    'completed': False,
                } for i, d in enumerate(intervals)
            ]

        total_exercises = sum(len(e['exercises']) for e in exercises)
        total_study_time = sum(sum(ex['estimated_time'] for ex in e['exercises']) for e in exercises)

        return jsonify({
            'status': 'success',
            'document_id': doc.id,
            'analysis': {
                'extracted_text_preview': text[:500] + ('...' if len(text) > 500 else ''),
                'concepts': concepts,
                'word_count': len(text.split()),
            },
            'generated_content': {
                'exercises': exercises,
                'total_exercises': total_exercises,
                'total_study_time': total_study_time,
                'spaced_repetition': spaced_repetition,
            },
            'timestamp': datetime.now().isoformat(),
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@analysis_bp.route('/concepts', methods=['GET'])
@jwt_required()
def get_concepts():
    doc_id = request.args.get('document_id', type=int)
    if not doc_id:
        return jsonify({'error': 'document_id requis'}), 400
    concepts = Concept.query.filter_by(document_id=doc_id).all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'category': c.category,
        'importance': c.importance,
        'difficulty': c.difficulty,
        'description': c.description,
    } for c in concepts])


@analysis_bp.route('/exercises', methods=['GET'])
@jwt_required()
def get_exercises():
    doc_id = request.args.get('document_id', type=int)
    if not doc_id:
        return jsonify({'error': 'document_id requis'}), 400
    rows = db.session.query(Exercise, Concept).join(Concept, Exercise.concept_id == Concept.id).filter(Concept.document_id == doc_id).all()
    out = []
    for ex, c in rows:
        out.append({
            'id': ex.id,
            'concept_id': c.id,
            'concept': c.name,
            'type': ex.type,
            'question': ex.question,
            'answer': ex.answer,
            'estimated_time': ex.estimated_time,
            'difficulty': ex.difficulty,
        })
    return jsonify(out)


# Les routes suivantes (plan/recommandations) restent disponibles

def get_methods_for_style(learning_style):
    methods_map = {
        'visual': ['Dual Coding', 'Méthode des Lieux', 'Cartes Conceptuelles', 'Visualisations'],
        'auditory': ['Technique Feynman', 'Répétition Orale', 'Podcasts Éducatifs', 'Discussions'],
        'kinesthetic': ['Apprentissage Actif', 'Simulations', 'Exercices Pratiques', 'Jeux de rôle'],
        'mixed': ['Approche Multimodale', 'Rotation des Méthodes', 'Adaptation Contextuelle', 'Personnalisation IA']
    }
    return methods_map.get(learning_style, methods_map['mixed'])


def generate_spaced_repetition_schedule(concept_name):
    now = datetime.now()
    intervals = [1, 3, 7, 14, 30, 60]
    schedule = []
    for i, interval in enumerate(intervals):
        schedule.append({
            'review_number': i + 1,
            'interval_days': interval,
            'scheduled_date': (now + timedelta(days=interval)).isoformat(),
            'completed': False,
            'confidence_required': 0.7 + (i * 0.05)
        })
    return schedule


def generate_weekly_schedule(chronotype, daily_hours):
    schedules = {
        'morning': {
            'monday': {'deep_work': '8h30-10h30', 'review': '14h-15h'},
            'tuesday': {'deep_work': '8h30-10h30', 'practice': '14h-15h30'},
            'wednesday': {'review': '8h30-9h30', 'consolidation': '14h-15h'},
            'thursday': {'deep_work': '8h30-10h30', 'application': '14h-15h30'},
            'friday': {'practice': '8h30-10h', 'review': '14h-15h'},
            'saturday': {'flexible': '9h-11h', 'assessment': '14h-14h30'},
            'sunday': {'rest': 'Repos ou révision légère'}
        },
        'intermediate': {
            'monday': {'deep_work': '10h30-12h30', 'review': '15h30-16h30'},
            'tuesday': {'deep_work': '10h30-12h30', 'practice': '15h30-17h'},
            'wednesday': {'review': '10h30-11h30', 'consolidation': '15h30-16h30'},
            'thursday': {'deep_work': '10h30-12h30', 'application': '15h30-17h'},
            'friday': {'practice': '10h30-12h', 'review': '15h30-16h30'},
            'saturday': {'flexible': '11h-13h', 'assessment': '15h30-16h'},
            'sunday': {'rest': 'Repos ou révision légère'}
        },
        'evening': {
            'monday': {'deep_work': '11h30-13h30', 'review': '17h30-18h30'},
            'tuesday': {'deep_work': '11h30-13h30', 'practice': '17h30-19h'},
            'wednesday': {'review': '11h30-12h30', 'consolidation': '17h30-18h30'},
            'thursday': {'deep_work': '11h30-13h30', 'application': '17h30-19h'},
            'friday': {'practice': '11h30-13h', 'review': '17h30-18h30'},
            'saturday': {'flexible': '12h-14h', 'assessment': '17h30-18h'},
            'sunday': {'rest': 'Repos ou révision légère'}
        }
    }
    return schedules.get(chronotype, schedules['intermediate'])


def get_optimal_times(chronotype):
    times_map = {
        'morning': ['8h-10h', '14h-16h'],
        'intermediate': ['10h-12h', '15h-17h'],
        'evening': ['11h-13h', '17h-19h']
    }
    return times_map.get(chronotype, times_map['intermediate'])


def get_method_effectiveness(learning_style):
    effectiveness_map = {'visual': 0.85, 'auditory': 0.80, 'kinesthetic': 0.75, 'mixed': 0.90}
    return effectiveness_map.get(learning_style, 0.80)


def get_adjustment_suggestions(plan):
    suggestions = []
    if plan['success_probability'] < 0.7:
        suggestions.append("Considérez augmenter le temps d'étude quotidien ou étendre la durée du plan")
    if plan['total_estimated_hours'] > plan['timeframe_months'] * 30 * plan['daily_study_hours']:
        suggestions.append("Le plan est ambitieux. Priorisez les concepts les plus importants")
    if len(plan['concepts_plan']) > 10:
        suggestions.append("Beaucoup de concepts à couvrir. Envisagez de les regrouper par thèmes")
    return suggestions


@analysis_bp.route('/generate-plan', methods=['POST'])
def generate_adaptive_plan():
    try:
        data = request.get_json() or {}
        target_score = data.get('target_score', 800)
        timeframe_months = data.get('timeframe_months', 3)
        daily_study_hours = data.get('daily_study_hours', 2)
        learning_style = data.get('learning_style', 'mixed')
        chronotype = data.get('chronotype', 'intermediate')
        concepts = data.get('concepts', [])

        plan = {
            'id': f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'target_score': target_score,
            'timeframe_months': timeframe_months,
            'daily_study_hours': daily_study_hours,
            'learning_style': learning_style,
            'chronotype': chronotype,
            'created_at': datetime.now().isoformat(),
            'concepts_plan': [],
            'weekly_schedule': {},
            'milestones': [],
            'success_probability': 0.0,
            'total_estimated_hours': 0,
        }

        total_hours = 0
        for i, concept in enumerate(concepts):
            name = concept.get('name', f'Concept {i+1}')
            concept_plan = {
                'name': name,
                'priority': i + 1,
                'difficulty': concept.get('difficulty', 'medium'),
                'importance': concept.get('importance', 0.5),
                'estimated_hours': random.randint(10, 40),
                'weekly_hours': random.randint(2, 8),
                'methods': get_methods_for_style(learning_style),
                'spaced_repetition': generate_spaced_repetition_schedule(name),
                'exercises_count': random.randint(20, 50),
                'mastery_criteria': {
                    'theoretical_understanding': 0.8,
                    'practical_application': 0.7,
                    'long_term_retention': 0.8,
                    'transfer_ability': 0.6,
                    'teaching_capability': 0.5
                }
            }
            plan['concepts_plan'].append(concept_plan)
            total_hours += concept_plan['estimated_hours']

        plan['total_estimated_hours'] = total_hours
        required_daily_hours = total_hours / (timeframe_months * 30)
        time_ratio = daily_study_hours / max(required_daily_hours, 0.5)
        plan['success_probability'] = min(0.95, 0.5 + (time_ratio * 0.4))

        for month in range(1, timeframe_months + 1):
            milestone = {
                'month': month,
                'target_concepts': len(concepts) * month // timeframe_months,
                'target_score_increase': (target_score - 650) * month // timeframe_months,
                'key_objectives': [
                    f"Maîtriser {3 * month} nouveaux concepts",
                    f"Atteindre {70 + month * 5}% de rétention moyenne",
                    f"Compléter {20 * month} exercices pratiques"
                ]
            }
            plan['milestones'].append(milestone)

        plan['weekly_schedule'] = generate_weekly_schedule(chronotype, daily_study_hours)

        return jsonify({
            'status': 'success',
            'plan': plan,
            'recommendations': {
                'optimal_study_times': get_optimal_times(chronotype),
                'method_effectiveness': get_method_effectiveness(learning_style),
                'adjustment_suggestions': get_adjustment_suggestions(plan)
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Erreur lors de la génération du plan: {str(e)}'}), 500


def calculate_next_review_interval(mastery_level):
    if mastery_level >= 0.9:
        return 30
    elif mastery_level >= 0.7:
        return 14
    elif mastery_level >= 0.5:
        return 7
    elif mastery_level >= 0.3:
        return 3
    else:
        return 1


def generate_progress_recommendations(concept_data):
    recommendations = []
    mastery = concept_data['mastery_level']
    retention = concept_data['retention_rate']
    if mastery < 0.5:
        recommendations.append("Niveau de maîtrise faible. Recommandé de revoir les bases.")
    if retention < 0.6:
        recommendations.append("Taux de rétention faible. Augmentez la fréquence des révisions.")
    if mastery > 0.8 and retention > 0.8:
        recommendations.append("Excellente progression ! Vous pouvez passer au concept suivant.")
    return recommendations


@analysis_bp.route('/update-progress', methods=['POST'])
def update_progress():
    try:
        data = request.get_json() or {}
        concept_id = data.get('concept_id')
        mastery_level = data.get('mastery_level', 0)
        retention_rate = data.get('retention_rate', 0)
        time_spent = data.get('time_spent', 0)

        updated_concept = {
            'concept_id': concept_id,
            'mastery_level': mastery_level,
            'retention_rate': retention_rate,
            'time_spent': time_spent,
            'last_updated': datetime.now().isoformat(),
            'next_review': (datetime.now() + timedelta(days=calculate_next_review_interval(mastery_level))).isoformat()
        }

        return jsonify({
            'status': 'success',
            'updated_concept': updated_concept,
            'recommendations': generate_progress_recommendations(updated_concept)
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Erreur lors de la mise à jour: {str(e)}'}), 500
