"""
API pour l'analyse de documents avec OCR et NLP
===============================================

@author: EULOGE MABIALA & Manus AI
@description: API pour l'analyse sémantique de documents
@version: 2.0.0
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import random
from flask_jwt_extended import jwt_required
from src.utils.ocr import extract_text_from_image
from src.utils.nlp import extract_concepts, analyze_sentiment

analysis_bp = Blueprint("analysis", __name__)


# Simulation d'analyse OCR et NLP
def simulate_ocr_analysis(file_content, file_type):
    """Simule l'analyse OCR d'un document"""

    # Concepts TOEIC typiques pour la simulation
    toeic_concepts = [
        {
            "name": "Conditional Sentences",
            "difficulty": "high",
            "importance": 0.9,
            "category": "grammar",
            "description": "Structures conditionnelles (if, unless, provided that)",
            "examples": [
                "If I were you, I would study harder",
                "Unless you practice, you won't improve",
            ],
        },
        {
            "name": "Business Vocabulary",
            "difficulty": "medium",
            "importance": 0.8,
            "category": "vocabulary",
            "description": "Vocabulaire professionnel et commercial",
            "examples": ["quarterly report", "market analysis", "stakeholder meeting"],
        },
        {
            "name": "Past Perfect Tense",
            "difficulty": "medium",
            "importance": 0.7,
            "category": "grammar",
            "description": "Temps du passé composé et plus-que-parfait",
            "examples": [
                "I had finished before he arrived",
                "She had been working there for years",
            ],
        },
        {
            "name": "Listening Comprehension",
            "difficulty": "high",
            "importance": 0.9,
            "category": "skill",
            "description": "Compréhension orale et reconnaissance des accents",
            "examples": [
                "Phone conversations",
                "Business presentations",
                "Announcements",
            ],
        },
        {
            "name": "Reading Speed",
            "difficulty": "medium",
            "importance": 0.8,
            "category": "skill",
            "description": "Vitesse de lecture et compréhension rapide",
            "examples": [
                "Skimming techniques",
                "Scanning for information",
                "Time management",
            ],
        },
    ]

    # Sélection aléatoire de concepts selon le type de fichier
    num_concepts = random.randint(3, 6)
    selected_concepts = random.sample(toeic_concepts, num_concepts)

    return {
        "extracted_text": f"Contenu simulé extrait du fichier {file_type}...",
        "concepts": selected_concepts,
        "word_count": random.randint(500, 2000),
        "reading_level": random.choice(["intermediate", "advanced", "expert"]),
        "estimated_study_time": random.randint(30, 180),  # minutes
    }


def generate_exercises(concepts):
    """Génère des exercices basés sur les concepts identifiés"""
    exercises = []

    for concept in concepts:
        concept_exercises = {"concept": concept["name"], "exercises": []}

        # Flashcards
        concept_exercises["exercises"].append(
            {
                "type": "flashcard",
                "count": random.randint(10, 25),
                "description": f"Cartes mémoire pour {concept['name']}",
                "estimated_time": random.randint(10, 20),
            }
        )

        # Quiz
        concept_exercises["exercises"].append(
            {
                "type": "quiz",
                "count": random.randint(5, 15),
                "description": f"Quiz à choix multiples sur {concept['name']}",
                "estimated_time": random.randint(15, 30),
            }
        )

        # Exercices pratiques
        if concept["category"] == "grammar":
            concept_exercises["exercises"].append(
                {
                    "type": "grammar_practice",
                    "count": random.randint(8, 20),
                    "description": f"Exercices de grammaire pour {concept['name']}",
                    "estimated_time": random.randint(20, 40),
                }
            )
        elif concept["category"] == "vocabulary":
            concept_exercises["exercises"].append(
                {
                    "type": "vocabulary_practice",
                    "count": random.randint(15, 30),
                    "description": f"Exercices de vocabulaire pour {concept['name']}",
                    "estimated_time": random.randint(15, 35),
                }
            )
        elif concept["category"] == "skill":
            concept_exercises["exercises"].append(
                {
                    "type": "skill_practice",
                    "count": random.randint(5, 12),
                    "description": f"Exercices de compétence pour {concept['name']}",
                    "estimated_time": random.randint(25, 45),
                }
            )

        exercises.append(concept_exercises)

    return exercises


def detect_fuzzy_areas(concepts, text_analysis):
    """Détecte les zones nécessitant une attention particulière"""
    fuzzy_areas = []

    for concept in concepts:
        if concept["difficulty"] == "high":
            fuzzy_areas.append(
                {
                    "concept": concept["name"],
                    "issue": "Complexité élevée",
                    "suggestion": f"Recommandé de commencer par des exemples simples pour {concept['name']}",
                    "priority": "high",
                }
            )

        if concept["importance"] > 0.8 and concept["difficulty"] == "medium":
            fuzzy_areas.append(
                {
                    "concept": concept["name"],
                    "issue": "Concept crucial",
                    "suggestion": f"Prévoir du temps supplémentaire pour maîtriser {concept['name']}",
                    "priority": "medium",
                }
            )

    # Ajout de suggestions générales
    if text_analysis["reading_level"] == "expert":
        fuzzy_areas.append(
            {
                "concept": "Niveau général",
                "issue": "Contenu avancé",
                "suggestion": "Prévoir des sessions de révision fréquentes pour ce niveau",
                "priority": "medium",
            }
        )

    return fuzzy_areas


def generate_spaced_repetition_schedule(concept_name):
    """Génère un planning de répétition espacée pour un concept"""
    now = datetime.now()

    intervals = [1, 3, 7, 14, 30, 60]  # jours
    schedule = []

    for i, interval in enumerate(intervals):
        review_date = now + timedelta(days=interval)
        schedule.append(
            {
                "review_number": i + 1,
                "interval_days": interval,
                "scheduled_date": review_date.isoformat(),
                "completed": False,
                "confidence_required": 0.7 + (i * 0.05),  # Augmente avec les révisions
            }
        )

    return schedule


@analysis_bp.route("/analyze-document", methods=["POST"])
def analyze_document():
    """Analyse un document uploadé"""
    try:
        if "file" not in request.files:
            return jsonify({"status": "error", "message": "Aucun fichier fourni"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"status": "error", "message": "Nom de fichier vide"}), 400

        # Informations sur le fichier
        file_info = {
            "name": file.filename,
            "size": len(file.read()),
            "type": file.content_type,
        }
        file.seek(0)  # Reset file pointer

        # Real Analysis
        extracted_text = ""

        # Reset file pointer
        file.seek(0)

        if file.content_type.startswith("image/"):
            extracted_text = extract_text_from_image(file)
        elif file.content_type == "text/plain":
            extracted_text = file.read().decode("utf-8", errors="ignore")
        else:
            # Fallback for PDF/Docx (using simulation for non-supported types for now)
            file_content = file.read()
            sim_result = simulate_ocr_analysis(file_content, file_info["type"])
            extracted_text = sim_result["extracted_text"]
            analysis_result = sim_result  # Use full simulation result

        # NLP Analysis if we have real text (and not just simulation)
        if file.content_type.startswith("image/") or file.content_type == "text/plain":
            if not extracted_text.strip():
                extracted_text = "No readable text found in document."

            raw_concepts = extract_concepts(extracted_text)

            # Enrich concepts with defaults for compatibility
            enriched_concepts = []
            for c in raw_concepts:
                enriched_concepts.append(
                    {
                        "name": c["name"],
                        "difficulty": "medium",
                        "importance": 0.7,
                        "category": "vocabulary",
                        "description": f"Extracted concept: {c['name']}",
                        "examples": [f"Usage of {c['name']}..."],
                    }
                )

            # If NLP failed to find concepts, fallback to some defaults
            if not enriched_concepts:
                enriched_concepts = simulate_ocr_analysis(None, "fallback")["concepts"]

            analysis_result = {
                "extracted_text": extracted_text,
                "concepts": enriched_concepts,
                "word_count": len(extracted_text.split()),
                "reading_level": analyze_sentiment(extracted_text),
                "estimated_study_time": max(5, len(extracted_text.split()) // 50),
            }

        # Génération d'exercices
        exercises = generate_exercises(analysis_result["concepts"])

        # Détection des zones floues
        fuzzy_areas = detect_fuzzy_areas(analysis_result["concepts"], analysis_result)

        # Génération des plannings de répétition espacée
        spaced_repetition = {}
        for concept in analysis_result["concepts"]:
            spaced_repetition[concept["name"]] = generate_spaced_repetition_schedule(
                concept["name"]
            )

        # Calcul des métriques globales
        total_exercises = sum(len(ex["exercises"]) for ex in exercises)
        total_study_time = sum(
            sum(exercise["estimated_time"] for exercise in ex["exercises"])
            for ex in exercises
        )

        response = {
            "status": "success",
            "file_info": file_info,
            "analysis": {
                "extracted_text": analysis_result["extracted_text"][:500]
                + "...",  # Tronqué
                "concepts": analysis_result["concepts"],
                "word_count": analysis_result["word_count"],
                "reading_level": analysis_result["reading_level"],
                "estimated_study_time": analysis_result["estimated_study_time"],
            },
            "generated_content": {
                "exercises": exercises,
                "total_exercises": total_exercises,
                "total_study_time": total_study_time,
                "fuzzy_areas": fuzzy_areas,
                "spaced_repetition": spaced_repetition,
            },
            "recommendations": {
                "priority_concepts": [
                    c["name"]
                    for c in analysis_result["concepts"]
                    if c["importance"] > 0.8
                ],
                "difficulty_order": sorted(
                    analysis_result["concepts"],
                    key=lambda x: x["importance"],
                    reverse=True,
                ),
                "estimated_completion_weeks": max(
                    1, total_study_time // (7 * 60)
                ),  # Basé sur 1h/jour
            },
            "timestamp": datetime.now().isoformat(),
        }

        return jsonify(response)

    except Exception as e:
        return jsonify(
            {"status": "error", "message": f"Erreur lors de l'analyse: {str(e)}"}
        ), 500


@analysis_bp.route("/generate-plan", methods=["POST"])
@jwt_required()
def generate_adaptive_plan():
    """Génère un plan d'apprentissage adaptatif"""
    try:
        data = request.get_json()

        # Paramètres requis
        target_score = data.get("target_score", 800)
        timeframe_months = data.get("timeframe_months", 3)
        daily_study_hours = data.get("daily_study_hours", 2)
        learning_style = data.get("learning_style", "mixed")
        chronotype = data.get("chronotype", "intermediate")
        concepts = data.get("concepts", [])

        # Génération du plan adaptatif
        plan = {
            "id": f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "target_score": target_score,
            "timeframe_months": timeframe_months,
            "daily_study_hours": daily_study_hours,
            "learning_style": learning_style,
            "chronotype": chronotype,
            "created_at": datetime.now().isoformat(),
            "concepts_plan": [],
            "weekly_schedule": {},
            "milestones": [],
            "success_probability": 0.0,
            "total_estimated_hours": 0,
        }

        # Planification des concepts
        total_hours = 0
        for i, concept in enumerate(concepts):
            concept_plan = {
                "name": concept.get("name", f"Concept {i + 1}"),
                "priority": i + 1,
                "difficulty": concept.get("difficulty", "medium"),
                "importance": concept.get("importance", 0.5),
                "estimated_hours": random.randint(10, 40),
                "weekly_hours": random.randint(2, 8),
                "methods": get_methods_for_style(learning_style),
                "spaced_repetition": generate_spaced_repetition_schedule(
                    concept.get("name", f"Concept {i + 1}")
                ),
                "exercises_count": random.randint(20, 50),
                "mastery_criteria": {
                    "theoretical_understanding": 0.8,
                    "practical_application": 0.7,
                    "long_term_retention": 0.8,
                    "transfer_ability": 0.6,
                    "teaching_capability": 0.5,
                },
            }
            plan["concepts_plan"].append(concept_plan)
            total_hours += concept_plan["estimated_hours"]

        plan["total_estimated_hours"] = total_hours

        # Calcul de la probabilité de succès
        required_daily_hours = total_hours / (timeframe_months * 30)
        time_ratio = daily_study_hours / max(required_daily_hours, 0.5)
        plan["success_probability"] = min(0.95, 0.5 + (time_ratio * 0.4))

        # Génération des jalons mensuels
        for month in range(1, timeframe_months + 1):
            milestone = {
                "month": month,
                "target_concepts": len(concepts) * month // timeframe_months,
                "target_score_increase": (target_score - 650)
                * month
                // timeframe_months,
                "key_objectives": [
                    f"Maîtriser {3 * month} nouveaux concepts",
                    f"Atteindre {70 + month * 5}% de rétention moyenne",
                    f"Compléter {20 * month} exercices pratiques",
                ],
            }
            plan["milestones"].append(milestone)

        # Planning hebdomadaire basé sur le chronotype
        plan["weekly_schedule"] = generate_weekly_schedule(
            chronotype, daily_study_hours
        )

        return jsonify(
            {
                "status": "success",
                "plan": plan,
                "recommendations": {
                    "optimal_study_times": get_optimal_times(chronotype),
                    "method_effectiveness": get_method_effectiveness(learning_style),
                    "adjustment_suggestions": get_adjustment_suggestions(plan),
                },
            }
        )

    except Exception as e:
        return jsonify(
            {
                "status": "error",
                "message": f"Erreur lors de la génération du plan: {str(e)}",
            }
        ), 500


