from __future__ import annotations

import re
from datetime import datetime, timedelta

from src.domain.email_entities import EmailMessage


DEADLINE_HINTS = ("prazo", "deadline", "até", "entrega", "vence", "urgente", "hoje", "amanhã")


def is_allowed_domain(email: EmailMessage, allowed_domains: list[str]) -> bool:
    if not allowed_domains:
        return False
    return email.from_domain.lower() in {domain.lower() for domain in allowed_domains}


def estimate_urgency_from_text(text: str) -> int:
    lowered_text = text.lower()
    hint_count = sum(1 for hint in DEADLINE_HINTS if hint in lowered_text)
    date_hits = len(re.findall(r"\b\d{1,2}/\d{1,2}\b", lowered_text))
    score = min(100, (hint_count * 18) + (date_hits * 20))
    return score


def is_recent_email(email: EmailMessage, lookback_hours: int, now: datetime) -> bool:
    if lookback_hours <= 0:
        return True
    cutoff = now - timedelta(hours=lookback_hours)
    return email.received_at >= cutoff
