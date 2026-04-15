from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Literal, cast

from google import genai

from src.config.settings import AppSettings
from src.domain.classification import estimate_urgency_from_text
from src.domain.email_entities import ClassifiedEmail, EmailMessage


AllowedCategory = Literal["atividade", "prazo", "aviso", "irrelevante"]


@dataclass(frozen=True)
class ClassificationResult:
    category: AllowedCategory
    justification: str
    confidence: float


def _clamp_confidence(value: float) -> float:
    if value < 0:
        return 0.0
    if value > 1:
        return 1.0
    return value


def _prompt_for(email_message: EmailMessage) -> str:
    return f"""
Classifique este e-mail acadêmico em exatamente uma categoria:
- atividade
- prazo
- aviso
- irrelevante

Retorne JSON estrito sem markdown:
{{
  "category": "atividade|prazo|aviso|irrelevante",
  "justification": "texto curto em português",
  "confidence": 0.0
}}

Assunto: {email_message.subject}
Remetente: {email_message.from_email}
Corpo:
{email_message.body_text[:1800]}
""".strip()


def _parse_result(response_text: str) -> ClassificationResult:
    parsed = json.loads(response_text)
    category_raw = str(parsed.get("category", "")).strip().lower()
    if category_raw not in {"atividade", "prazo", "aviso", "irrelevante"}:
        raise ValueError("Invalid category")
    justification = str(parsed.get("justification", "")).strip() or "Classificacao padrao por ausencia de justificativa."
    confidence = _clamp_confidence(float(parsed.get("confidence", 0.6)))
    return ClassificationResult(
        category=cast(AllowedCategory, category_raw),
        justification=justification,
        confidence=confidence,
    )


class GeminiEmailClassifier:
    def __init__(self, settings: AppSettings) -> None:
        self._client = genai.Client(api_key=settings.gemini_api_key)
        self._model = settings.gemini_model

    def classify(self, email_message: EmailMessage) -> ClassifiedEmail:
        baseline_urgency = estimate_urgency_from_text(f"{email_message.subject}\n{email_message.body_text}")
        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=_prompt_for(email_message),
            )
            response_text = response.text or ""
            if not response_text:
                raise ValueError("Empty model response")
            parsed = _parse_result(response_text)
            urgency_score = max(
                baseline_urgency,
                80 if parsed.category == "prazo" else 0,
                70 if parsed.category == "atividade" and baseline_urgency >= 50 else 0,
            )
            return ClassifiedEmail(
                email=email_message,
                category=parsed.category,
                justification=parsed.justification,
                urgency_score=urgency_score,
                confidence=parsed.confidence,
            )
        except Exception:
            return ClassifiedEmail(
                email=email_message,
                category="aviso",
                justification="Fallback por falha temporaria da IA.",
                urgency_score=baseline_urgency,
                confidence=0.4,
            )