def get_methods_for_style(learning_style):
    """Retourne les méthodes optimales pour un style d'apprentissage"""
    methods_map = {
        "visual": [
            "Dual Coding",
            "Méthode des Lieux",
            "Cartes Conceptuelles",
            "Visualisations",
        ],
        "auditory": [
            "Technique Feynman",
            "Répétition Orale",
            "Podcasts Éducatifs",
            "Discussions",
        ],
        "kinesthetic": [
            "Apprentissage Actif",
            "Simulations",
            "Exercices Pratiques",
            "Jeux de rôle",
        ],
        "mixed": [
            "Approche Multimodale",
            "Rotation des Méthodes",
            "Adaptation Contextuelle",
            "Personnalisation IA",
        ],
    }
    return methods_map.get(learning_style, methods_map["mixed"])


def generate_weekly_schedule(chronotype, daily_hours):
    """Génère un planning hebdomadaire optimisé"""
    schedules = {
        "morning": {
            "monday": {"deep_work": "8h30-10h30", "review": "14h-15h"},
            "tuesday": {"deep_work": "8h30-10h30", "practice": "14h-15h30"},
            "wednesday": {"review": "8h30-9h30", "consolidation": "14h-15h"},
            "thursday": {"deep_work": "8h30-10h30", "application": "14h-15h30"},
            "friday": {"practice": "8h30-10h", "review": "14h-15h"},
            "saturday": {"flexible": "9h-11h", "assessment": "14h-14h30"},
            "sunday": {"rest": "Repos ou révision légère"},
        },
        "intermediate": {
            "monday": {"deep_work": "10h30-12h30", "review": "15h30-16h30"},
            "tuesday": {"deep_work": "10h30-12h30", "practice": "15h30-17h"},
            "wednesday": {"review": "10h30-11h30", "consolidation": "15h30-16h30"},
            "thursday": {"deep_work": "10h30-12h30", "application": "15h30-17h"},
            "friday": {"practice": "10h30-12h", "review": "15h30-16h30"},
            "saturday": {"flexible": "11h-13h", "assessment": "15h30-16h"},
            "sunday": {"rest": "Repos ou révision légère"},
        },
        "evening": {
            "monday": {"deep_work": "11h30-13h30", "review": "17h30-18h30"},
            "tuesday": {"deep_work": "11h30-13h30", "practice": "17h30-19h"},
            "wednesday": {"review": "11h30-12h30", "consolidation": "17h30-18h30"},
            "thursday": {"deep_work": "11h30-13h30", "application": "17h30-19h"},
            "friday": {"practice": "11h30-13h", "review": "17h30-18h30"},
            "saturday": {"flexible": "12h-14h", "assessment": "17h30-18h"},
            "sunday": {"rest": "Repos ou révision légère"},
        },
    }
    return schedules.get(chronotype, schedules["intermediate"])


