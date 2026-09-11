# Canonical archive parts

The canonical archive is represented by exactly eight ordered base64 fragments, `part00` through `part07`, with a nominal part size of 30,000 base64 bytes except the final part. Reconstruct by concatenating in lexical order, removing line breaks if any, base64-decoding, then verifying SHA-256 `ad002065dab27e56f6929deac6867a6fca60d04c065a14a10c9132b527d5d357`.

Older partial archive experiments are not canonical and must not be used.
