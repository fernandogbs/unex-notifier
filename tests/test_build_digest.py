from __future__ import annotations

from datetime import UTC, datetime

from src.application.build_digest import build_daily_digest
from src.domain.email_entities import ClassifiedEmail, EmailCategory, EmailMessage


def _classified(category: EmailCategory, urgency: int, subject: str) -> ClassifiedEmail:
    email = EmailMessage(
        message_id=f"id-{subject}",
        subject=subject,
        from_email="prof@faculdade.edu.br",
        from_domain="faculdade.edu.br",
        received_at=datetime.now(UTC),
        body_text="Conteudo",
        source_url="https://mail.google.com/",
    )
    return ClassifiedEmail(
        email=email,
        category=category,
        justification="teste",
        urgency_score=urgency,
        confidence=0.9,
    )


def test_build_daily_digest_groups_categories() -> None:
    digest = build_daily_digest(
        classified_emails=[
            _classified("atividade", 75, "Entrega do trabalho"),
            _classified("aviso", 10, "Aula remota"),
            _classified("irrelevante", 0, "Newsletter"),
        ],
        allowed_domains=["faculdade.edu.br"],
    )
    assert "ATIVIDADE" in digest
    assert "AVISO" in digest
    assert "irrelevante" in digest.lower()
    assert "Urgência: ALTA (75/100)" in digest
