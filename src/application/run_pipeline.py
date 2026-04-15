from __future__ import annotations

import logging
from datetime import UTC, datetime

from src.application.build_digest import build_daily_digest
from src.config.settings import AppSettings
from src.domain.classification import is_allowed_domain, is_recent_email
from src.domain.email_entities import ClassifiedEmail, EmailMessage
from src.infra.ai.gemini_classifier import GeminiEmailClassifier
from src.infra.email.imap_reader import fetch_recent_unseen_emails
from src.infra.store.sqlite_seen_repo import SeenEmailRepository


logger = logging.getLogger(__name__)


def _filter_candidates(
    emails: list[EmailMessage],
    settings: AppSettings,
    seen_repo: SeenEmailRepository,
) -> list[EmailMessage]:
    now = datetime.now(UTC)
    filtered: list[EmailMessage] = []
    for email in emails:
        if seen_repo.has_seen(email.message_id):
            continue
        if not is_recent_email(email, settings.lookback_hours, now):
            continue
        if not is_allowed_domain(email, settings.allowed_domain_list):
            continue
        filtered.append(email)
    return filtered


def run_pipeline(settings: AppSettings) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )
    logger.info("Starting email pipeline")

    seen_repo = SeenEmailRepository(settings.sqlite_path)
    all_emails = fetch_recent_unseen_emails(settings)
    logger.info("Fetched %s recent unseen emails", len(all_emails))

    candidates = _filter_candidates(all_emails, settings, seen_repo)
    if not candidates:
        logger.info("No candidate emails after filtering")
        print("Nenhum e-mail novo encontrado para os filtros atuais.")
        return

    classifier = GeminiEmailClassifier(settings)
    classified: list[ClassifiedEmail] = [classifier.classify(item) for item in candidates]
    digest = build_daily_digest(classified, settings.allowed_domain_list)
    print(digest)

    if settings.dry_run:
        logger.info("Dry-run active; not marking emails as seen")
        return

    seen_repo.mark_seen_many([item.email.message_id for item in classified])
    logger.info("Processed and marked %s classified emails", len(classified))
