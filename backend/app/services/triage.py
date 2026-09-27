import json


from google import genai
from google.genai import errors

from ..config import settings
from ..prompts.triage import SYSTEM_PROMPT


class TriageService:
    def __init__(self):
        self.client = (
            genai.Client(api_key=settings.gemini_api_key)
            if settings.gemini_api_key
            else None
        )

    def _fallback(self):
        return {
            "category": "other",
            "priority": "medium",
            "sentiment": "neutral",
            "confidence": 0.0,
            "suggested_team": "Human Review",
            "draft_reply": (
                "Thank you for contacting support. "
                "Your request has been received and will be "
                "reviewed by a human support agent."
            ),
        }

    def classify(self, subject: str, body: str) -> dict:

        # No API key
        if not self.client:
            return self._fallback()

        prompt = f"""
{SYSTEM_PROMPT}

Return ONLY valid JSON. Do not use markdown or code fences.

Ticket:
Subject: {subject}

Body:
{body}
"""

        try:
            response = self.client.models.generate_content(
                model=settings.gemini_model,
                contents=prompt,
            )

            raw = response.text.strip()

            if raw.startswith("```"):
                raw = (
                    raw.replace("```json", "")
                    .replace("```", "")
                    .strip()
                )

            return json.loads(raw)

        except errors.ClientError as exc:
            # Handles 429 quota errors and other Gemini API errors.
            print(f"Gemini API error: {exc}")
            return self._fallback()

        except errors.ServerError as exc:
            # Handles temporary Gemini server failures.
            print(f"Gemini server error: {exc}")
            return self._fallback()

        except json.JSONDecodeError as exc:
            # Gemini returned something that was not valid JSON.
            print(f"Gemini JSON parsing error: {exc}")
            return self._fallback()