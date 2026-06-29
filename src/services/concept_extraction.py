"""
Service d'extraction de concepts
================================
"""

from src.utils.nlp import extract_concepts


def extract_concepts_from_text(text: str, max_concepts: int = 10) -> list:
    """
    Extrait les concepts clés à partir d'un texte.
    
    Args:
        text (str): Texte brut
        max_concepts (int): Nombre maximum de concepts à extraire
        
    Returns:
        list: Liste de dictionnaires contenant les concepts formatés
    """
    if not text:
        return []

    raw_concepts = extract_concepts(text, max_concepts=max_concepts)
    formatted_concepts = []

    for c in raw_concepts:
        # Calcul heuristique de la confiance en fonction de la pertinence (fréquence)
        relevance = c.get("relevance", 1)
        confidence = min(0.95, 0.5 + (relevance * 0.05))

        formatted_concepts.append({
            "title": c["name"],
            "description": f"Concept '{c['name']}' identifié à partir de l'analyse fréquentielle du texte.",
            "confidence": round(confidence, 2),
            "source": "heuristic"
        })

    return formatted_concepts
