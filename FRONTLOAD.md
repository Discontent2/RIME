# RIME Development Front-Load

**Read this before modifying the engine.**

This document captures the project state at the moment **RIME v0.012** became the first user-accepted working baseline.

## 1. Mission

RIME is a **deterministic image-conditioned procedural Sega Genesis music composition engine**.

A still image is not merely classified into a mood or converted into a text prompt. RIME measures the image, derives interpretable musical control data, composes symbolic music, and renders an original Genesis-inspired soundtrack.

Current conceptual label:

> **Interpretable image-conditioned musification for deterministic Sega Genesis-style procedural composition.**

Core path:

```text
image
→ multi-scale visual evidence
→ transformation / edge / anomaly evidence
→ mapping intelligence
→ musical genomes
→ composition rules
→ symbolic events / MIDI
→ YM2612 + SN76489-inspired local renderer
→ WAV + diagnostics
```

## 2. Non-negotiable project rules at v0.012

### Genesis only

The project direction is **Sega Genesis / Mega Drive only**.

Do not add SNES/SPC700/S-DSP logic or hybrid-console behavior unless the project owner explicitly changes direction.

### Deterministic identity

Same image + same settings + same variation must reproduce the same musical identity.

Variation may create related arrangements, but RIME should remain reproducible and inspectable.

### Image evidence must matter causally

Do not turn RIME into a black-box image classifier followed by a canned preset.

A musical decision should be traceable through:

```text
visual evidence → genome value → musical decision → generated event
```

### Negative space is not permission to repeatedly stop the song

Earlier versions confused darkness / space with absence of rhythmic foundation. That created perpetual intros and false starts.

After Launch, negative space should preferentially thin:

1. lead
2. ornament
3. upper harmony density

while protecting bass pulse / core percussion / foundation except during intentional structural events.

### Stop budget

Default law:

> **Maximum 3 substantial stops in any rolling 80-second window.**

A lead rest is not a stop. A stop means substantial collapse of the musical foundation for at least roughly one beat.

Excess collapses are bridged rather than allowed to restart the composition.

### Launch must mean Launch

The composition may begin atmospherically, but it must reach a finite Launch point and then commit.

Foundation occupancy and propulsion are different metrics. A sustained drone must not fool the engine into believing the groove has launched.

### Phrase memory

Do not return to bar-by-bar procedural amnesia.

Current accepted behavior includes:

- 8-bar drum/groove memory
- 8-bar melodic memory
- phrase roles such as statement, continuation, answer, breath, variant, development and turn
- bass/harmony/lead sharing a rhythmic pocket

### Human listening remains final authority

Programmatic quality tests protect structure. They do not prove a track sounds good.

Do not describe structural validation as an auditory judgment.

## 3. Why the current architecture exists

### v0.001

Initial proof of concept:

- image → reduced visual representation
- musical genome
- bars of drums/bass/harmony/lead
- MIDI/WAV/diagnostic output

Problem: different images could produce overly similar songs.

### v0.003–v0.004

Multi-resolution image analysis and image-derived Rhythm Genome were introduced.

Important mapping idea:

- lower image → kick tendency
- middle image → snare/percussion
- upper image → hats/high detail
- edges → accents

This reduced cross-image rhythm similarity but did not yet solve musical form.

### v0.005–v0.006

Dark-fantasy composition architecture became more explicit:

- RIME Sigil
- atmosphere axes/classes
- tonal/timbre genome
- functional form
- negative-space engine
- Gaussian persistence
- directional edges
- anomaly lane
- Solarized Shadow

Problem: silence and interruption were still too frequent.

### v0.007–v0.009

Continuity and Launch were developed.

Critical discovery:

> Foundation occupancy is not the same as propulsion.

A held drone could score as high foundation coverage while the song still felt like an intro.

Fixes:

- Continuity Timeline
- free-run before interruption
- Momentum Engine
- 3-stop / rolling-80-second law
- Launch + Drive Engine
- onset-based drive metrics
- groove commitment after Launch

### v0.010

Genesis drum production was rebuilt around hardware-inspired roles and darker 16-bit reference behavior.

Six current drum architectures:

- Dungeon Pulse
- Gothic Drive
- Occult Groove
- Uncanny Machine
- Macabre Action
- Sacred Weight

Core production roles:

- DAC-style kick/snare body
- SN76489-style noise hats/open hats
- YM2612-style pitched toms / metallic percussion
- FM bass and melodic roles

Extra percussion activity should usually come from hats/noise/ghost/metal layers rather than endlessly multiplying kick hits.

### v0.011

Melody and whole-band rhythm received the same memory/commitment treatment as drums.

Important accepted behaviors:

- 8-bar melodic phrase memory
- Sigil used as identity, not restarted every bar
- call/answer/development/breath
- register continuity
- selective PSG shadow of important FM lead attacks
- bass/harmony/lead share one rhythmic pocket
- lead may breathe while the band keeps moving

