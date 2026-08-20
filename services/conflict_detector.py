import re
from typing import List, Dict


# -------------------------------------------------
# NORMALIZATION
# -------------------------------------------------

def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def get_words(text: str) -> set:
    return set(normalize_text(text).split())


# -------------------------------------------------
# NEGATION
# -------------------------------------------------

NEGATION_WORDS = {
    "not",
    "no",
    "never",
    "without",
    "cannot",
    "can't",
    "must not",
    "do not",
    "does not",
    "should not",
    "shall not",
    "prohibited",
    "forbidden"
}


def contains_negation(text: str) -> bool:

    normalized = normalize_text(text)

    return any(
        phrase in normalized
        for phrase in NEGATION_WORDS
    )


# -------------------------------------------------
# SIMILARITY
# -------------------------------------------------

def similarity_score(
    text_a: str,
    text_b: str
) -> float:

    words_a = get_words(text_a)
    words_b = get_words(text_b)

    if not words_a or not words_b:
        return 0.0

    common = words_a.intersection(words_b)

    score = (
        len(common)
        / min(len(words_a), len(words_b))
    ) * 100

    return round(
        min(score, 100.0),
        2
    )


# -------------------------------------------------
# TIME / DEADLINE CONFLICT
# -------------------------------------------------

def extract_time_rule(text: str):

    normalized = normalize_text(text)

    # Immediate reporting
    if any(word in normalized for word in [
        "immediately",
        "immediate",
        "as soon as possible",
        "right away",
        "at once"
    ]):
        return "immediate"

    # Days
    match = re.search(
        r"(within|after|in)\s+(\d+)\s+days?",
        normalized
    )

    if match:
        return int(match.group(2))

    # Hours
    match = re.search(
        r"(within|after|in)\s+(\d+)\s+hours?",
        normalized
    )

    if match:
        return int(match.group(2)) / 24

    return None


# -------------------------------------------------
# IMPORTANT TOPIC WORDS
# -------------------------------------------------

def extract_topic_words(text: str) -> set:

    words = get_words(text)

    stop_words = {
        "the", "a", "an", "is", "are",
        "was", "were", "must", "should",
        "shall", "will", "may", "can",
        "be", "to", "and", "or", "of",
        "in", "on", "for", "with",
        "within", "immediately"
    }

    return {
        word
        for word in words
        if word not in stop_words
        and len(word) > 2
    }


# -------------------------------------------------
# CONFLICT DETECTION
# -------------------------------------------------

def detect_conflict(
    statement_a: str,
    statement_b: str
) -> Dict:

    if (
        not statement_a.strip()
        or not statement_b.strip()
    ):
        return {
            "conflict": False,
            "confidence": 0,
            "reason": "One or both statements are empty."
        }

    similarity = similarity_score(
        statement_a,
        statement_b
    )

    negation_a = contains_negation(
        statement_a
    )

    negation_b = contains_negation(
        statement_b
    )

    topic_a = extract_topic_words(
        statement_a
    )

    topic_b = extract_topic_words(
        statement_b
    )

    common_topics = (
        topic_a.intersection(topic_b)
    )

    # ---------------------------------------------
    # CASE 1: Same topic + opposite negation
    # ---------------------------------------------

    if (
        similarity >= 30
        and negation_a != negation_b
    ):

        return {
            "conflict": True,
            "confidence": round(
                min(similarity + 25, 100),
                2
            ),
            "reason": (
                "The statements address the same "
                "topic but contain opposing instructions."
            ),
            "statement_a": statement_a,
            "statement_b": statement_b
        }

    # ---------------------------------------------
    # CASE 2: Same topic + different deadlines
    # ---------------------------------------------

    time_a = extract_time_rule(
        statement_a
    )

    time_b = extract_time_rule(
        statement_b
    )

    if (
        common_topics
        and time_a is not None
        and time_b is not None
    ):

        if time_a != time_b:

            return {
                "conflict": True,
                "confidence": 90,
                "reason": (
                    "The statements address the same "
                    "topic but specify different "
                    "reporting deadlines."
                ),
                "statement_a": statement_a,
                "statement_b": statement_b
            }

    # ---------------------------------------------
    # CASE 3: Immediate vs fixed deadline
    # ---------------------------------------------

    if (
        common_topics
        and (
            time_a == "immediate"
            or time_b == "immediate"
        )
        and time_a != time_b
    ):

        return {
            "conflict": True,
            "confidence": 92,
            "reason": (
                "One statement requires immediate "
                "action while the other provides "
                "a different time period."
            ),
            "statement_a": statement_a,
            "statement_b": statement_b
        }

    # ---------------------------------------------
    # No conflict
    # ---------------------------------------------

    return {
        "conflict": False,
        "confidence": round(
            similarity,
            2
        ),
        "reason": (
            "No obvious contradiction was detected."
        ),
        "statement_a": statement_a,
        "statement_b": statement_b
    }


# -------------------------------------------------
# FIND CONFLICTS
# -------------------------------------------------

def find_conflicts(
    statements: List[str]
) -> List[Dict]:

    conflicts = []

    for i in range(
        len(statements)
    ):

        for j in range(
            i + 1,
            len(statements)
        ):

            result = detect_conflict(
                statements[i],
                statements[j]
            )

            if result["conflict"]:

                result[
                    "statement_a_index"
                ] = i

                result[
                    "statement_b_index"
                ] = j

                conflicts.append(
                    result
                )

    return conflicts