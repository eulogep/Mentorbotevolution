"""
API pour les algorithmes de répétition espacée
==============================================

@author: EULOGE MABIALA & Manus AI
@description: API pour la gestion de la répétition espacée adaptative
@version: 2.0.0
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime, timedelta
import math
import random

spaced_repetition_bp = Blueprint('spaced_repetition', __name__)

class SpacedRepetitionAlgorithm:
    """Algorithme de répétition espacée adaptatif"""
    
    def __init__(self):
        # Paramètres de l'algorithme SM-2 modifié
        self.initial_interval = 1  # jour
        self.initial_easiness = 2.5
        self.min_easiness = 1.3
        self.max_easiness = 4.0
        
    def calculate_next_interval(self, current_interval, easiness_factor, quality_response):
        """
        Calcule le prochain intervalle de révision
        
        Args:
            current_interval: Intervalle actuel en jours
            easiness_factor: Facteur de facilité (1.3 - 4.0)
            quality_response: Qualité de la réponse (0-5)
                0: Échec complet
                1: Incorrect avec effort
                2: Incorrect mais familier
                3: Correct avec difficulté
                4: Correct avec hésitation
                5: Correct facilement
        """
        
        # Mise à jour du facteur de facilité
        new_easiness = easiness_factor + (0.1 - (5 - quality_response) * (0.08 + (5 - quality_response) * 0.02))
        new_easiness = max(self.min_easiness, min(self.max_easiness, new_easiness))
        
        # Calcul du nouvel intervalle
        if quality_response < 3:
            # Réponse incorrecte - recommencer
            new_interval = 1
        else:
            if current_interval == 1:
                new_interval = 6
            elif current_interval == 6:
                new_interval = 6 * new_easiness
            else:
                new_interval = current_interval * new_easiness
        
        return max(1, round(new_interval)), new_easiness
    
    def calculate_retention_probability(self, days_since_review, easiness_factor):
        """Calcule la probabilité de rétention basée sur la courbe d'oubli"""
        # Formule basée sur la courbe d'oubli d'Ebbinghaus modifiée
        decay_rate = 1 / easiness_factor
        retention = math.exp(-decay_rate * days_since_review)
        return max(0, min(1, retention))
    
    def get_optimal_review_time(self, last_review, interval, easiness_factor, target_retention=0.8):
        """Détermine le moment optimal pour la révision"""
        days_passed = (datetime.now() - last_review).days
        current_retention = self.calculate_retention_probability(days_passed, easiness_factor)
        
        if current_retention <= target_retention:
            return datetime.now()  # Révision immédiate
        else:
            # Calculer quand la rétention atteindra le seuil cible
            optimal_days = -math.log(target_retention) * easiness_factor
            return last_review + timedelta(days=optimal_days)

@spaced_repetition_bp.route('/create-card', methods=['POST'])
@jwt_required()
def create_spaced_repetition_card():
    """Crée une nouvelle carte de répétition espacée"""
    try:
        data = request.get_json()
        
        card = {
            'id': f"card_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}",
            'concept_name': data.get('concept_name'),
            'content': data.get('content'),
            'difficulty': data.get('difficulty', 'medium'),
            'created_at': datetime.now().isoformat(),
            'last_reviewed': None,
            'next_review': datetime.now().isoformat(),
            'interval': 1,
            'easiness_factor': 2.5,
            'review_count': 0,
            'success_rate': 0.0,
            'average_response_time': 0.0,
            'tags': data.get('tags', []),
            'priority': data.get('priority', 'normal')
        }
        
        return jsonify({
            'status': 'success',
            'card': card,
            'message': 'Carte créée avec succès'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erreur lors de la création: {str(e)}'
        }), 500

