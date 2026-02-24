#!/usr/bin/env bash
# Wrapper script to run commands in .venv-extract environment.
# Usage: ./tools/run-extract.sh <command> [args...]
# Example: ./tools/run-extract.sh python tools/ingest.py source.pdf -s my_strategy

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$REPO_ROOT/.venv-extract"

if [[ ! -d "$VENV_DIR" ]]; then
    echo "❌ .venv-extract not found at $VENV_DIR" >&2
    echo "   Create with: python3 -m venv $VENV_DIR" >&2
    exit 1
fi

source "$VENV_DIR/bin/activate"
exec "$@"
