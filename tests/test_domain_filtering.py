from __future__ import annotations

from datetime import UTC, datetime, timedelta

from src.domain.classification import is_allowed_domain, is_recent_email
from src.domain.email_entities import EmailMessage


def _sample_email(*, domain: str, received_at: datetime) -> EmailMessage:
    return EmailMessage(
        message_id="id-1",
        subject="Aviso",
        from_email=f"secretaria@{domain}",
        from_domain=domain,
        received_at=received_at,
        body_text="Corpo do email",
        source_url="https://mail.google.com/",
    )


def test_is_allowed_domain_accepts_configured_domain() -> None:
    email = _sample_email(domain="faculdade.edu.br", received_at=datetime.now(UTC))
    assert is_allowed_domain(email, ["faculdade.edu.br"])


def test_is_allowed_domain_rejects_unknown_domain() -> None:
    email = _sample_email(domain="outro.org", received_at=datetime.now(UTC))
    assert not is_allowed_domain(email, ["faculdade.edu.br"])


def test_is_recent_email_respects_lookback() -> None:
    now = datetime.now(UTC)
    old_email = _sample_email(domain="faculdade.edu.br", received_at=now - timedelta(hours=25))
    fresh_email = _sample_email(domain="faculdade.edu.br", received_at=now - timedelta(hours=2))

    assert not is_recent_email(old_email, 24, now)
    assert is_recent_email(fresh_email, 24, now)