def get_optimal_times(chronotype):
    """Retourne les heures optimales selon le chronotype"""
    times_map = {
        "morning": ["8h-10h", "14h-16h"],
        "intermediate": ["10h-12h", "15h-17h"],
        "evening": ["11h-13h", "17h-19h"],
    }
    return times_map.get(chronotype, times_map["intermediate"])


def get_method_effectiveness(learning_style):
    """Retourne l'efficacité des méthodes selon le style"""
    effectiveness_map = {
        "visual": 0.85,
        "auditory": 0.80,
        "kinesthetic": 0.75,
        "mixed": 0.90,
    }
    return effectiveness_map.get(learning_style, 0.80)


def get_adjustment_suggestions(plan):
    """Génère des suggestions d'ajustement du plan"""
    suggestions = []

    if plan["success_probability"] < 0.7:
        suggestions.append(
            "Considérez augmenter le temps d'étude quotidien ou étendre la durée du plan"
        )

    if (
        plan["total_estimated_hours"]
        > plan["timeframe_months"] * 30 * plan["daily_study_hours"]
    ):
        suggestions.append(
            "Le plan est ambitieux. Priorisez les concepts les plus importants"
        )

    if len(plan["concepts_plan"]) > 10:
        suggestions.append(
            "Beaucoup de concepts à couvrir. Envisagez de les regrouper par thèmes"
        )

    return suggestions


