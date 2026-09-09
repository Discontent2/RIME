#!/usr/bin/env bash
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
if [ -x "$HERE/.venv/bin/python" ]; then
  exec "$HERE/.venv/bin/python" "$HERE/run_rime.py" "$@"
else
  exec python3 "$HERE/run_rime.py" "$@"
fi
