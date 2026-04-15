from __future__ import annotations

import imaplib
import socket

from google import genai

from src.config.settings import AppSettings


def _check_imap(settings: AppSettings) -> str:
    mailbox = settings.imap_mailbox
    try:
        with imaplib.IMAP4_SSL(settings.imap_host, settings.imap_port, timeout=10) as client:
            client.login(settings.imap_username, settings.imap_app_password)
            status, _ = client.select(mailbox)
            if status != "OK":
                return f"error: mailbox '{mailbox}' nao encontrada"
            client.logout()
            return "ok"
    except imaplib.IMAP4.error:
        return "error: falha de autenticacao IMAP (usuario/senha)"
    except TimeoutError:
        return "error: timeout na conexao IMAP"
    except socket.gaierror:
        return "error: host IMAP invalido ou indisponivel"
    except Exception as error:
        return f"error: {error}"


def _check_gemini(settings: AppSettings) -> str:
    client = genai.Client(api_key=settings.gemini_api_key)
    response = client.models.generate_content(
        model=settings.gemini_model,
        contents="Retorne apenas: ok",
    )
    response_text = response.text or ""
    if "ok" in response_text.lower():
        return "ok"
    return "unexpected-response"


def run_smoke_checks(settings: AppSettings) -> dict[str, str]:
    results: dict[str, str] = {"imap": _check_imap(settings)}
    try:
        results["gemini"] = _check_gemini(settings)
    except Exception as error:
        results["gemini"] = f"error: {error}"

    return results
