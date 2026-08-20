import re
from typing import List, Dict


# -------------------------------------------------
# Text Normalization
# -------------------------------------------------

def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# -------------------------------------------------
# Keyword Extraction
# -------------------------------------------------

def extract_keywords(text: str) -> List[str]:

    normalized = normalize_text(text)

    stop_words = {
        "the", "a", "an", "is", "are", "was", "were",
        "what", "how", "when", "where", "why", "can",
        "could", "should", "would", "do", "does", "did",
        "i", "we", "you", "my", "our", "their",
        "for", "to", "of", "in", "on", "and", "or",
        "with", "this", "that", "it", "me", "myself"
    }

    words = normalized.split()

    keywords = [
        word
        for word in words
        if len(word) > 2 and word not in stop_words
    ]

    return list(dict.fromkeys(keywords))


# -------------------------------------------------
# Related Word Groups
# -------------------------------------------------

RELATED_TERMS = {

    "lost": {
        "lost", "loss", "stolen", "missing"
    },

    "laptop": {
        "laptop", "device", "computer", "notebook"
    },

    "password": {
        "password", "credential", "credentials",
        "account", "authentication"
    },

    "security": {
        "security", "secure", "protection",
        "incident"
    },

    "data": {
        "data", "file", "files", "information",
        "confidential", "leakage"
    },

    "software": {
        "software", "application", "app",
        "program", "installation"
    },

    "leave": {
        "leave", "absence", "holiday", "vacation"
    },

    "manager": {
        "manager", "supervisor", "reporting"
    },

    "it": {
        "it", "helpdesk", "help", "technical"
    }
}


# -------------------------------------------------
# Expand Keywords
# -------------------------------------------------

def expand_keywords(keywords: List[str]) -> set:

    expanded = set(keywords)

    for keyword in keywords:

        for group in RELATED_TERMS.values():

            if keyword in group:
                expanded.update(group)

    return expanded


# -------------------------------------------------
# Calculate Match Score
# -------------------------------------------------

def calculate_match_score(
    situation: str,
    sop_chunk: str
) -> float:

    situation_keywords = extract_keywords(
        situation
    )

    chunk_keywords = set(
        extract_keywords(sop_chunk)
    )

    if not situation_keywords or not chunk_keywords:
        return 0.0

    expanded_situation = expand_keywords(
        situation_keywords
    )

    common_keywords = (
        expanded_situation.intersection(
            chunk_keywords
        )
    )

    if not common_keywords:
        return 0.0

    # Score based mainly on user's important words
    original_matches = (
        set(situation_keywords)
        .intersection(chunk_keywords)
    )

    expanded_matches = len(common_keywords)

    original_score = (
        len(original_matches)
        / len(situation_keywords)
    ) * 100

    # Small bonus for related terminology
    related_bonus = min(
        expanded_matches * 5,
        20
    )

    score = min(
        original_score + related_bonus,
        100
    )

    return round(score, 2)


# -------------------------------------------------
# Find Best Matching Chunks
# -------------------------------------------------

def match_situation_to_sop(
    situation: str,
    chunks: List[str],
    top_k: int = 3
) -> List[Dict]:

    if not situation.strip():
        return []

    results = []

    for index, chunk in enumerate(chunks):

        if not chunk.strip():
            continue

        score = calculate_match_score(
            situation,
            chunk
        )

        if score > 0:

            results.append({
                "chunk_index": index,
                "score": score,
                "text": chunk
            })

    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return results[:top_k]


# -------------------------------------------------
# Best Match
# -------------------------------------------------

def get_best_match(
    situation: str,
    chunks: List[str]
) -> Dict:

    matches = match_situation_to_sop(
        situation,
        chunks,
        top_k=1
    )

    # No match
    if not matches:

        return {
            "matched": False,
            "score": 0,
            "text": "",
            "chunk_index": -1,
            "message": (
                "No relevant SOP section was found "
                "for this situation."
            )
        }

    best_match = matches[0]

    # Important threshold
    # Very weak matches should NOT be shown
    if best_match["score"] < 40:

        return {
            "matched": False,
            "score": best_match["score"],
            "text": "",
            "chunk_index": best_match["chunk_index"],
            "message": (
                "No sufficiently relevant SOP section "
                "was found for this situation."
            )
        }

    return {
        "matched": True,
        "score": best_match["score"],
        "text": best_match["text"],
        "chunk_index": best_match["chunk_index"],
        "message": (
            "A relevant SOP section was found "
            "for this situation."
        )
    }