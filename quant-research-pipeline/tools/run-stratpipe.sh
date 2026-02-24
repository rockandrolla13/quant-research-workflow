#!/usr/bin/env bash
# Wrapper script to run commands in .venv-stratpipe environment.
# Usage: ./tools/run-stratpipe.sh <command> [args...]
# Example: ./tools/run-stratpipe.sh pytest strategies/fx_cookbook/repo/tests -q

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$REPO_ROOT/.venv-stratpipe"

if [[ ! -d "$VENV_DIR" ]]; then
    echo "❌ .venv-stratpipe not found at $VENV_DIR" >&2
    echo "   Create with: python3 -m venv $VENV_DIR" >&2
    exit 1
fi

source "$VENV_DIR/bin/activate"
exec "$@"
