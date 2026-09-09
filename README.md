# RIME

**Retro Image Music Engine**

> **Current stable baseline: v0.012 — Equivariant Musification + Mapping Intelligence**
>
> Status: **accepted working baseline** as of 2026-09-09.

## START HERE

**For Codex, AI coding agents, or a new development session:** read [`FRONTLOAD.md`](FRONTLOAD.md) before changing the engine. It records the design intent, non-regression rules, current architecture, accepted behaviors, and the path that led to v0.012.

RIME is a **deterministic, image-conditioned procedural Sega Genesis music composition engine**. A still image is analyzed at multiple spatial scales, converted into interpretable musical genomes, composed into symbolic musical events, and rendered through an original **YM2612/SN76489-inspired** local synthesizer.

RIME is not an image classifier followed by a music prompt. The core path is:

```text
IMAGE
  ↓
MULTI-SCALE VISUAL ANALYSIS
  ↓
TRANSFORM / EDGE / ANOMALY EVIDENCE
  ↓
MAPPING INTELLIGENCE
  ↓
MUSICAL GENOMES
  ↓
PROCEDURAL COMPOSITION
  ↓
MIDI / EVENTS
  ↓
GENESIS-INSPIRED SYNTHESIS
  ↓
WAV + MIDI + DIAGNOSTIC
```

## Project identity

The most precise current description is:

> **An interpretable image-conditioned musification system for deterministic Sega Genesis-style procedural composition.**

The practical product description is simpler:

> **Turn an image into an original Sega Genesis-style soundtrack.**

## Hard project direction

RIME is now **Genesis-only**. Do not reintroduce SNES/SPC700 design into this project unless that direction is explicitly changed later.

Primary sound language:

- Yamaha **YM2612** inspired FM roles
- Texas Instruments **SN76489** inspired PSG/noise roles
- DAC-style kick/snare body in the local Genesis-inspired renderer
- PSG/noise hats and high percussion
- FM bass, lead, tom and metallic percussion roles

RIME does **not** claim to be a cycle-accurate Mega Drive emulator. The renderer is an original local synthesizer inspired by the hardware architecture.

## What v0.012 preserves

v0.012 is built on the musical systems that became acceptable across v0.008–v0.011:

- finite intro followed by an explicit **Launch**
- **Drive Engine** that measures propulsion by onsets, not merely sustained occupancy
- **Momentum Engine**
- maximum **3 substantial stops per rolling 80 seconds**
- Genesis drum-production engine with six groove architectures
- dense PSG/noise surface percussion without simply multiplying kick hits
- **8-bar drum memory**
- **8-bar melodic memory**
- melody statement / continuation / answer / breath / development behavior
- bass, harmony and lead sharing one rhythmic pocket
- RIME **Sigil** as recognizable melodic identity
- Solarized Shadow breakdown
- Foreshadow and primary-world return
- negative space that may thin lead/harmony without repeatedly killing the rhythmic foundation
- deterministic same-image / same-settings behavior

## What v0.012 adds

v0.012 formalizes the relationship between image evidence and music:

- **Equivariant musification**
- **Mapping Intelligence Genome**
- macro / meso / micro musical jurisdiction
- **Visual Kinetic Potential** for implied motion in still images
- crossmodal priors
- hue demotion: hue colors harmony/timbre but no longer directly owns tonic selection
- statistical region-of-interest hierarchy without object-recognition AI
- `--visual-authority 1|2|3`
- `--mapping-test` laboratory for controlled image transformations

### Musical jurisdiction

```text
MACRO visual structure
→ tonic stability, register, bass weight, large-form tendency

MESO visual structure
→ kinetic potential, groove, phrase energy, transient drive

MICRO visual detail
→ PSG/noise surface, ornament, small percussion, local FM texture
```

This prevents tiny visual noise from unexpectedly rewriting global musical identity.

## Mapping principle

The central v0.012 law is:

> **Change the image intentionally, and the music should change intentionally.**

Controlled mapping tests preserve the base identity family while allowing relevant surface parameters to respond.

Current laboratory transformations include:

- brightness +20%
- brightness -20%
- higher contrast
- lower contrast
- Gaussian blur
- desaturation
- horizontal flip
- center crop

The experiment locks core invariants such as tonic, mode, RIME Sigil, Genesis drum architecture and form architecture so the transformed outputs remain related versions of the same picture-song.

## Quick start

```bash
python run_rime.py image.png \
  --length 32 \
  --evolve 3 \
  --grid-mode layered \
  --rhythm-strength 3 \
  --visual-authority 2 \
  --solar-breakdown auto \
  --foreshadow auto \
  --max-stops 3 \
  --stop-window 80 \
  --variation 0 \
  --output output
```

### Mapping laboratory

```bash
python run_rime.py image.png \
  --length 16 \
  --evolve 2 \
  --visual-authority 2 \
  --mapping-test full \
  --output output
```

## Outputs

A normal generation can produce:

- WAV
- MIDI
- musical genome JSON
- pixel/analysis previews
- anomaly / transform previews
- `*_vision.png` visual diagnostic

A mapping test additionally produces transformed-image variants and `*_mapping_report.json` / `*_mapping_report.png`.

## Validation philosophy

Programmatic tests are useful for determinism, mapping direction, continuity, stop budgets, activity coverage and non-regression. They **do not replace listening**.

> **Human listening is the decisive musical quality test.**

The user explicitly accepted v0.012 as the first satisfactory working baseline. Future versions should improve from this point rather than casually replacing the behaviors that finally solved the repeated false starts, underpowered drums, bar-by-bar melody resets and disconnected band rhythm of earlier versions.

## Repository orientation

- `FRONTLOAD.md` — context that should be read before development
- `MAPPING.md` — v0.012 visual-to-musical mapping model
- `VALIDATION.md` — structural validation state
- `TERMUX.md` — Android / Termux operation
- `CHANGELOG.md` — v0.012 change summary
- `rime/` — engine modules
- `tests/` — smoke/regression tests
- `presets/genesis.json` — Genesis-oriented preset data
- `releases/` — packaged stable snapshots when present

## Current milestone

**v0.012 is the reference branch point.**

Do not optimize away its interpretability. RIME's major advantage is that a bad musical result can be traced through:

```text
visual evidence
→ genome value
→ musical decision
→ generated event
```

That causal inspectability is part of the product, not merely a debugging convenience.
