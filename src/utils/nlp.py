import re
from collections import Counter

# Basic stop words list (French + English mix as project seems mixed/French context)
STOP_WORDS = set(
    [
        "le",
        "la",
        "les",
        "un",
        "une",
        "des",
        "du",
        "de",
        "d",
        "et",
        "ou",
        "mais",
        "où",
        "est",
        "sont",
        "c",
        "en",
        "à",
        "au",
        "aux",
        "par",
        "pour",
        "sur",
        "dans",
        "avec",
        "sans",
        "ce",
        "se",
        "ces",
        "cet",
        "cette",
        "qui",
        "que",
        "quoi",
        "dont",
        "je",
        "tu",
        "il",
        "elle",
        "nous",
        "vous",
        "ils",
        "elles",
        "a",
        "the",
        "of",
        "and",
        "or",
        "in",
        "on",
        "at",
        "to",
        "for",
        "with",
        "is",
        "are",
        "it",
        "that",
        "this",
    ]
)


def extract_concepts(text, max_concepts=10):
    """
    Extracts key concepts from text using simple frequency analysis and regex patterns.
    Replaces advanced NLP (Spacy) for now.

    Args:
        text (str): Input text.
        max_concepts (int): Maximum number of concepts to return.

    Returns:
        list: List of dicts {'text': word, 'count': n}.
    """
    if not text:
        return []

    # Normalize text
    text = text.lower()

    # 1. Regex Extraction: Look for "Definition of X" or "X: ..." patterns (heuristic)
    # Finds words before a colon that might be definitions
    definition_candidates = re.findall(r"\b([a-zA-Zà-ÿ]{4,})\s*:", text)

    # 2. Frequency Analysis
    # Remove non-word characters
    words = re.findall(r"\b[a-zA-Zà-ÿ]{4,}\b", text)

    # Filter stopwords
    meaningful_words = [w for w in words if w not in STOP_WORDS]

    # Count frequencies
    counter = Counter(meaningful_words)

    # Boost definition candidates in counter
    for cand in definition_candidates:
        if cand in STOP_WORDS:
            continue
        counter[cand] += 3

    # Get most common
    most_common = counter.most_common(max_concepts)

    # Format for API
    concepts = [
        {"name": word.capitalize(), "relevance": count} for word, count in most_common
    ]

    return concepts


def analyze_sentiment(text):
    """
    Basic mock sentiment/difficulty analysis based on length and vocabulary.
    """
    word_count = len(text.split())
    if word_count < 50:
        return "easy"
    elif word_count > 300:
        return "hard"
    return "medium"
