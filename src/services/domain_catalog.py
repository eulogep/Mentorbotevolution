"""Catalogue transparent des modèles de parcours multi-domaines.

Les modèles fournissent seulement une structure initiale que l'utilisateur choisit
explicitement. Ils ne sont ni une analyse de niveau, ni une recommandation
personnalisée, ni une certification de compétence.
"""

DOMAIN_OPTIONS = {
    "language": "Langues",
    "computing": "Informatique",
    "productivity": "Bureautique",
    "data": "Données et visualisation",
    "infrastructure": "Réseau et systèmes",
    "security": "Cybersécurité",
    "general": "Parcours libre",
}

PROGRAM_TEMPLATES = [
    {
        "id": "toeic-foundations",
        "title": "Préparation TOEIC",
        "domain": "language",
        "description": "Parcours pour organiser vocabulaire, grammaire, compréhension orale et lecture autour d’un objectif d’examen déclaré.",
        "objective_type": "exam_score",
        "objective_label": "Score TOEIC visé",
        "source": "editorial_template",
        "practice_types": ["recall", "explanation", "listening", "timed_reading"],
        "concepts": [
            {"name": "Grammaire et structures de phrase", "competency_type": "knowledge", "evidence_criterion": "Expliquer et appliquer une structure dans une phrase nouvelle."},
            {"name": "Vocabulaire professionnel", "competency_type": "knowledge", "evidence_criterion": "Employer le terme correctement dans un contexte professionnel."},
            {"name": "Compréhension orale", "competency_type": "diagnostic", "evidence_criterion": "Identifier l’information clé et justifier la réponse."},
            {"name": "Lecture et gestion du temps", "competency_type": "procedure", "evidence_criterion": "Repérer des informations pertinentes dans un texte chronométré."},
        ],
    },
    {
        "id": "computing-foundations",
        "title": "Fondamentaux de l’informatique",
        "domain": "computing",
        "description": "Parcours transversal pour comprendre les principes de calcul, données, systèmes, réseau et sécurité avant de se spécialiser.",
        "objective_type": "competency",
        "objective_label": "Compétence visée",
        "source": "editorial_template",
        "practice_types": ["recall", "explanation", "diagnostic", "practice"],
        "concepts": [
            {"name": "Représentation des données", "competency_type": "knowledge", "evidence_criterion": "Expliquer comment texte, nombres et fichiers sont représentés et stockés."},
            {"name": "Algorithmique et décomposition", "competency_type": "procedure", "evidence_criterion": "Décomposer un problème simple en étapes ordonnées et testables."},
            {"name": "Systèmes d’exploitation et processus", "competency_type": "knowledge", "evidence_criterion": "Décrire le rôle du système d’exploitation, d’un processus et de la mémoire."},
            {"name": "Réseaux et protocoles", "competency_type": "diagnostic", "evidence_criterion": "Expliquer le chemin général d’une requête et isoler une cause probable de panne simple."},
            {"name": "Hygiène numérique et sécurité de base", "competency_type": "procedure", "evidence_criterion": "Justifier des mesures de protection de compte et reconnaître un risque courant."},
        ],
    },
    {
        "id": "excel-foundations",
        "title": "Excel — fondamentaux",
        "domain": "productivity",
        "description": "Parcours de structuration, calcul, analyse et communication avec des feuilles de calcul.",
        "objective_type": "competency",
        "objective_label": "Compétence visée",
        "source": "editorial_template",
        "practice_types": ["recall", "practice", "production"],
        "concepts": [],
    },
    {
        "id": "powerbi-foundations",
        "title": "Power BI — fondamentaux",
        "domain": "data",
        "description": "Parcours de préparation des données, modélisation et visualisation de tableaux de bord.",
        "objective_type": "competency",
        "objective_label": "Compétence visée",
        "source": "editorial_template",
        "practice_types": ["recall", "practice", "production"],
        "concepts": [],
    },
    {
        "id": "network-foundations",
        "title": "Réseau — fondamentaux",
        "domain": "infrastructure",
        "description": "Parcours de compréhension des équipements, protocoles, adressage et dépannage de base.",
        "objective_type": "competency",
        "objective_label": "Compétence visée",
        "source": "editorial_template",
        "practice_types": ["recall", "explanation", "diagnostic", "practice"],
        "concepts": [],
    },
    {
        "id": "cybersecurity-foundations",
        "title": "Cybersécurité — fondamentaux",
        "domain": "security",
        "description": "Parcours défensif fondé sur la sécurité des comptes, les risques, la détection et les pratiques en environnement autorisé.",
        "objective_type": "competency",
        "objective_label": "Compétence visée",
        "source": "editorial_template",
        "practice_types": ["recall", "explanation", "diagnostic", "practice"],
        "concepts": [],
    },
]


def public_catalog() -> list[dict]:
    """Return safe-to-display template metadata without mutable references."""
    templates = []
    for template in PROGRAM_TEMPLATES:
        templates.append({
            "id": template["id"],
            "title": template["title"],
            "domain": template["domain"],
            "domain_label": DOMAIN_OPTIONS[template["domain"]],
            "description": template["description"],
            "objective_type": template["objective_type"],
            "objective_label": template["objective_label"],
            "practice_types": template["practice_types"],
            "concept_count": len(template["concepts"]),
        })
    return templates


def find_template(template_id: str) -> dict | None:
    return next((template for template in PROGRAM_TEMPLATES if template["id"] == template_id), None)