@spaced_repetition_bp.route('/review-card', methods=['POST'])
@jwt_required()
def review_card():
    """Traite une révision de carte et calcule le prochain intervalle"""
    try:
        data = request.get_json()
        
        card_id = data.get('card_id')
        quality_response = data.get('quality_response')  # 0-5
        response_time = data.get('response_time', 0)  # secondes
        
        # Récupération des données de la carte (simulation)
        card_data = {
            'id': card_id,
            'interval': data.get('current_interval', 1),
            'easiness_factor': data.get('current_easiness', 2.5),
            'review_count': data.get('review_count', 0),
            'success_rate': data.get('success_rate', 0.0),
            'average_response_time': data.get('average_response_time', 0.0)
        }
        
        # Calcul du nouvel intervalle
        algorithm = SpacedRepetitionAlgorithm()
        new_interval, new_easiness = algorithm.calculate_next_interval(
            card_data['interval'],
            card_data['easiness_factor'],
            quality_response
        )
        
        # Mise à jour des statistiques
        new_review_count = card_data['review_count'] + 1
        success_count = card_data['success_rate'] * card_data['review_count']
        if quality_response >= 3:
            success_count += 1
        new_success_rate = success_count / new_review_count
        
        # Temps de réponse moyen
        total_time = card_data['average_response_time'] * card_data['review_count']
        new_average_time = (total_time + response_time) / new_review_count
        
        # Prochaine date de révision
        next_review_date = datetime.now() + timedelta(days=new_interval)
        
        updated_card = {
            'id': card_id,
            'last_reviewed': datetime.now().isoformat(),
            'next_review': next_review_date.isoformat(),
            'interval': new_interval,
            'easiness_factor': new_easiness,
            'review_count': new_review_count,
            'success_rate': new_success_rate,
            'average_response_time': new_average_time,
            'last_quality': quality_response
        }
        
        # Génération de feedback
        feedback = generate_review_feedback(quality_response, new_interval, new_success_rate)
        
        return jsonify({
            'status': 'success',
            'updated_card': updated_card,
            'feedback': feedback,
            'next_review_in_days': new_interval,
            'retention_probability': algorithm.calculate_retention_probability(0, new_easiness)
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erreur lors de la révision: {str(e)}'
        }), 500

@spaced_repetition_bp.route('/get-due-cards', methods=['GET'])
@jwt_required()
def get_due_cards():
    """Récupère les cartes dues pour révision"""
    try:
        user_id = request.args.get('user_id')
        limit = int(request.args.get('limit', 20))
        
        # Simulation de cartes dues
        due_cards = []
        for i in range(min(limit, random.randint(5, 15))):
            card = {
                'id': f"card_{i+1}",
                'concept_name': f"Concept {i+1}",
                'content': f"Contenu de révision pour le concept {i+1}",
                'next_review': (datetime.now() - timedelta(hours=random.randint(1, 48))).isoformat(),
                'priority': random.choice(['low', 'normal', 'high']),
                'difficulty': random.choice(['easy', 'medium', 'hard']),
                'success_rate': random.uniform(0.3, 0.9),
                'days_overdue': random.randint(0, 5)
            }
            due_cards.append(card)
        
        # Tri par priorité et retard
        due_cards.sort(key=lambda x: (
            {'high': 0, 'normal': 1, 'low': 2}[x['priority']],
            -x['days_overdue']
        ))
        
        return jsonify({
            'status': 'success',
            'due_cards': due_cards,
            'total_due': len(due_cards),
            'estimated_time': len(due_cards) * 2  # 2 minutes par carte
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erreur lors de la récupération: {str(e)}'
        }), 500

