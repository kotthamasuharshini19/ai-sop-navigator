import os
import json
import requests
from typing import Dict

from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# You can change this model later if needed.
MODEL = "openai/gpt-4o-mini"


def detect_gaps(sop_text: str) -> Dict:
    """
    Analyze an SOP using OpenRouter AI and identify
    potentially missing, incomplete, vague, or unclear areas.

    This is an intelligent flagging mechanism.
    It does NOT create official company policies.
    """

    if not sop_text or not sop_text.strip():
        return {
            "gaps_found": True,
            "gap_count": 1,
            "gaps": [
                {
                    "section": "document",
                    "status": "potential_gap",
                    "reason": "No readable SOP content was provided."
                }
            ],
            "weak_areas": []
        }

    if not OPENROUTER_API_KEY:
        return {
            "gaps_found": True,
            "gap_count": 1,
            "gaps": [
                {
                    "section": "configuration",
                    "status": "potential_gap",
                    "reason": "OPENROUTER_API_KEY is not configured."
                }
            ],
            "weak_areas": []
        }

    prompt = f"""
You are an expert SOP document analyst.

Analyze the following Standard Operating Procedure.

Your task is to identify POTENTIAL gaps only.

Look for information that is:
- missing
- incomplete
- ambiguous
- unclear
- insufficiently documented

Consider areas such as:
- purpose
- scope
- responsibilities
- procedure steps
- exceptions
- escalation
- approvals
- timelines
- required documentation
- safety considerations
- roles and ownership
- decision conditions
- reporting requirements

IMPORTANT:
Do NOT assume that every SOP must contain every possible section.

Only flag something when there is a reasonable indication that
important procedural information is missing or unclear.

Do NOT create official policies.
Do NOT invent requirements.
Do NOT claim legal or regulatory non-compliance.

Return ONLY valid JSON in this format:

{{
  "gaps_found": true,
  "gap_count": 2,
  "gaps": [
    {{
      "section": "Escalation",
      "status": "potential_gap",
      "reason": "The SOP does not clearly explain what should happen when the normal procedure cannot resolve the issue.",
      "evidence": "No escalation responsibility or escalation path is specified.",
      "severity": "medium"
    }}
  ],
  "weak_areas": [
    {{
      "type": "potentially_vague_instruction",
      "phrase": "appropriate action",
      "reason": "The instruction does not define what action should be taken."
    }}
  ],
  "summary": "The SOP is generally structured but contains some areas that may require clarification."
}}

If no meaningful gaps are found, return:

{{
  "gaps_found": false,
  "gap_count": 0,
  "gaps": [],
  "weak_areas": [],
  "summary": "No significant potential gaps were identified."
}}

SOP CONTENT:

{sop_text}
"""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a precise SOP gap detection assistant. "
                    "Return only valid JSON."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.1,
        "max_tokens": 1500
    }

    try:

        response = requests.post(
            OPENROUTER_URL,
            headers=headers,
            json=payload,
            timeout=60
        )

        response.raise_for_status()

        data = response.json()

        content = (
            data["choices"][0]["message"]["content"]
            .strip()
        )

        # Remove markdown code fences if the model returns them.
        if content.startswith("```"):
            content = content.replace("```json", "")
            content = content.replace("```", "")
            content = content.strip()

        result = json.loads(content)

        # Make sure required fields exist.
        result.setdefault(
            "gaps_found",
            False
        )

        result.setdefault(
            "gap_count",
            len(result.get("gaps", []))
        )

        result.setdefault(
            "gaps",
            []
        )

        result.setdefault(
            "weak_areas",
            []
        )

        result.setdefault(
            "summary",
            "Analysis completed."
        )

        return result

    except requests.exceptions.RequestException as error:

        return {
            "gaps_found": False,
            "gap_count": 0,
            "gaps": [],
            "weak_areas": [],
            "summary": (
                "Unable to connect to the AI service. "
                f"Error: {str(error)}"
            )
        }

    except json.JSONDecodeError:

        return {
            "gaps_found": False,
            "gap_count": 0,
            "gaps": [],
            "weak_areas": [],
            "summary": (
                "The AI returned an unexpected response format."
            )
        }

    except Exception as error:

        return {
            "gaps_found": False,
            "gap_count": 0,
            "gaps": [],
            "weak_areas": [],
            "summary": (
                f"Gap analysis failed: {str(error)}"
            )
        }