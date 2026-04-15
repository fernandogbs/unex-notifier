from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal


EmailCategory = Literal["atividade", "prazo", "aviso", "irrelevante"]


@dataclass(frozen=True)
class EmailMessage:
    message_id: str
    subject: str
    from_email: str
    from_domain: str
    received_at: datetime
    body_text: str
    source_url: str


@dataclass(frozen=True)
class ClassifiedEmail:
    email: EmailMessage
    category: EmailCategory
    justification: str
    urgency_score: int
    confidence: float
