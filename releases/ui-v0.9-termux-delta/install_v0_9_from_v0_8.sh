#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
PART_DIR="$REPO_DIR/releases/ui-v0.9-termux-delta"
BASE="$HOME/RIME_UI_v0_8"
TARGET="$HOME/RIME_UI_v0_9"
ARCHIVE="$PREFIX/tmp/RIME_UI_v0_9_DELTA_FROM_v0_8.tar.gz"
EXPECTED="249632bae0f6f78d897bef230eecaf46cb3329d3181fb78ad15bc204896aa378"

if [ ! -d "$BASE" ]; then
  echo "RIME UI v0.8 was not found at: $BASE"
  echo "Start v0.8 once or place it there, then run this installer again."
  exit 1
fi

rm -rf "$TARGET"
cp -a "$BASE" "$TARGET"

cat "$PART_DIR"/RIME_UI_v0_9_DELTA_FROM_v0_8.tar.gz.b64.part* | base64 -d > "$ARCHIVE"
ACTUAL="$(sha256sum "$ARCHIVE" | awk '{print $1}')"
if [ "$ACTUAL" != "$EXPECTED" ]; then
  echo "Checksum mismatch. Expected $EXPECTED but got $ACTUAL"
  rm -f "$ARCHIVE"
  exit 1
fi

tar -xzf "$ARCHIVE" -C "$TARGET"
rm -f "$ARCHIVE"
find "$TARGET" -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true

echo
echo "RIME UI v0.9 installed at: $TARGET"
echo "Start it with:"
echo "  cd ~/RIME_UI_v0_9 && python run_ui.py"