@analysis_bp.route("/update-progress", methods=["POST"])
def update_progress():
    """Met à jour la progression d'un concept"""
    try:
        data = request.get_json()

        concept_id = data.get("concept_id")
        mastery_level = data.get("mastery_level", 0)
        retention_rate = data.get("retention_rate", 0)
        time_spent = data.get("time_spent", 0)

        # Simulation de mise à jour (en réalité, sauvegarder en base de données)
        updated_concept = {
            "concept_id": concept_id,
            "mastery_level": mastery_level,
            "retention_rate": retention_rate,
            "time_spent": time_spent,
            "last_updated": datetime.now().isoformat(),
            "next_review": (
                datetime.now()
                + timedelta(days=calculate_next_review_interval(mastery_level))
            ).isoformat(),
        }

        return jsonify(
            {
                "status": "success",
                "updated_concept": updated_concept,
                "recommendations": generate_progress_recommendations(updated_concept),
            }
        )

    except Exception as e:
        return jsonify(
            {"status": "error", "message": f"Erreur lors de la mise à jour: {str(e)}"}
        ), 500


def calculate_next_review_interval(mastery_level):
    """Calcule l'intervalle de révision suivant basé sur le niveau de maîtrise"""
    if mastery_level >= 0.9:
        return 30  # 1 mois
    elif mastery_level >= 0.7:
        return 14  # 2 semaines
    elif mastery_level >= 0.5:
        return 7  # 1 semaine
    elif mastery_level >= 0.3:
        return 3  # 3 jours
    else:
        return 1  # 1 jour


def generate_progress_recommendations(concept_data):
    """Génère des recommandations basées sur la progression"""
    recommendations = []

    mastery = concept_data["mastery_level"]
    retention = concept_data["retention_rate"]

    if mastery < 0.5:
        recommendations.append(
            "Niveau de maîtrise faible. Recommandé de revoir les bases."
        )

    if retention < 0.6:
        recommendations.append(
            "Taux de rétention faible. Augmentez la fréquence des révisions."
        )

    if mastery > 0.8 and retention > 0.8:
        recommendations.append(
            "Excellente progression ! Vous pouvez passer au concept suivant."
        )

    return recommendations
