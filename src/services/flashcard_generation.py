"""
Service de génération de flashcards
===================================
"""


def generate_flashcards_from_concepts(concepts: list) -> list:
    """
    Génère des flashcards heuristiques à partir de concepts extraits.
    
    Args:
        concepts (list): Liste de concepts au format d'extraction
        
    Returns:
        list: Liste de flashcards générées
    """
    flashcards = []

    for c in concepts:
        title = c["title"]
        flashcards.append({
            "concept_name": title,
            "question": f"Qu'est-ce que le concept : '{title}' ?",
            "answer": f"Le concept '{title}' est une notion importante identifiée dans le document. (Description heuristique : {c.get('description', '')})",
            "difficulty": "medium",
            "source": "heuristic"
        })

    return flashcards