@spaced_repetition_bp.route('/get-schedule', methods=['GET'])
@jwt_required()
def get_review_schedule():
    """Génère un planning de révision optimisé"""
    try:
        user_id = request.args.get('user_id')
        days_ahead = int(request.args.get('days_ahead', 7))
        
        schedule = {}
        base_date = datetime.now().date()
        
        for day_offset in range(days_ahead):
            current_date = base_date + timedelta(days=day_offset)
            date_str = current_date.isoformat()
            
            # Simulation du nombre de cartes à réviser chaque jour
            cards_count = random.randint(5, 25)
            estimated_time = cards_count * random.randint(90, 180)  # secondes
            
            schedule[date_str] = {
                'date': date_str,
                'cards_due': cards_count,
                'estimated_time_minutes': estimated_time // 60,
                'difficulty_distribution': {
                    'easy': random.randint(0, cards_count // 3),
                    'medium': random.randint(cards_count // 3, 2 * cards_count // 3),
                    'hard': random.randint(0, cards_count // 3)
                },
                'optimal_times': get_optimal_review_times(current_date),
                'workload': 'light' if cards_count < 10 else 'moderate' if cards_count < 20 else 'heavy'
            }
        
        return jsonify({
            'status': 'success',
            'schedule': schedule,
            'summary': {
                'total_cards': sum(day['cards_due'] for day in schedule.values()),
                'total_time_hours': sum(day['estimated_time_minutes'] for day in schedule.values()) / 60,
                'peak_day': max(schedule.keys(), key=lambda k: schedule[k]['cards_due']),
                'light_days': len([d for d in schedule.values() if d['workload'] == 'light'])
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erreur lors de la génération du planning: {str(e)}'
        }), 500

@spaced_repetition_bp.route('/adaptive-settings', methods=['POST'])
@jwt_required()
def update_adaptive_settings():
    """Met à jour les paramètres adaptatifs de l'algorithme"""
    try:
        data = request.get_json()
        
        user_id = data.get('user_id')
        settings = {
            'target_retention': data.get('target_retention', 0.8),
            'max_daily_cards': data.get('max_daily_cards', 50),
            'preferred_times': data.get('preferred_times', ['09:00', '14:00', '19:00']),
            'difficulty_preference': data.get('difficulty_preference', 'balanced'),
            'learning_style': data.get('learning_style', 'mixed'),
            'break_intervals': data.get('break_intervals', 25),  # minutes
            'session_length': data.get('session_length', 30),  # minutes
            'weekend_study': data.get('weekend_study', True),
            'notification_enabled': data.get('notification_enabled', True)
        }
        
        # Calcul des ajustements recommandés
        recommendations = calculate_adaptive_recommendations(settings)
        
        return jsonify({
            'status': 'success',
            'updated_settings': settings,
            'recommendations': recommendations,
            'estimated_improvement': calculate_estimated_improvement(settings)
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erreur lors de la mise à jour: {str(e)}'
        }), 500

@spaced_repetition_bp.route('/performance-analytics', methods=['GET'])
@jwt_required()
def get_performance_analytics():
    """Fournit des analyses de performance de la répétition espacée"""
    try:
        user_id = request.args.get('user_id')
        period_days = int(request.args.get('period_days', 30))
        
        # Simulation de données analytiques
        analytics = {
            'period_days': period_days,
            'total_reviews': random.randint(100, 500),
            'average_success_rate': random.uniform(0.7, 0.9),
            'average_response_time': random.uniform(3.0, 8.0),  # secondes
            'retention_rate': random.uniform(0.75, 0.95),
            'consistency_score': random.uniform(0.6, 0.9),
            
            'daily_stats': generate_daily_stats(period_days),
            'concept_performance': generate_concept_performance(),
            'difficulty_breakdown': {
                'easy': {'success_rate': random.uniform(0.85, 0.95), 'avg_time': random.uniform(2, 4)},
                'medium': {'success_rate': random.uniform(0.70, 0.85), 'avg_time': random.uniform(4, 7)},
                'hard': {'success_rate': random.uniform(0.50, 0.75), 'avg_time': random.uniform(7, 12)}
            },
            
            'learning_curve': generate_learning_curve(period_days),
            'optimal_intervals': calculate_optimal_intervals(),
            'recommendations': generate_performance_recommendations()
        }
        
        return jsonify({
            'status': 'success',
            'analytics': analytics,
            'insights': generate_insights(analytics)
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erreur lors de l\'analyse: {str(e)}'
        }), 500

def generate_review_feedback(quality_response, new_interval, success_rate):
    """Génère un feedback personnalisé pour la révision"""
    feedback = {
        'message': '',
        'encouragement': '',
        'tips': [],
        'next_action': ''
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
            "Utilisez des techniques de mémorisation"
        ])
        feedback['next_action'] = "Révision rapprochée recommandée"
    
    if success_rate > 0.8:
        feedback['encouragement'] = f"Taux de réussite excellent: {success_rate:.1%}"
    elif success_rate > 0.6:
        feedback['encouragement'] = f"Progression constante: {success_rate:.1%}"
    else:
        feedback['tips'].append("Concentrez-vous sur la compréhension avant la mémorisation")
    
    return feedback

def get_optimal_review_times(date):
    """Retourne les heures optimales de révision pour une date"""
    # Basé sur les recherches en chronobiologie
    return [
        {'time': '09:00', 'effectiveness': 0.9, 'description': 'Pic matinal de concentration'},
        {'time': '14:00', 'effectiveness': 0.8, 'description': 'Après-midi productif'},
        {'time': '19:00', 'effectiveness': 0.7, 'description': 'Révision du soir'}
    ]

def calculate_adaptive_recommendations(settings):
    """Calcule des recommandations adaptatives"""
    recommendations = []
    
    if settings['target_retention'] > 0.9:
        recommendations.append("Rétention cible très élevée. Cela nécessitera plus de révisions.")
    
    if settings['max_daily_cards'] > 40:
        recommendations.append("Limite quotidienne élevée. Assurez-vous de maintenir la qualité.")
    
    if not settings['weekend_study']:
        recommendations.append("Étudier le weekend peut améliorer la rétention de 15%.")
    
    return recommendations

def calculate_estimated_improvement(settings):
    """Calcule l'amélioration estimée avec les nouveaux paramètres"""
    base_improvement = 0.1  # 10% d'amélioration de base
    
    if settings['target_retention'] > 0.8:
        base_improvement += 0.05
    
    if settings['learning_style'] == 'mixed':
        base_improvement += 0.03
    
    if settings['notification_enabled']:
        base_improvement += 0.02
    
    return min(0.3, base_improvement)  # Maximum 30% d'amélioration

def generate_daily_stats(period_days):
    """Génère des statistiques quotidiennes simulées"""
    stats = []
    for i in range(period_days):
        date = (datetime.now() - timedelta(days=period_days - i - 1)).date()
        stats.append({
            'date': date.isoformat(),
            'cards_reviewed': random.randint(0, 30),
            'success_rate': random.uniform(0.6, 0.95),
            'time_spent_minutes': random.randint(10, 60),
            'new_cards': random.randint(0, 5)
        })
    return stats

def generate_concept_performance():
    """Génère des performances par concept"""
    concepts = ['Grammar', 'Vocabulary', 'Listening', 'Reading', 'Writing']
    return [
        {
            'concept': concept,
            'mastery_level': random.uniform(0.4, 0.9),
            'retention_rate': random.uniform(0.6, 0.9),
            'total_reviews': random.randint(20, 100),
            'average_interval': random.uniform(3, 15)
        }
        for concept in concepts
    ]

def generate_learning_curve(period_days):
    """Génère une courbe d'apprentissage"""
    curve = []
    base_performance = 0.5
    for i in range(0, period_days, 3):  # Points tous les 3 jours
        # Simulation d'amélioration progressive avec fluctuations
        performance = base_performance + (i / period_days) * 0.3 + random.uniform(-0.05, 0.05)
        curve.append({
            'day': i,
            'performance': max(0, min(1, performance)),
            'confidence': random.uniform(0.7, 0.95)
        })
    return curve

def calculate_optimal_intervals():
    """Calcule les intervalles optimaux par difficulté"""
    return {
        'easy': [1, 4, 10, 25, 60],
        'medium': [1, 3, 7, 18, 45],
        'hard': [1, 2, 5, 12, 30]
    }

def generate_performance_recommendations():
    """Génère des recommandations de performance"""
    return [
        "Maintenez une régularité dans vos révisions",
        "Concentrez-vous sur les concepts à faible rétention",
        "Utilisez les heures de pic cognitif pour les révisions difficiles",
        "Prenez des pauses régulières pour optimiser la mémorisation"
    ]

def generate_insights(analytics):
    """Génère des insights basés sur les analytics"""
    insights = []
    
    if analytics['average_success_rate'] > 0.8:
        insights.append("Excellente performance globale ! Vous maîtrisez bien la méthode.")
    
    if analytics['consistency_score'] < 0.7:
        insights.append("Votre régularité pourrait être améliorée pour de meilleurs résultats.")
    
    if analytics['retention_rate'] > 0.9:
        insights.append("Taux de rétention exceptionnel ! Votre méthode est très efficace.")
    
    return insights
