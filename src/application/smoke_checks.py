from __future__ import annotations

import socket

from google import genai

from src.config.settings import AppSettings


def _check_imap(settings: AppSettings) -> str:
    with socket.create_connection((settings.imap_host, settings.imap_port), timeout=5):
        return "ok"


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
    results: dict[str, str] = {}
    try:
        results["imap"] = _check_imap(settings)
    except Exception as error:
        results["imap"] = f"error: {error}"

    try:
        results["gemini"] = _check_gemini(settings)
    except Exception as error:
        results["gemini"] = f"error: {error}"

    return results
