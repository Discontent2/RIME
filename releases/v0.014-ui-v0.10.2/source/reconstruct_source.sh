#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
cat RIME_v0_014_UI_v0_10_2_source.tar.gz.b64.part* | tr -d '\r\n' | base64 -d > RIME_v0_014_UI_v0_10_2_source.tar.gz
printf '%s  %s\n' 'ad002065dab27e56f6929deac6867a6fca60d04c065a14a10c9132b527d5d357' 'RIME_v0_014_UI_v0_10_2_source.tar.gz' | sha256sum -c -