### v0.012

Mapping Intelligence formalized the visual-to-musical relationship.

The new development law became:

> **Change the image intentionally, and the music should change intentionally.**

Additions:

- equivariant musification
- Mapping Intelligence Genome
- macro / meso / micro jurisdiction
- Visual Kinetic Potential
- crossmodal priors
- hue demotion
- statistical salience / region hierarchy
- `--visual-authority`
- `--mapping-test`

The project owner listened to v0.012 output and explicitly judged the current result **acceptable**. Treat this version as the stable reference point.

## 4. Current visual hierarchy

### Macro

Large-scale / persistent visual structure.

Primary musical jurisdiction:

- tonic stability
- register depth
- bass weight
- large-form tendency
- persistent/drone structures

### Meso

Core structural detail and directional organization.

Primary musical jurisdiction:

- Visual Kinetic Potential
- groove energy
- phrase energy
- syncopation
- transient drive
- directional motion

### Micro

Fragile fine detail and transformed evidence.

Primary musical jurisdiction:

- PSG/noise surface
- hats
- small percussion
- ornament
- local FM/noise roughness

**Micro detail should not directly choose tonic or large form.**

## 5. Crossmodal priors currently intended

- brightness → spectral brightness / register height
- large dark mass → bass weight / low-register occupation
- fine detail → PSG/high-frequency activity
- roughness → local FM/noise roughness
- blur-persistent structure → sustain / drone / foundation
- contrast → accent / transient definition
- directional energy → kinetic potential / propulsion
- hue → timbral and harmonic color, **not direct tonic ownership**

These are priors, not universal perceptual laws. Keep them inspectable and testable.

## 6. Equivariance laboratory

`--mapping-test` applies controlled visual transformations while holding the composition's identity family stable.

Current full test:

- brightness +20%
- brightness -20%
- high contrast
- low contrast
- Gaussian blur r4
- desaturation
- horizontal flip
- center crop 80% resized to source dimensions

Experimental invariants are locked:

- tonic
- mode
- RIME Sigil
- Genesis drum architecture
- form architecture

Surface values are allowed to respond.

A 100% mapping score means the programmed transformations moved in the intended directions and invariants held. It does **not** mean every mapping has been perceptually proven ideal.

## 7. Known v0.012 regression state

A recurring glowing-figure test image used across v0.008–v0.012 produced the following structural v0.012 regression:

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

A later boss/stage-select image also produced a result the project owner explicitly accepted by listening. The exact subjective judgment is more important than chasing a perfect numerical score.

## 8. Development workflow

Before changing composition logic:

1. run existing smoke tests
2. generate the same known image on the current baseline
3. change one coherent subsystem at a time
4. run the same image again
5. compare structural metrics
6. listen to the output
7. run at least one contrasting image
8. use `--mapping-test` when changing visual mapping logic

Avoid broad rewrites that make it impossible to identify why a musical behavior changed.

## 9. Current recommended command

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

Mapping laboratory:

```bash
python run_rime.py image.png \
  --length 16 \
  --evolve 2 \
  --visual-authority 2 \
  --mapping-test full \
  --output output
```

## 10. Do not regress these solved problems

Future versions must be checked for the return of:

- different images producing nearly identical drum timing
- perpetual-intro behavior
- false starts
- foundation collapsing whenever the lead rests
- long unintentional silence
- bar-by-bar lead resets
- melody repeatedly restating the Sigil without development
- drums being too sparse to provide locomotion
- kick overuse as the only way to add percussion density
- bass/harmony/lead sounding like separate procedural generators
- small image details unexpectedly rewriting tonic/form
- controlled image edits creating unrelated songs

## 11. Current limitation

RIME's renderer is **Genesis-inspired**, not a cycle-accurate YM2612/SN76489 emulator.

The symbolic composer, mapping system and deterministic architecture are the central invention. More authentic chip rendering can be explored later without discarding the accepted composition/mapping behavior.

## 12. Front-load directive for a coding agent

Use the following as the first context for any major RIME coding session:

> You are working on RIME, a deterministic image-conditioned procedural Sega Genesis music composition engine. v0.012 is the accepted stable baseline. Read README.md, FRONTLOAD.md, MAPPING.md and VALIDATION.md before editing. Preserve Genesis-only direction, determinism, causal visual mapping, the 3-stops-per-rolling-80-seconds law, finite Launch, onset-based Drive, 8-bar drum and melody memory, shared band pocket, negative-space protection of the foundation, and the v0.012 macro/meso/micro Mapping Intelligence model. Do not reintroduce SNES logic. Do not treat test metrics as proof of auditory quality. Make narrow, testable changes and compare against v0.012 before declaring an improvement.
