#!/usr/bin/env bash
set -e
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
echo "RIME v0.008 ready. Try: ./rime.sh test_images_demo.png --length 32 --evolve 3 --solar-breakdown auto --foreshadow auto --free-run-min 10 --free-run-max 60 --max-stops 3 --stop-window 80 --variation 0"
