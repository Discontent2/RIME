#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

SRC="$HOME/RIME_UI_v0_7"
DEST="$HOME/RIME_UI_v0_8"
CACHE="${TMPDIR:-$HOME/.cache}/rime-v08-github-install"
BASE="https://raw.githubusercontent.com/Discontent2/RIME/main/releases/ui-v0.8-termux-delta"
ARCHIVE="$CACHE/RIME_UI_v0_8_DELTA_FROM_v0_7.tar.gz"
EXPECTED_SHA="0b75252cf82cd1de3c7cbee5239ee84abc329deb585b0b69ce5d591f2a1b6400"

printf '\nRIME UI v0.8 GitHub installer\n'
printf '================================\n'

if [ ! -d "$SRC" ]; then
  printf '\nERROR: %s was not found.\n' "$SRC" >&2
  printf 'This compact installer upgrades the existing RIME UI v0.7 folder.\n' >&2
  printf 'Do not delete v0.7. If your folder has a different name, rename it to RIME_UI_v0_7 and rerun.\n' >&2
  exit 2
fi

if [ ! -f "$SRC/run_ui.py" ]; then
  printf '\nERROR: %s exists but does not look like a complete v0.7 installation.\n' "$SRC" >&2
  exit 3
fi

if ! command -v curl >/dev/null 2>&1; then
  printf 'Installing curl...\n'
  pkg install -y curl
fi

mkdir -p "$CACHE"
rm -f "$CACHE"/part?? "$CACHE/archive.b64" "$ARCHIVE"

printf 'Fetching v0.8 delta directly from GitHub...\n'
for n in 00 01 02 03 04 05 06; do
  printf '  part %s/06\n' "$n"
  curl -fL --retry 4 --retry-delay 2 --connect-timeout 20 \
    "$BASE/RIME_UI_v0_8_DELTA_FROM_v0_7.tar.gz.b64.part$n" \
    -o "$CACHE/part$n"
done

cat "$CACHE"/part00 "$CACHE"/part01 "$CACHE"/part02 "$CACHE"/part03 \
    "$CACHE"/part04 "$CACHE"/part05 "$CACHE"/part06 > "$CACHE/archive.b64"

base64 -d "$CACHE/archive.b64" > "$ARCHIVE"

ACTUAL_SHA="$(sha256sum "$ARCHIVE" | awk '{print $1}')"
if [ "$ACTUAL_SHA" != "$EXPECTED_SHA" ]; then
  printf '\nERROR: checksum mismatch.\nExpected: %s\nActual:   %s\n' "$EXPECTED_SHA" "$ACTUAL_SHA" >&2
  exit 4
fi
printf 'Checksum verified: %s\n' "$ACTUAL_SHA"

printf 'Building %s from your v0.7 installation...\n' "$DEST"
rm -rf "$DEST"
cp -a "$SRC" "$DEST"
tar -xzf "$ARCHIVE" -C "$DEST"

cd "$DEST"
printf 'Compiling Python files...\n'
python -m compileall -q .

printf 'Running RIME UI smoke test...\n'
python tests/test_ui.py

printf '\nSUCCESS: RIME UI v0.8 is installed at:\n  %s\n' "$DEST"
printf '\nStart it with:\n  cd ~/RIME_UI_v0_8\n  python run_ui.py\n\n'
printf 'Then open http://127.0.0.1:7860\n\n'
