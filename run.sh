#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$ROOT_DIR/.venv"

detect_python() {
  if [[ -n "${PYTHON_BIN:-}" ]]; then
    echo "$PYTHON_BIN"
    return 0
  fi

  if command -v python3 >/dev/null 2>&1; then
    echo "python3"
    return 0
  fi

  if command -v python >/dev/null 2>&1; then
    echo "python"
    return 0
  fi

  echo "Python interpreter not found (python3/python)." >&2
  exit 1
}

VENV_PYTHON="$VENV_DIR/bin/python"
VENV_PIP="$VENV_DIR/bin/pip"

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
  local base_python
  base_python="$(detect_python)"

  if [[ ! -d "$VENV_DIR" ]]; then
    "$base_python" -m venv "$VENV_DIR"
  fi

  if [[ ! -x "$VENV_PYTHON" ]]; then
    echo "Virtualenv python not found at $VENV_PYTHON" >&2
    exit 1
  fi
}

install_deps() {
  "$VENV_PYTHON" -m pip install --upgrade pip >/dev/null
  "$VENV_PIP" install -e ".[dev]" >/dev/null
}

main() {
  cd "$ROOT_DIR"
  command="${1:-run}"

  case "$command" in
    init)
      ensure_venv
      install_deps
      "$VENV_PYTHON" -m src.main --init
      ;;
    smoke)
      ensure_venv
      install_deps
      "$VENV_PYTHON" -m src.main --smoke-check
      ;;
    run)
      ensure_venv
      install_deps
      "$VENV_PYTHON" -m src.main
      ;;
    dry-run)
      ensure_venv
      install_deps
      "$VENV_PYTHON" -m src.main --dry-run
      ;;
    test)
      ensure_venv
      install_deps
      "$VENV_PYTHON" -m pytest
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
