#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
INPUT_REPO="$ROOT_DIR/aethermind-input"
PERCEPTION_REPO="$ROOT_DIR/aethermind-perception"

for repo in "$INPUT_REPO" "$PERCEPTION_REPO"; do
  if [ ! -d "$repo" ]; then
    echo "Missing repo: $repo" >&2
    exit 1
  fi
  if [ -f "$repo/requirements.txt" ]; then
    pip install -r "$repo/requirements.txt" || echo "Warning: failed to install dependencies for $repo" >&2
  fi
done

SESSION=session_test
SESSION_DIR="$INPUT_REPO/data/$SESSION"
rm -rf "$SESSION_DIR"
mkdir -p "$SESSION_DIR"

mkdir -p "$INPUT_REPO/fixtures"
echo "dummy" > "$INPUT_REPO/fixtures/test.mp4"
echo "dummy" > "$INPUT_REPO/fixtures/test.wav"
cp "$INPUT_REPO/fixtures/test.mp4" "$SESSION_DIR/test.mp4"
cp "$INPUT_REPO/fixtures/test.wav" "$SESSION_DIR/test.wav"
echo '{"timestamp":0,"action":"noop"}' > "$SESSION_DIR/actions.jsonl"

OUTPUT_ROOT="$PERCEPTION_REPO/sessions/$SESSION"
rm -rf "$OUTPUT_ROOT"
mkdir -p "$OUTPUT_ROOT"

python "$PERCEPTION_REPO/session_runner.py" "$SESSION_DIR" "$OUTPUT_ROOT"

SESSION_JSON="$OUTPUT_ROOT/session.json"
CLIPS_DIR="$OUTPUT_ROOT/clips"

if [ ! -f "$SESSION_JSON" ]; then
  echo "FAIL: session.json not found" >&2
  exit 1
fi

expected=$(python - "$SESSION_JSON" <<'PY'
import json,math,sys
with open(sys.argv[1]) as f:
    data=json.load(f)
print(math.ceil(data['clip_length']/data['chunk_duration']))
PY
)

actual=$(ls "$CLIPS_DIR" | wc -l)

if [ "$actual" -ne "$expected" ]; then
  echo "FAIL: expected $expected clips, found $actual" >&2
  exit 1
fi

echo "PASS: produced $actual clips"
