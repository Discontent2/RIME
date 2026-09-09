# RIME v0.012 validation

Validation was performed locally against the packaged Python engine. These are structural/programmatic checks, not a claim of auditory listening.

## Core regressions passed

- Python compilation
- deterministic genome/event generation for identical image/settings
- Genesis-only renderer path
- 8 / 16 / 32 / 64-bar composition paths
- layered and layered64 analysis
- Launch + Drive Engine
- Genesis drum-production engine
- 8-bar Genesis melody memory
- cross-role band rhythm
- Solarized Shadow and Foreshadow
- Silence Governor
- Momentum Engine / maximum 3 stops per rolling 80 seconds
- MIDI export
- stereo WAV export
- expanded v0.012 Vision Diagnostic

## v0.012 mapping-intelligence checks

The new Mapping Intelligence genome was checked for bounded values and deterministic construction. Hue no longer directly selects tonic; tonic is calculated primarily from macro structure plus a stable identity seed, with a small hue nudge.

The full controlled transformation laboratory was run on the bundled demo image with eight variants:

- brightness +20%
- brightness -20%
- high contrast
- low contrast
- Gaussian blur r4
- desaturated
- horizontal flip
- center crop 80%

All eight passed their defined direction/invariant checks, producing a mapping confidence of 100% for that test image.

The same eight-variant test was also run on the recurring glowing-figure regression image used during v0.008–v0.011 development. It likewise passed all defined mapping checks.

Important: a 100% mapping-test score means the implemented *rules moved in their prescribed directions and identity invariants held*. It is not a claim that listeners will prefer every mapping.

## Exact glowing-figure regression, 32 bars

The v0.012 regression produced:

```text
Architecture:        dungeon + apocalyptic
Key / mode:          G aeolian
Tempo:               97 BPM
Visual kinetic:      69%
Transient prior:     62%
Micro-detail prior:  59%
Macro authority:     76%
Meso authority:      72%
Micro authority:     59%
Foundation coverage: 96%
Drive coverage:      100%
Rolling stop max:    3 / 80 seconds
Genesis drums:       uncanny_machine
Drum events:         660 total / 32 bars
Bass active bars:    100%
Harmony active bars: 100%
Lead active bars:    74%
Quality:             PASS
```

## Important limitation

RIME's Genesis Lab renderer is an original YM2612/SN76489-inspired local synthesizer, not a cycle-accurate Mega Drive emulator. Equivariance tests verify deterministic mapping behavior, not subjective musical quality. Human listening remains the decisive test.
