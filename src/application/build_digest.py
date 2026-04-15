from __future__ import annotations

from collections import defaultdict
from datetime import datetime

from src.domain.email_entities import ClassifiedEmail, EmailCategory


def _category_title(category: EmailCategory) -> str:
    if category == "atividade":
        return "ATIVIDADE"
    if category == "prazo":
        return "PRAZO"
    if category == "aviso":
        return "AVISO"
    return "IRRELEVANTE"


def build_daily_digest(classified_emails: list[ClassifiedEmail], allowed_domains: list[str]) -> str:
    today_label = datetime.now().strftime("%d %b")
    grouped: dict[EmailCategory, list[ClassifiedEmail]] = defaultdict(list)
    for item in classified_emails:
        grouped[item.category].append(item)

    lines: list[str] = [f"Resumo de e-mails - {today_label}"]
    domain_label = ", ".join(allowed_domains) if allowed_domains else "domínios não definidos"
    lines.append(f"Domínios monitorados: {domain_label}")
    lines.append(f"Total processado: {len(classified_emails)} e-mail(s)")
    lines.append("")

    for category in ("atividade", "prazo", "aviso", "irrelevante"):
        emails = grouped.get(category, [])
        if not emails:
            continue
        lines.append(f"{_category_title(category)} ({len(emails)})")
        lines.append("-" * 48)
        for email in emails:
            lines.append(f"Assunto: {email.email.subject or '(sem assunto)'}")
            lines.append(f"De: {email.email.from_email}")
            lines.append(f"Categoria: {_category_title(email.category)}")
            lines.append(f"Resumo da classificação: {email.justification}")
            lines.append(f"Confiança: {email.confidence:.2f}")
            if email.urgency_score >= 70:
                lines.append(f"Urgência: ALTA ({email.urgency_score}/100)")
            else:
                lines.append(f"Urgência: {email.urgency_score}/100")
            lines.append(f"Recebido em: {email.email.received_at.isoformat()}")
            lines.append(f"Link: {email.email.source_url}")
            lines.append("")
        lines.append("")

    lines.append("Fim do relatório.")
    return "\n".join(lines)
