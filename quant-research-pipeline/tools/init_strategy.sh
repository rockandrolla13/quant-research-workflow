#!/usr/bin/env bash
# Scaffold a new strategy directory.
# Usage: bash tools/init_strategy.sh <strategy_id> [pdf_path]

set -euo pipefail

if [ $# -lt 1 ]; then
    echo "Usage: bash tools/init_strategy.sh <strategy_id> [pdf_path]"
    exit 1
fi

STRATEGY_ID="$1"
PDF_PATH="${2:-}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIR="$ROOT/strategies/$STRATEGY_ID"

if [ -d "$DIR" ]; then
    echo "⚠️  Directory already exists: $DIR"
    echo "    Re-running is safe — missing subdirs will be created."
fi

# Create directory structure
mkdir -p "$DIR/input"
mkdir -p "$DIR/extract/images"
mkdir -p "$DIR/synth"
mkdir -p "$DIR/spec"
mkdir -p "$DIR/repo/src/$STRATEGY_ID"
mkdir -p "$DIR/repo/tests"
mkdir -p "$DIR/repo/notebooks"
mkdir -p "$DIR/tex"

# Copy PDF if provided
if [ -n "$PDF_PATH" ]; then
    if [ ! -f "$PDF_PATH" ]; then
        echo "❌ PDF not found: $PDF_PATH"
        exit 1
    fi
    if [ ! -f "$DIR/input/source.pdf" ]; then
        cp "$PDF_PATH" "$DIR/input/source.pdf"
        echo "📄 Copied PDF to $DIR/input/source.pdf"
    else
        echo "📄 source.pdf already exists, skipping copy"
    fi
fi

# Create meta.json template if not exists
if [ ! -f "$DIR/input/meta.json" ]; then
    cat > "$DIR/input/meta.json" << 'METAEOF'
{
  "title": "",
  "authors": [],
  "date": "",
  "source_url": ""
}
METAEOF
    echo "📝 Created $DIR/input/meta.json"
fi

echo "✅ Strategy scaffolded: $DIR"
echo ""
echo "   Next steps:"
echo "   1. .venv-extract/bin/python tools/ingest.py $DIR/input/source.pdf --strategy-id $STRATEGY_ID"
echo "   2. Wait for synth/ and spec/ to be filled"
echo "   3. .venv-extract/bin/python tools/validate_spec.py $DIR/spec/spec.yaml"
echo "   4. .venv-extract/bin/python tools/update_state.py $DIR --status"
