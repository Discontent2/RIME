#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
cat source.b64.part??? | tr -d '\r\n' | base64 -d > RIME_v0_014_UI_v0_10_2_source.tar.gz
sha256sum -c SHA256SUMS.txt
printf 'archive_bytes='; wc -c < RIME_v0_014_UI_v0_10_2_source.tar.gz
printf 'base64_bytes='; cat source.b64.part??? | tr -d '\r\n' | wc -c
tar -tzf RIME_v0_014_UI_v0_10_2_source.tar.gz >/dev/null
printf 'tar_integrity=PASS\n'
