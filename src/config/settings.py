from __future__ import annotations

from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )

    imap_host: str = Field(alias="IMAP_HOST")
    imap_port: int = Field(default=993, alias="IMAP_PORT")
    imap_username: str = Field(alias="IMAP_USERNAME")
    imap_app_password: str = Field(alias="IMAP_APP_PASSWORD")
    imap_mailbox: str = Field(default="INBOX", alias="IMAP_MAILBOX")
    allowed_domains: str = Field(alias="ALLOWED_DOMAINS")

    gemini_api_key: str = Field(alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-1.5-flash", alias="GEMINI_MODEL")

    sqlite_path: Path = Field(default=Path(".data/seen_emails.db"), alias="SQLITE_PATH")
    lookback_hours: int = Field(default=24, alias="LOOKBACK_HOURS")
    max_emails_per_run: int = Field(default=30, alias="MAX_EMAILS_PER_RUN")
    dry_run: bool = Field(default=False, alias="DRY_RUN")

    @field_validator("allowed_domains")
    @classmethod
    def ensure_allowed_domains(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("ALLOWED_DOMAINS cannot be empty")
        return value

    @property
    def allowed_domain_list(self) -> list[str]:
        items = [domain.strip().lower() for domain in self.allowed_domains.split(",")]
        return [item for item in items if item]


def load_settings() -> AppSettings:
    settings = AppSettings()
    settings.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    return settings
