import os
import requests


OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

MODEL = "openai/gpt-oss-20b"


def ask_ai(question: str, sop_context: str = ""):
    """
    Answer a user's question using OpenRouter.

    If SOP context is provided, use it when relevant.
    Otherwise answer as a general AI assistant.
    """

    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        return {
            "success": False,
            "answer": "OpenRouter API key is not configured."
        }

    if not question.strip():
        return {
            "success": False,
            "answer": "Please enter a question."
        }

    if sop_context.strip():

        prompt = f"""
You are an AI assistant inside an application called AI SOP Navigator.

The user has uploaded an SOP document.

Uploaded SOP content:
---------------------
{sop_context}
---------------------

User question:
{question}

Instructions:
1. If the question is related to the uploaded SOP, answer using the SOP.
2. If the question is not related to the SOP, answer it normally using your general knowledge.
3. Never invent information from the SOP.
4. If the SOP does not contain the requested information, clearly say so.
5. Give a clear and concise answer.
"""

    else:

        prompt = f"""
You are a helpful AI assistant.

Answer the user's question clearly and accurately.

User question:
{question}
"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3
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

        answer = (
            data["choices"][0]["message"]["content"]
        )

        return {
            "success": True,
            "answer": answer
        }

    except requests.exceptions.RequestException as error:

        return {
            "success": False,
            "answer": f"AI request failed: {str(error)}"
        }

    except Exception as error:

        return {
            "success": False,
            "answer": f"Unexpected error: {str(error)}"
        }