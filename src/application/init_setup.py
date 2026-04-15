from __future__ import annotations

from dataclasses import dataclass
from getpass import getpass
from pathlib import Path


@dataclass(frozen=True)
class ImapProfile:
    label: str
    host: str
    port: int
    mailbox: str


IMAP_PROFILES: dict[str, ImapProfile] = {
    "gmail": ImapProfile(
        label="Gmail",
        host="imap.gmail.com",
        port=993,
        mailbox="INBOX",
    ),
    "outlook": ImapProfile(
        label="Outlook",
        host="outlook.office365.com",
        port=993,
        mailbox="INBOX",
    ),
    "yahoo": ImapProfile(
        label="Yahoo Mail",
        host="imap.mail.yahoo.com",
        port=993,
        mailbox="INBOX",
    ),
    "other": ImapProfile(
        label="Outro provedor",
        host="",
        port=993,
        mailbox="INBOX",
    ),
}


def _prompt_text(label: str, default: str | None = None, secret: bool = False) -> str:
    suffix = f" [{default}]" if default else ""
    full_label = f"{label}{suffix}: "
    if secret:
        value = getpass(full_label).strip()
    else:
        value = input(full_label).strip()
    if value:
        return value
    if default is not None:
        return default
    raise ValueError(f"{label} is required")


def _prompt_yes_no(label: str, default: bool = True) -> bool:
    default_label = "s" if default else "n"
    value = input(f"{label} [s/n] [{default_label}]: ").strip().lower()
    if not value:
        return default
    if value in {"s", "sim", "y", "yes"}:
        return True
    if value in {"n", "nao", "não", "no"}:
        return False
    raise ValueError("Resposta invalida. Use 's' ou 'n'.")


def _prompt_imap_profile_key() -> str:
    print("Escolha o provedor de e-mail para aplicar uma configuracao sugerida:")
    keys = list(IMAP_PROFILES.keys())
    for index, key in enumerate(keys, start=1):
        print(f"  {index}. {IMAP_PROFILES[key].label}")

    raw_value = _prompt_text("Opcao", default="1")
    if raw_value.isdigit():
        selected_index = int(raw_value)
        if 1 <= selected_index <= len(keys):
            return keys[selected_index - 1]

    normalized_value = raw_value.strip().lower()
    if normalized_value in IMAP_PROFILES:
        return normalized_value
    raise ValueError("Opcao de provedor invalida.")


def run_init_setup(target_file: Path = Path(".env")) -> None:
    print("Configuracao guiada do UNEX Notifier")
    print("Preencha os dados abaixo. Pressione Enter para usar o valor sugerido.")
    print("")

    profile_key = _prompt_imap_profile_key()
    profile = IMAP_PROFILES[profile_key]

    print("")
    use_suggested = _prompt_yes_no(
        "Usar configuracao IMAP sugerida para esse provedor?",
        default=True,
    )

    if use_suggested:
        imap_host = profile.host
        imap_port = str(profile.port)
        imap_mailbox = profile.mailbox
    else:
        imap_host = _prompt_text("Servidor IMAP", default=profile.host or None)
        imap_port = _prompt_text("Porta IMAP", default=str(profile.port))
        imap_mailbox = _prompt_text("Caixa de entrada (mailbox)", default=profile.mailbox)

    print("")
    imap_username = _prompt_text("E-mail completo da conta IMAP")
    imap_app_password = _prompt_text(
        "Senha de acesso IMAP (ou app password)",
        secret=True,
    )
    allowed_domains = _prompt_text(
        "Dominios permitidos (separados por virgula, ex: faculdade.edu.br)",
    )
    gemini_api_key = _prompt_text("Chave da API Gemini", secret=True)
    gemini_model = _prompt_text("Modelo Gemini", default="gemini-2.5-flash")

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
