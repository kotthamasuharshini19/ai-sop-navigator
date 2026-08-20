import re
from datetime import datetime
from typing import Dict, Optional


# -------------------------------------------------
# VERSION PATTERNS
# -------------------------------------------------

VERSION_PATTERNS = [
    r"\bversion\s*[:\-]?\s*([0-9]+(?:\.[0-9]+)*)",
    r"\bv\s*([0-9]+(?:\.[0-9]+)*)\b",
    r"\brev(?:ision)?\s*[:\-]?\s*([0-9]+(?:\.[0-9]+)*)",
]


# -------------------------------------------------
# DATE PATTERNS
# -------------------------------------------------

DATE_PATTERNS = [

    # 01/01/2024
    r"\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b",

    # 2024-01-01
    r"\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b",

    # January 2024 / August 2026
    r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b",

    # 1 January 2024
    r"\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b",
]


# -------------------------------------------------
# EXTRACT VERSION
# -------------------------------------------------

def extract_version(text: str) -> Optional[str]:

    for pattern in VERSION_PATTERNS:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            return match.group(1)

    return None


# -------------------------------------------------
# EXTRACT DATES
# -------------------------------------------------

def extract_dates(text: str):

    dates = []

    for pattern in DATE_PATTERNS:

        matches = re.findall(
            pattern,
            text,
            re.IGNORECASE
        )

        dates.extend(matches)

    return list(
        dict.fromkeys(dates)
    )


# -------------------------------------------------
# PARSE DATE
# -------------------------------------------------

def parse_date(date_string: str):

    date_string = date_string.strip()

    formats = [

        "%d/%m/%Y",
        "%d-%m-%Y",

        "%Y/%m/%d",
        "%Y-%m-%d",

        "%B %Y",
        "%b %Y",

        "%d %B %Y",
        "%d %b %Y",
    ]

    for fmt in formats:

        try:

            return datetime.strptime(
                date_string,
                fmt
            )

        except ValueError:
            continue

    return None


# -------------------------------------------------
# OUTDATED DETECTION
# -------------------------------------------------

def detect_outdated_status(
    sop_text: str,
    max_age_years: int = 3
) -> Dict:

    version = extract_version(
        sop_text
    )

    date_strings = extract_dates(
        sop_text
    )

    parsed_dates = []

    for date_string in date_strings:

        parsed = parse_date(
            date_string
        )

        if parsed:
            parsed_dates.append(
                parsed
            )

    latest_date = None

    if parsed_dates:

        latest_date = max(
            parsed_dates
        )

    current_date = datetime.now()

    age_years = None

    potentially_outdated = False

    # -------------------------------------------------
    # AGE CALCULATION
    # -------------------------------------------------

    if latest_date:

        age_days = (
            current_date - latest_date
        ).days

        age_years = round(
            age_days / 365.25,
            2
        )

        if age_years > max_age_years:

            potentially_outdated = True

    # -------------------------------------------------
    # RESULT
    # -------------------------------------------------

    if potentially_outdated:

        message = (
            "Potentially outdated SOP detected. "
            "The document may require review or update."
        )

    elif latest_date:

        message = (
            "No obvious outdated indicator detected. "
            "The SOP date is within the configured review period."
        )

    else:

        message = (
            "No date information was detected "
            "to estimate the SOP age."
        )

    return {

        "version": version,

        "dates_found": date_strings,

        "latest_date": (
            latest_date.strftime(
                "%Y-%m-%d"
            )
            if latest_date
            else None
        ),

        "age_years": age_years,

        "potentially_outdated":
            potentially_outdated,

        "message": message
    }


# -------------------------------------------------
# VERSION COMPARISON
# -------------------------------------------------

def compare_versions(
    version_a: str,
    version_b: str
) -> Dict:

    def version_tuple(version):

        numbers = re.findall(
            r"\d+",
            version
        )

        return tuple(
            int(number)
            for number in numbers
        )

    a = version_tuple(
        version_a
    )

    b = version_tuple(
        version_b
    )

    if a > b:
        result = "newer"

    elif a < b:
        result = "older"

    else:
        result = "same"

    return {

        "version_a":
            version_a,

        "version_b":
            version_b,

        "relationship":
            result
    }