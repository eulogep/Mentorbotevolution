"""
API pour les algorithmes de répétition espacée
==============================================

@author: EULOGE MABIALA
@description: API pour la gestion de la répétition espacée adaptative avec persistance DB
@version: 2.1.0
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import math

from src.models.user import db, Card, StudySession
from src.services.pipeline_flashcard_import import import_pipeline_flashcards

spaced_repetition_bp = Blueprint('spaced_repetition', __name__)


class SpacedRepetitionAlgorithm:
    """Algorithme de répétition espacée adaptatif (SM-2 modifié)"""

    MIN_EASINESS = 1.3
    MAX_EASINESS = 4.0

    @staticmethod
    def calculate_next_interval(current_interval, easiness_factor, quality_response):
        """
        Calcule le prochain intervalle de révision.

        Args:
            current_interval: Intervalle actuel en jours
            easiness_factor: Facteur de facilité (1.3 - 4.0)
            quality_response: Qualité de la réponse (0-5)
        """
        # Mise à jour du facteur de facilité
        new_easiness = easiness_factor + (
            0.1 - (5 - quality_response) * (0.08 + (5 - quality_response) * 0.02)
        )
        new_easiness = max(
            SpacedRepetitionAlgorithm.MIN_EASINESS,
            min(SpacedRepetitionAlgorithm.MAX_EASINESS, new_easiness),
        )

        # Calcul du nouvel intervalle
        if quality_response < 3:
            new_interval = 1  # Réponse incorrecte — recommencer
        elif current_interval == 1:
            new_interval = 6
        elif current_interval == 6:
            new_interval = 6 * new_easiness
        else:
            new_interval = current_interval * new_easiness

        return max(1, round(new_interval)), new_easiness

    @staticmethod
    def calculate_retention_probability(days_since_review, easiness_factor):
        """Calcule la probabilité de rétention (courbe d'oubli d'Ebbinghaus modifiée)."""
        decay_rate = 1 / easiness_factor
        retention = math.exp(-decay_rate * days_since_review)
        return max(0.0, min(1.0, retention))


# ─── Endpoints ────────────────────────────────────────────────────────────────


@spaced_repetition_bp.route('/create-card', methods=['POST'])
@jwt_required()
def create_spaced_repetition_card():
    """Crée une nouvelle carte de répétition espacée (persistée en DB)."""
    try:
        data = request.get_json()
        user_id = int(get_jwt_identity())

        if not data or not data.get('concept_name'):
            return jsonify({'status': 'error', 'message': 'concept_name is required'}), 400

        card = Card(
            user_id=user_id,
            concept_name=data['concept_name'],
            front_content=data.get('content', data.get('front_content', '')),
            back_content=data.get('back_content', ''),
            difficulty=data.get('difficulty', 'medium'),
            priority=data.get('priority', 'normal'),
            tags=','.join(data.get('tags', [])) if isinstance(data.get('tags'), list) else '',
            next_review=datetime.utcnow(),
        )

        db.session.add(card)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'card': card.to_dict(),
            'message': 'Carte créée avec succès',
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Erreur lors de la création: {str(e)}'}), 500


@spaced_repetition_bp.route('/review-card', methods=['POST'])
@jwt_required()
def review_card():
    """Traite une révision de carte et calcule le prochain intervalle (SM-2)."""
    try:
        data = request.get_json()
        user_id = int(get_jwt_identity())

        card_id = data.get('card_id')
        quality_response = data.get('quality_response')  # 0-5
        response_time = data.get('response_time', 0)     # secondes

        if card_id is None or quality_response is None:
            return jsonify({'status': 'error', 'message': 'card_id and quality_response required'}), 400

        card = Card.query.filter_by(id=card_id, user_id=user_id).first()
        if not card:
            return jsonify({'status': 'error', 'message': 'Card not found'}), 404

        # Calcul SM-2
        algo = SpacedRepetitionAlgorithm()
        new_interval, new_easiness = algo.calculate_next_interval(
            card.interval, card.easiness_factor, quality_response
        )

        # Mise à jour de la carte
        card.interval = new_interval
        card.easiness_factor = new_easiness
        card.review_count += 1
        if quality_response >= 3:
            card.success_count += 1
        card.total_response_time += response_time
        card.last_reviewed = datetime.utcnow()
        card.next_review = datetime.utcnow() + timedelta(days=new_interval)

        db.session.commit()

        # Feedback
        feedback = _generate_review_feedback(quality_response, new_interval, card.success_rate)

        return jsonify({
            'status': 'success',
            'updated_card': card.to_dict(),
            'feedback': feedback,
            'next_review_in_days': new_interval,
            'retention_probability': algo.calculate_retention_probability(0, new_easiness),
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Erreur lors de la révision: {str(e)}'}), 500


@spaced_repetition_bp.route('/get-due-cards', methods=['GET'])
@jwt_required()
def get_due_cards():
    """Récupère les cartes dues pour révision depuis la DB."""
    try:
        user_id = int(get_jwt_identity())
        limit = int(request.args.get('limit', 20))

        due_cards = (
            Card.query
            .filter(Card.user_id == user_id, Card.next_review <= datetime.utcnow())
            .order_by(Card.next_review.asc())
            .limit(limit)
            .all()
        )

        cards_data = [c.to_dict() for c in due_cards]

        return jsonify({
            'status': 'success',
            'due_cards': cards_data,
            'total_due': len(cards_data),
            'estimated_time': len(cards_data) * 2,  # ~2 minutes par carte
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Erreur: {str(e)}'}), 500


@spaced_repetition_bp.route('/get-schedule', methods=['GET'])
@jwt_required()
def get_review_schedule():
    """Génère un planning de révision basé sur les cartes réelles de l'utilisateur."""
    try:
        user_id = int(get_jwt_identity())
        days_ahead = int(request.args.get('days_ahead', 7))

        schedule = {}
        base_date = datetime.utcnow().date()

        for day_offset in range(days_ahead):
            current_date = base_date + timedelta(days=day_offset)
            day_start = datetime.combine(current_date, datetime.min.time())
            day_end = datetime.combine(current_date, datetime.max.time())

            day_cards = (
                Card.query
                .filter(
                    Card.user_id == user_id,
                    Card.next_review >= day_start,
                    Card.next_review <= day_end,
                )
                .all()
            )

            cards_count = len(day_cards)
            date_str = current_date.isoformat()

            schedule[date_str] = {
                'date': date_str,
                'cards_due': cards_count,
                'estimated_time_minutes': cards_count * 2,
                'difficulty_distribution': {
                    'easy': sum(1 for c in day_cards if c.difficulty == 'easy'),
                    'medium': sum(1 for c in day_cards if c.difficulty == 'medium'),
                    'hard': sum(1 for c in day_cards if c.difficulty == 'hard'),
                },
                'workload': 'light' if cards_count < 10 else 'moderate' if cards_count < 20 else 'heavy',
            }

        return jsonify({
            'status': 'success',
            'schedule': schedule,
            'summary': {
                'total_cards': sum(day['cards_due'] for day in schedule.values()),
                'total_time_hours': round(sum(day['estimated_time_minutes'] for day in schedule.values()) / 60, 1),
                'peak_day': max(schedule.keys(), key=lambda k: schedule[k]['cards_due']) if schedule else None,
                'light_days': len([d for d in schedule.values() if d['workload'] == 'light']),
            },
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Erreur: {str(e)}'}), 500


@spaced_repetition_bp.route('/performance-analytics', methods=['GET'])
@jwt_required()
def get_performance_analytics():
    """Fournit des analyses de performance basées sur les données réelles."""
    try:
        user_id = int(get_jwt_identity())
        period_days = int(request.args.get('period_days', 30))

        cutoff = datetime.utcnow() - timedelta(days=period_days)

        # Statistiques depuis les cartes
        all_cards = Card.query.filter_by(user_id=user_id).all()
        reviewed_cards = [c for c in all_cards if c.review_count > 0]

        total_reviews = sum(c.review_count for c in all_cards)
        avg_success = (
            sum(c.success_rate for c in reviewed_cards) / len(reviewed_cards)
            if reviewed_cards else 0.0
        )
        avg_response_time = (
            sum(c.average_response_time for c in reviewed_cards) / len(reviewed_cards)
            if reviewed_cards else 0.0
        )

        # Sessions récentes
        sessions = (
            StudySession.query
            .filter(StudySession.user_id == user_id, StudySession.started_at >= cutoff)
            .order_by(StudySession.started_at.desc())
            .all()
        )

        # Performance par difficulté
        difficulty_breakdown = {}
        for diff in ['easy', 'medium', 'hard']:
            diff_cards = [c for c in reviewed_cards if c.difficulty == diff]
            if diff_cards:
                difficulty_breakdown[diff] = {
                    'success_rate': round(sum(c.success_rate for c in diff_cards) / len(diff_cards), 3),
                    'avg_time': round(sum(c.average_response_time for c in diff_cards) / len(diff_cards), 1),
                    'count': len(diff_cards),
                }
            else:
                difficulty_breakdown[diff] = {'success_rate': 0, 'avg_time': 0, 'count': 0}

        analytics = {
            'period_days': period_days,
            'total_cards': len(all_cards),
            'total_reviews': total_reviews,
            'average_success_rate': round(avg_success, 3),
            'average_response_time': round(avg_response_time, 1),
            'recent_sessions': [s.to_dict() for s in sessions[:10]],
            'difficulty_breakdown': difficulty_breakdown,
        }

        # Insights
        insights = []
        if avg_success > 0.8:
            insights.append("Excellente performance globale ! Vous maîtrisez bien la méthode.")
        elif avg_success > 0.6:
            insights.append("Bonne progression. Continuez à réviser régulièrement.")
        elif total_reviews > 0:
            insights.append("Votre taux de réussite peut être amélioré. Concentrez-vous sur la compréhension.")

        if len(all_cards) == 0:
            insights.append("Créez vos premières cartes pour commencer la répétition espacée !")

        return jsonify({
            'status': 'success',
            'analytics': analytics,
            'insights': insights,
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Erreur: {str(e)}'}), 500


# ─── Helpers ──────────────────────────────────────────────────────────────────


def _generate_review_feedback(quality_response, new_interval, success_rate):
    """Génère un feedback personnalisé pour la révision."""
    feedback = {
        'message': '',
        'encouragement': '',
        'tips': [],
        'next_action': '',
    }

    if quality_response >= 4:
        feedback['message'] = "Excellente réponse ! Votre maîtrise s'améliore."
        feedback['encouragement'] = "Continuez sur cette lancée !"
        feedback['next_action'] = f"Prochaine révision dans {new_interval} jour(s)"
    elif quality_response == 3:
        feedback['message'] = "Bonne réponse avec quelques hésitations."
        feedback['tips'].append("Essayez de réviser plus régulièrement")
        feedback['next_action'] = f"Révision programmée dans {new_interval} jour(s)"
    else:
        feedback['message'] = "Cette notion nécessite plus de travail."
        feedback['tips'].extend([
            "Relisez le cours sur ce concept",
            "Pratiquez avec des exercices supplémentaires",
            "Utilisez des techniques de mémorisation",
        ])
        feedback['next_action'] = "Révision rapprochée recommandée"

    if success_rate > 0.8:
        feedback['encouragement'] = f"Taux de réussite excellent: {success_rate:.1%}"
    elif success_rate > 0.6:
        feedback['encouragement'] = f"Progression constante: {success_rate:.1%}"
    elif success_rate > 0:
        feedback['tips'].append("Concentrez-vous sur la compréhension avant la mémorisation")

    return feedback


@spaced_repetition_bp.route('/import-pipeline-flashcards', methods=['POST'])
@jwt_required()
def import_pipeline_cards():
    """Importe les flashcards du pipeline d'apprentissage pour l'utilisateur connecté."""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json() or {}

        result = import_pipeline_flashcards(user_id, data)
        if result.get("status") == "error":
            return jsonify(result), 400

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Erreur serveur : {str(e)}"}), 500
