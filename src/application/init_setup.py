from __future__ import annotations

from getpass import getpass
from pathlib import Path


def _prompt(name: str, default: str | None = None, secret: bool = False) -> str:
    suffix = f" [{default}]" if default else ""
    label = f"{name}{suffix}: "
    if secret:
        value = getpass(label).strip()
    else:
        value = input(label).strip()
    if value:
        return value
    if default is not None:
        return default
    raise ValueError(f"{name} is required")


def run_init_setup(target_file: Path = Path(".env")) -> None:
    print("Configuracao rapida do UNEX Notifier")
    print("Preencha os campos abaixo. Pressione Enter para aceitar os padroes.")
    print("")

    imap_host = _prompt("IMAP_HOST", default="imap.gmail.com")
    imap_port = _prompt("IMAP_PORT", default="993")
    imap_username = _prompt("IMAP_USERNAME (email completo)")
    imap_app_password = _prompt("IMAP_APP_PASSWORD (app password Google)", secret=True)
    imap_mailbox = _prompt("IMAP_MAILBOX", default="INBOX")
    allowed_domains = _prompt("ALLOWED_DOMAINS (separados por virgula)")
    gemini_api_key = _prompt("GEMINI_API_KEY", secret=True)
    gemini_model = _prompt("GEMINI_MODEL", default="gemini-1.5-flash")

    content = "\n".join(
        [
            f"IMAP_HOST={imap_host}",
            f"IMAP_PORT={imap_port}",
            f"IMAP_USERNAME={imap_username}",
            f"IMAP_APP_PASSWORD={imap_app_password}",
            f"IMAP_MAILBOX={imap_mailbox}",
            f"ALLOWED_DOMAINS={allowed_domains}",
            f"GEMINI_API_KEY={gemini_api_key}",
            f"GEMINI_MODEL={gemini_model}",
            "SQLITE_PATH=.data/seen_emails.db",
            "LOOKBACK_HOURS=24",
            "MAX_EMAILS_PER_RUN=30",
            "DRY_RUN=false",
            "",
        ]
    )

    target_file.write_text(content, encoding="utf-8")
    print("")
    print(f"Arquivo {target_file} criado com sucesso.")
    print("Proximo passo: python -m src.main --smoke-check")
