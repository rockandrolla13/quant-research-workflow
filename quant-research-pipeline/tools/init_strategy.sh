#!/usr/bin/env bash
# Scaffold a new strategy directory.
# Usage: ./tools/init_strategy.sh <strategy_id> [pdf_path]

set -euo pipefail

[[ $# -lt 1 ]] && { echo "Usage: $0 <strategy_id> [pdf]"; exit 1; }

SID="$1"; PDF="${2:-}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIR="$ROOT/strategies/$SID"

[[ -d "$DIR" ]] && echo "⚠️ $DIR exists, adding missing dirs"

mkdir -p "$DIR"/{input,extract/images,synth,spec,repo/src/"$SID",repo/tests,repo/notebooks,tex}

if [[ -n "$PDF" ]]; then
    [[ ! -f "$PDF" ]] && { echo "❌ PDF not found: $PDF"; exit 1; }
    [[ ! -f "$DIR/input/source.pdf" ]] && cp "$PDF" "$DIR/input/source.pdf" && echo "📄 Copied PDF"
fi

[[ ! -f "$DIR/input/meta.json" ]] && echo '{"title":"","authors":[],"date":"","source_url":""}' > "$DIR/input/meta.json"

echo "✅ Scaffolded: $DIR"
echo "Next: ./tools/run-extract.sh python tools/ingest.py $DIR/input/source.pdf -s $SID"
