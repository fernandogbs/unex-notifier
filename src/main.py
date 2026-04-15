from __future__ import annotations

import argparse

from src.application.init_setup import run_init_setup
from src.application.run_pipeline import run_pipeline
from src.application.smoke_checks import run_smoke_checks
from src.config.settings import load_settings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Email notifier pipeline")
    parser.add_argument("--init", action="store_true", help="Run interactive setup and generate .env")
    parser.add_argument("--dry-run", action="store_true", help="Do not send Telegram message")
    parser.add_argument("--smoke-check", action="store_true", help="Validate IMAP, Gemini and Telegram setup")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.init:
        run_init_setup()
        return

    settings = load_settings()
    if args.smoke_check:
        results = run_smoke_checks(settings)
        for name, result in results.items():
            print(f"{name}: {result}")
        return
    if args.dry_run:
        settings.dry_run = True
    run_pipeline(settings)


if __name__ == "__main__":
    main()
