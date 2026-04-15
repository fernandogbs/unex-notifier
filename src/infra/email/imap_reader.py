from __future__ import annotations

import email
import imaplib
from datetime import UTC, datetime, timedelta
from email.header import decode_header
from email.message import Message
from email.utils import parsedate_to_datetime

from src.config.settings import AppSettings
from src.domain.email_entities import EmailMessage


def _decode_mime(value: str | None) -> str:
    if not value:
        return ""

    parts = decode_header(value)
    chunks: list[str] = []
    for chunk, encoding in parts:
        if isinstance(chunk, bytes):
            chunks.append(chunk.decode(encoding or "utf-8", errors="replace"))
            continue
        chunks.append(chunk)
    return "".join(chunks).strip()


def _extract_text(payload: Message) -> str:
    if payload.is_multipart():
        for part in payload.walk():
            if part.get_content_type() != "text/plain":
                continue
            if "attachment" in str(part.get("Content-Disposition", "")):
                continue
            raw = part.get_payload(decode=True)
            if not raw:
                continue
            charset = part.get_content_charset() or "utf-8"
            return raw.decode(charset, errors="replace").strip()
        return ""

    raw_payload = payload.get_payload(decode=True)
    if not raw_payload:
        return ""
    charset = payload.get_content_charset() or "utf-8"
    return raw_payload.decode(charset, errors="replace").strip()


def _extract_domain(sender: str) -> str:
    if "@" not in sender:
        return ""
    address = sender.split("<")[-1].replace(">", "")
    return address.split("@")[-1].strip().lower()


def _parse_received_at(value: str | None) -> datetime:
    if not value:
        return datetime.now(UTC)
    parsed = parsedate_to_datetime(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def fetch_recent_unseen_emails(settings: AppSettings) -> list[EmailMessage]:
    since = datetime.now(UTC) - timedelta(hours=settings.lookback_hours)
    since_token = since.strftime("%d-%b-%Y")
    criteria = f'(UNSEEN SINCE "{since_token}")'

    with imaplib.IMAP4_SSL(settings.imap_host, settings.imap_port) as client:
        client.login(settings.imap_username, settings.imap_app_password)
        client.select(settings.imap_mailbox)

        status, result = client.search(None, criteria)
        if status != "OK":
            return []

        ids = result[0].split()
        if not ids:
            return []

        selected_ids = ids[-settings.max_emails_per_run :]
        parsed_emails: list[EmailMessage] = []
        for message_id in selected_ids:
            fetch_status, fetched = client.fetch(message_id, "(RFC822)")
            if fetch_status != "OK":
                continue
            if not fetched or not fetched[0]:
                continue

            raw_email = fetched[0][1]
            if not isinstance(raw_email, bytes):
                continue

            payload = email.message_from_bytes(raw_email)
            subject = _decode_mime(payload.get("Subject"))
            sender = _decode_mime(payload.get("From"))
            message_identifier = _decode_mime(payload.get("Message-ID")) or f"imap-{message_id.decode()}"
            body_text = _extract_text(payload)
            received_at = _parse_received_at(payload.get("Date"))
            from_domain = _extract_domain(sender)
            source_url = "https://mail.google.com/mail/u/0/#inbox"

            parsed_emails.append(
                EmailMessage(
                    message_id=message_identifier,
                    subject=subject,
                    from_email=sender,
                    from_domain=from_domain,
                    received_at=received_at,
                    body_text=body_text,
                    source_url=source_url,
                )
            )
        return parsed_emails
