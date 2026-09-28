import json

from google import genai
from pydantic import ValidationError

from ..config import settings
from ..prompts.triage import SYSTEM_PROMPT
from ..schemas.ticket import TriageResult


class TriageService:
    def __init__(self):
        self.client = (
            genai.Client(api_key=settings.gemini_api_key)
            if settings.gemini_api_key
            else None
        )

    def _fallback(self) -> dict:
        return {
            "category": "other",
            "priority": "medium",
            "sentiment": "neutral",
            "confidence": 0.0,
            "suggested_team": "Human Review",
            "draft_reply": (
                "Thank you for contacting support. Your request has been "
                "received and will be reviewed by a human support agent."
            ),
        }

    def _parse_and_validate(self, raw: str) -> dict:
        raw = raw.strip()

        # Remove markdown code fences if the model adds them.
        if raw.startswith("```"):
            raw = raw.replace("```json", "", 1)
            raw = raw.replace("```", "", 1).strip()

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return self._fallback()

        try:
            result = TriageResult.model_validate(data)
        except ValidationError:
            return self._fallback()

        return result.model_dump()

    def classify(self, subject: str, body: str) -> dict:
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

            raw = response.text

            if not raw:
                return self._fallback()

            return self._parse_and_validate(raw)

        except Exception:
            return self._fallback()