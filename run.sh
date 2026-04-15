#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$ROOT_DIR/.venv"
PYTHON_BIN="${PYTHON_BIN:-python3}"

print_help() {
  cat <<'EOF'
UNEX Notifier runner

Usage:
  ./run.sh init         # setup env + interactive .env creation
  ./run.sh smoke        # run connectivity smoke checks
  ./run.sh run          # run normal pipeline
  ./run.sh dry-run      # run pipeline without marking emails as seen
  ./run.sh test         # run unit tests
  ./run.sh help         # show this help
EOF
}

ensure_venv() {
  if [[ ! -d "$VENV_DIR" ]]; then
    "$PYTHON_BIN" -m venv "$VENV_DIR"
  fi
  # shellcheck disable=SC1091
  source "$VENV_DIR/bin/activate"
}

install_deps() {
  python -m pip install --upgrade pip >/dev/null
  pip install -e ".[dev]" >/dev/null
}

main() {
  cd "$ROOT_DIR"
  command="${1:-run}"

  case "$command" in
    init)
      ensure_venv
      install_deps
      python -m src.main --init
      ;;
    smoke)
      ensure_venv
      install_deps
      python -m src.main --smoke-check
      ;;
    run)
      ensure_venv
      install_deps
      python -m src.main
      ;;
    dry-run)
      ensure_venv
      install_deps
      python -m src.main --dry-run
      ;;
    test)
      ensure_venv
      install_deps
      pytest
      ;;
    help|--help|-h)
      print_help
      ;;
    *)
      echo "Unknown command: $command"
      echo ""
      print_help
      exit 1
      ;;
  esac
}

main "$@"
