# AGENTS.md

## Read first

Before changing RIME, read:

1. `README.md`
2. `FRONTLOAD.md`
3. `MAPPING.md`
4. `VALIDATION.md`

## Stable baseline

**RIME v0.012 is the accepted working baseline.** Preserve its successful behavior unless a task explicitly changes it.

## Project definition

RIME is a deterministic, image-conditioned procedural **Sega Genesis / Mega Drive** music composition engine with interpretable visual-to-musical mapping.

## Hard constraints

- Genesis-only direction. Do not add SNES/SPC700/S-DSP logic.
- Preserve deterministic same-image/same-settings identity.
- Preserve causal inspectability: visual evidence → genome → musical decision → event.
- Preserve finite Launch and onset-based Drive.
- Preserve maximum 3 substantial stops per rolling 80 seconds by default.
- Negative space may thin lead/ornament/harmony but must not repeatedly kill the post-Launch foundation.
- Preserve 8-bar drum/groove memory and 8-bar melodic memory.
- Preserve shared rhythmic pocket among drums, bass, harmony and lead.
- Preserve RIME Sigil identity without restarting it every bar.
- Preserve v0.012 macro/meso/micro Mapping Intelligence jurisdiction.
- Hue may color harmony/timbre but should not directly own tonic selection.
- Treat structural tests as structural tests. Human listening is the final musical quality test.
- The local renderer is YM2612/SN76489-inspired, not cycle-accurate hardware emulation.

## Development rule

Make narrow, testable changes. Run the existing smoke/regression suite and compare against v0.012 before claiming improvement. If visual mapping changes, use `--mapping-test` and verify intended changes while identity invariants remain stable.
