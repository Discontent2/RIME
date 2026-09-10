# RIME UI v0.8
## ROUTE ARC + FX CONSTELLATION
### Canonical Full Build Specification

> **Status:** planned build specification. This document defines the target for RIME UI v0.8 and does not by itself mean the version has been implemented or released.

**Build target:** advance RIME from route-guided generation into deliberate song composition with an opening, journey, destination approach, closing, and a separate image-derived performance-FX universe.

The core idea is:

```text
IMAGE
  ↓
VISUAL GENOME
  ↓
PIT V2
  ↓
TRANSIT MAP V2
  ↓
COMPOSITION COMPASS
  ↓
ROUTE ARC
  ├─ Opening Gate
  ├─ Departure
  ├─ Journey
  ├─ Terminal Approach
  └─ Closing Gate
  ↓
CORE COMPOSITION
  ↓
FX CONSTELLATION
  ↓
FINAL GENESIS RENDER
```

The hierarchy must remain:

> **Compass decides why. Transit decides where. Route Arc decides how the song travels. PIT supplies musical material. FX Constellation transforms the journey.**

## 1. Primary goals

v0.8 should solve four things:

1. Songs need an intentional **opening** rather than merely starting at bar 1.
2. Songs need an intentional **ending** rather than simply running out of bars.
3. Route stations need to create gradual compositional movement.
4. Effects need to become structured musical events instead of random DSP decoration.

The result should feel like one piece of music traveling through a world.

## 2. Preserve everything already working

v0.8 inherits:

- stable normalized image identity
- Golden run protection
- Sonic Lock
- v0.012 accepted foundation
- Bass Behavior
- Pedal Intensity
- Pedal Register
- Bass Level
- Bass Depth
- PIT V2
- six PIT lanes
- PIT influence/sensitivity/persistence
- Transit Route A/B
- Composition Compass
- route influence
- Transit diagnostics
- alternate-route generation

Explicit user settings remain authoritative.

## 3. Sonic Lock contract

When **Sonic Lock ON**:

```text
Image analysis             ON
PIT analysis               ON
Transit Map generation     ON
Route Arc analysis         ON
FX Constellation analysis  ON

PIT audio modification     OFF
Transit audio modification OFF
Route Arc audio changes    OFF
FX processing              OFF
```

Sonic Lock is a microscope, not a remix button.

The accepted regression WAV must remain:

```text
1a6f3f730123a002707214a1f7e7782a9ebc73fdbf387bb7fca75329afeb61ad
```

for the established baseline regression image/settings.

## 4. Route Arc Engine

Add a new compositional layer above ordinary Transit interpolation.

A complete route becomes:

```text
OPENING GATE
     ↓
DEPARTURE
     ↓
FIRST MAJOR STATION
     ↓
ROUTE JOURNEY
     ↓
DESTINATION APPROACH
     ↓
DESTINATION
     ↓
CLOSING GATE
```

Opening and closing are not ordinary stations. They are dedicated state machines.

## 5. Opening Gate

### UI control

**Opening Mode**

```text
Auto
Cold Open
Fade
Signal Boot
Ritual
Motif Preview
Percussion Entry
Drone Gate
```

Default:

```text
Auto
```

### Opening Length

```text
Auto
2 bars
4 bars
8 bars
16 bars
```

Default:

```text
Auto
```

Auto should normally select **2 to 8 bars**.

### Opening behaviors

#### Cold Open

Immediate commitment.

```text
bass      immediate
drums     immediate
harmony   active
lead      immediate or within one bar
```

Best for high kinetic potential.

#### Fade

Progressive layer admission.

```text
atmosphere
→ harmony
→ bass
→ percussion
→ lead
```

#### Signal Boot

Mechanical Genesis startup without arcade sound-effect clichés.

Potential sequence:

```text
PSG pulse
→ FM transient
→ repeated signal
→ bass activation
→ drum lock
```

#### Ritual

Especially useful for Dungeon / Sacred / Occult imagery.

```text
bass pedal or drone
sparse FM harmony
incomplete Sigil
restrained percussion
gradual commitment
```

#### Motif Preview

Introduce only part of the RIME Sigil.

Example:

```text
full Sigil:
1 - ♭3 - 5 - 4

opening preview:
1 - - - 5
```

The complete statement appears later.

#### Percussion Entry

Drum identity appears before the melodic world fully opens.

#### Drone Gate

Blur-persistent visual structures establish a sustained low foundation before rhythmic travel.

## 6. Departure mechanic

The Opening Gate needs an explicit:

## DEPARTURE POINT

Example diagnostic:

```text
Opening Gate: Ritual
Opening: bars 1–4
Departure: bar 4
Route commitment: bar 5
```

After departure:

- bass foundation cannot randomly vanish
- core drums cannot repeatedly restart
- lead and harmony may breathe
- full-band collapses obey Momentum Engine rules
- stop budget remains max 3 substantial stops per rolling 80 seconds

This specifically protects against the old false-start problem.

## 7. Terminal Approach

The song should know it is nearing its destination.

Add:

**Terminal Approach**

```text
Auto
Short
Medium
Long
```

Default:

```text
Auto
```

Suggested meanings:

```text
Short   1–2 bars
Medium  3–4 bars
Long    5–8 bars
```

During the approach, RIME interpolates toward destination values.

Example:

```text
bar 25  tension .61
bar 26  tension .55
bar 27  tension .46
bar 28  tension .34
bar 29  destination reached
```

It can similarly interpolate:

- bass motion
- lead register
- harmony stability
- drum density
- PIT admission
- FX wetness
- Sigil completeness

No teleporting from one state to another.

## 8. Closing Gate

### Closing Mode

```text
Auto
Resolve
Return Sigil
Vanish
Loop Lock
Crash
Transmission Loss
Suspended
```

Default:

```text
Auto
```

### Closing Length

```text
Auto
2 bars
4 bars
8 bars
16 bars
```

Default:

```text
Auto
```

Auto normally uses **2 to 8 bars**.

## 9. Closing behaviors

### Resolve

Drive toward tonal stability.

```text
tension ↓
chromaticism ↓
tonic confidence ↑
harmonic instability ↓
```

### Return Sigil

The core visual-musical identity closes the piece.

The final Sigil may be:

- slower
- lower
- harmonized
- rhythmically simplified

but must remain recognizably related.

### Vanish

Recommended layer-removal hierarchy:

```text
lead
→ PSG detail
→ percussion
→ harmony
→ bass/drone
```

### Loop Lock

Designed for gameplay music.

Final harmony, bass and pickup rhythm should connect naturally to the opening state.

No giant reverb tail that destroys looping.

### Crash

One deliberate hard ending.

Possible combination:

```text
PCM impact
FM chord
bass strike
short silence
```

Never multiple fake endings.

### Transmission Loss

The music continues while the signal deteriorates:

```text
bandwidth ↓
noise ↑
sample rate ↓
delay fragments ↑
dry level ↓
```

### Suspended

Intentional unresolved ending:

```text
open fifth
suspended harmony
non-tonic bass
partial Sigil
```

Unresolved does not mean unfinished.

## 10. Transit Map V2

Add node classifications:

| Node | Meaning |
|---|---|
| ◇ Opening Gate | entry mechanism |
| ● Major Station | substantial compositional state |
| • Minor Station | subtle development |
| ✦ Interchange | branch / transformation opportunity |
| ○ Optional Spur | route-specific side event |
| ◉ Terminal Approach | destination preparation |
| ◎ Destination | Compass target |
| ▽ Closing Gate | exit mechanism |

A typical route:

```text
◇ RITUAL GATE
│
● LOWER TERMINAL
│
● BASS ANCHOR
├────○ GLASS SPUR
│
✦ RED JUNCTION
│
● CROWN RELAY
│
◉ RETURN APPROACH
│
◎ HOME
│
▽ SIGIL CLOSE
```

## 11. Station mechanics

A station should describe a **musical state**, not a note.

Example:

```text
RED JUNCTION

Energy        +0.08
Tension       +0.11
Density       +0.05
Lead register +2 semitones
Bass motion   +1 onset/bar
Harmony       shorter attacks
PSG detail    moderate
PCM event     eligible
```

The route engine interpolates into and out of this state.

Major stations can modify larger-scale values.

Minor stations should usually modify only a few percent.

## 12. FX Constellation

This is a separate navigation system.

```text
TRANSIT MAP
= geography of the composition

FX CONSTELLATION
= alternate sonic universe surrounding it
```

PIT asks:

> What musical material exists?

Transit asks:

> Where can the composition travel?

Constellation asks:

> How can the sound be transformed while traveling?

## 13. Universe model

Define:

```text
UNIVERSE A
main composition

UNIVERSE B
effects interpretation
```

Universe B must **not** silently own:

- tonic
- mode
- RIME Sigil
- primary route
- destination
- bass behavior override
- section count

Universe B can own:

- filtering
- echo
- reverb
- degradation
- stutter
- reverse
- freeze
- modulation
- distortion
- noise
- temporary fragmentation

## 14. FX Constellation source

UI:

**Constellation Source**

```text
Auto
Original
Horizontal Mirror
Solar Shadow
Anomaly Map
Off
```

Default:

```text
Auto
```

Horizontal Mirror is especially important because it gives a related alternate universe without changing the visual identity.

Future:

```text
Second Image
```

but dual-image support is not required for v0.8.

## 15. FX families

The DSP should be SP-404-inspired in workflow, without requiring external software or copying specific proprietary implementations.

### Filter

```text
Low-pass
High-pass
Band-pass
Dark Filter
Resonant Sweep
Isolator-style split
Telephone Band
```

### Space

```text
Room
Dark Hall
Long Reverb
Metallic Chamber
Frozen Tail
Short Ambience
```

### Time

```text
Delay
Feedback Echo
Tape-like Echo
Slap
Rhythmic Repeat
```

### Texture

```text
Noise
Vinyl-like wear
Cassette instability
Bit reduction
Sample-rate reduction
Digital grit
FM dirt
```

### Motion

```text
Pitch wobble
Chorus-like drift
Flange-like sweep
Phaser-like motion
Tremolo
Pan movement
```

### Performance

```text
Stutter
Retrigger
Scatter-like fragmentation
Reverse
Freeze
Gate
DJ-style stop
Beat repeat
```

### Destruction

```text
Saturation
Overdrive
Hard distortion
Ring-mod-like breakup
Heavy crush
Solar fracture
Transmission failure
```

Destruction nodes should remain rare.

## 16. FX Constellation controls

Create a drawer:

## FX CONSTELLATION

Controls:

```text
Constellation Source
Auto / Original / Mirror / Solar / Anomaly / Off

FX Influence
0–100%

FX Density
Sparse / Balanced / Dense

FX Discipline
Strict / Balanced / Wild

FX Route
Auto / A / B / Minimal

Filter
Auto / Off / Low / Medium / High

Delay
Auto / Off / Low / Medium / High

Reverb
Auto / Off / Low / Medium / High

Texture
Auto / Off / Low / Medium / High

Crush
Auto / Off / Low / Medium / High

Stutter
Auto / Off / Rare / Moderate

Reverse
Auto / Off / Rare / Moderate

Freeze
Auto / Off / Rare / Moderate
```

Defaults:

```text
Source      Auto
Influence   30%
Density     Sparse
Discipline  Strict
FX Route    Auto

all individual FX:
Auto
```

## 17. FX Discipline

### Strict

Default.

- preserve groove
- preserve bass foundation
- prefer filtering, echo and ambience
- rare reverse
- rare freeze
- short stutters
- effects return cleanly

### Balanced

More noticeable performance processing.

### Wild

Allows stronger:

- fragmentation
- reverse
- crush
- pitch movement
- stutter
- long delay behavior

Still cannot override core compositional identity.

## 18. FX Event Budget

Major FX must obey a budget.

Default:

```text
Maximum major FX events:
3 per rolling 80 seconds
```

Major FX include:

- freeze
- reverse
- heavy stutter
- large filter collapse
- severe crush
- transmission failure
- long delay takeover

Minor coloration does not count as a major event.

## 19. Visual-to-FX analysis

Suggested relationships:

```text
brightness
→ spectral openness

roughness
→ distortion / crush

blur persistence
→ reverb / freeze

fine detail
→ stutter / retrigger

edge density
→ modulation speed

anomaly
→ rarity + intensity

symmetry
→ delay / repetition

color contrast
→ modulation character
```

A star should generally require agreement from several visual features.

Example:

```text
high anomaly
high edge strength
low persistence
fine detail

→ PERFORMANCE STAR
```

while:

```text
dark mass
high persistence
low detail

→ SPACE / FILTER STAR
```

## 20. Constellation Map output

Generate:

```text
*_fx_constellation.png
```

Visual concept:

```text
              ✦ DARK HALL
             /
● FILTER ───✧ DELAY
 \            \
  ✦ TEXTURE   ✦ FREEZE
      \        /
       ✧ CRUSH
          \
           ◎ RETURN CLEAN
```

Bright route:

```text
selected FX journey
```

Dim routes:

```text
available but unused possibilities
```

Default terminal node should normally be:

```text
RETURN CLEAN
```

unless Closing Mode intentionally wants an effected ending.

## 21. Transit + FX interaction

Effects attach to **stations**, not merely timestamps.

Example:

```text
Transit:
Red Junction

FX:
Short Tape Echo

Trigger:
arrival

Duration:
0.5 bar
```

This makes Route A and Route B remain coherent even when station timing changes.

Possible relationships:

```text
approaching station
arriving
occupying
departing
between stations
closing gate
```

## 22. Opening FX rules

Before departure, favor:

- filtering
- light noise
- ambience
- short echo
- mild degradation

Avoid by default:

- heavy stutter
- reverse takeover
- freeze
- heavy crush

RIME should introduce itself before aggressive transformation.

## 23. Mid-song FX rules

Interchanges and optional spurs are ideal places for:

- delay
- stutter
- retrigger
- short reverse
- filter sweeps
- crush
- spatial changes

Typical event duration:

```text
0.25–4 bars
```

## 24. Closing FX rules

### Resolve

Effects gradually withdraw.

### Return Sigil

Clean up before the final Sigil.

### Vanish

Increase reverb while decreasing dry signal.

### Transmission Loss

Increase degradation progressively.

### Crash

Minimal tail.

### Loop Lock

No effect state may make the loop seam obvious.

## 25. Route Arc UI drawer

Create:

## ROUTE ARC

```text
Opening Mode
Auto / Cold Open / Fade / Signal Boot / Ritual /
Motif Preview / Percussion Entry / Drone Gate

Opening Length
Auto / 2 / 4 / 8 / 16

Terminal Approach
Auto / Short / Medium / Long

Closing Mode
Auto / Resolve / Return Sigil / Vanish /
Loop Lock / Crash / Transmission Loss / Suspended

Closing Length
Auto / 2 / 4 / 8 / 16
```

All defaults:

```text
Auto
```

## 26. Preserve Bass Console authority

Route Arc may alter:

- bass activity
- note duration
- velocities
- occasional movement
- section emphasis

It must not silently replace explicit selections.

Example:

```text
Bass Behavior = PEDAL
```

means Route Arc cannot change it to Walk.

Likewise:

```text
Bass Level = 65%
```

must remain 65%.

Explicit controls outrank Auto systems.

## 27. PIT relationship

Final hierarchy:

```text
COMPASS
  ↓
TRANSIT
  ↓
ROUTE ARC
  ↓
PIT ADMISSION
  ↓
FX CONSTELLATION
```

Interpretation:

```text
Compass:
where are we trying to go?

Transit:
which road do we take?

Route Arc:
how do we move along that road?

PIT:
what instruments/material are available here?

FX:
what happens to that material sonically?
```

This is the point where RIME becomes a compositional architecture rather than a stack of mappings.

## 28. Composition Blueprint

Generate:

```text
*_composition_blueprint.json
```

Minimum conceptual structure:

```json
{
  "opening_gate": {},
  "departure": {},
  "transit_route": {},
  "stations": [],
  "terminal_approach": {},
  "destination": {},
  "closing_gate": {},
  "fx_constellation": {},
  "fx_events": [],
  "compass": {}
}
```

## 29. FX Event JSON

Each applied event records:

```text
effect
family
station
trigger relationship
start bar
end bar
strength
wet amount
constellation source
visual evidence
```

Example:

```json
{
  "effect": "dark_delay",
  "family": "time",
  "station": "Red Junction",
  "relationship": "arrival",
  "start_bar": 14.0,
  "end_bar": 14.75,
  "strength": 0.31,
  "source": "mirror_anomaly"
}
```

## 30. Audio rendering

Effects should initially use deterministic local DSP.

Implementable v0.8 DSP:

```text
low/high-pass filtering
simple resonant filtering
delay
feedback delay
short ambience/reverb
bit-depth reduction
sample-rate reduction
saturation
noise
amplitude gate
short reverse buffers
repeat/stutter buffers
pitch wobble
freeze buffer
```

No external plugin dependency.

Same:

```text
image + settings + route + variation
```

must produce the same result.

## 31. MIDI principle

Default effects alter WAV, not musical MIDI.

Therefore:

```text
FX OFF vs FX AUTO

MIDI:
identical whenever composition is unchanged

WAV:
different
```

Stutter/retrigger may later optionally become MIDI events, but v0.8 should keep FX rendering conceptually separate.

## 32. Result panel

Add:

## COMPOSITION

```text
Opening
Ritual / 4 bars

Departure
Bar 5

Route
A

Stations
7

Compass
Return

Terminal Approach
4 bars

Closing
Return Sigil / 4 bars
```

Then:

## PARALLEL FX UNIVERSE

```text
Source
Horizontal Mirror

Route
B

FX Visits
3

Dominant FX
Dark Filter
Short Delay
Frozen Tail

Influence
30%

Discipline
Strict
```

## 33. Output buttons

Result panel should expose:

```text
WAV
MIDI
GENOME JSON
COMPOSITION BLUEPRINT
RIME VISION
PIT MAP
PIT JSON
TRANSIT MAP
TRANSIT JSON
FX CONSTELLATION
FX EVENT JSON
```

## 34. Diagnostic chain

Display conceptually:

```text
SOURCE IMAGE
     ↓
RIME VISION
     ↓
PIT MAP
     ↓
TRANSIT MAP
     ↓
FX CONSTELLATION
```

That lets the user see:

```text
what RIME saw
↓
what instruments it discovered
↓
where the song traveled
↓
what alternate sonic universe affected it
```

## 35. Golden run metadata

Future Golden records should include:

```text
pixel fingerprint
key / mode
Sigil
bass behavior
Opening Gate
departure bar
Transit route
Compass destination
Terminal Approach
Closing Gate
FX source
FX route
WAV fingerprint
```

This gives meaningful Golden comparisons beyond audio hashes.

## 36. Quality diagnostics

Add Route Arc warnings:

```text
opening too long
multiple apparent launches
journey too short
destination approached too abruptly
closing begins too early
multiple apparent endings
closing masks Sigil
```

Hard warning:

```text
FALSE ENDINGS > 1
```

Add FX warnings:

```text
major FX budget exceeded
FX wetness sustained too long
stutter obscures groove
filter removes bass foundation
reverse frequency too high
closing FX obscures resolution
```

Warnings should inform rather than silently override explicit settings.

## 37. Recommended default generation

With all new controls on Auto, an example might resolve to:

```text
WORLD
Dungeon + Sacred

OPENING
Ritual
4 bars

DEPARTURE
Bar 5

TRANSIT
Route A
7 stations

COMPASS
Return

TERMINAL APPROACH
4 bars

CLOSING
Return Sigil
4 bars

CONSTELLATION SOURCE
Mirror

FX ROUTE
B

FX VISITS
3

FX INFLUENCE
30%

DISCIPLINE
Strict
```

The listener should perceive one continuous journey.

## 38. Development priority

### P0, required for release

```text
Opening Gate
Departure point
Terminal Approach
Closing Gate
Route interpolation
Transit node classes
FX Constellation generation
Filter
Delay
Reverb
Crush
FX scheduling
Composition Blueprint
new diagnostics
Sonic Lock regression
```

### P1, strongly desired

```text
Stutter
Reverse
Freeze
Mirror constellation
Solar constellation
Anomaly constellation
Golden Route metadata
```

### P2, defer if necessary

```text
second uploaded image
interactive station dragging
clickable FX stars
independent route seed
independent FX seed
manual route editing
```

Do not let P2 delay the testable version.

## 39. Validation matrix

| Test | Expected result |
|---|---|
| Sonic Lock | accepted WAV remains byte-identical |
| Auto vs Cold Open | body remains related, opening audibly changes |
| Resolve vs Vanish | route body remains related, ending changes |
| Route A vs Route B | same world/destination, different journey |
| FX Off vs Auto | same composition/MIDI, different WAV |
| FX Influence 0% | FX Constellation produces no audio change |
| Mirror vs Original FX | related but different constellation path |
| Same image/settings twice | identical map, blueprint, MIDI and WAV |
| Bass explicit override | Route Arc does not replace it |
| Closing Gate | no more than one convincing final ending |

## 40. Acceptance criteria

v0.8 passes only when:

```text
✓ the track clearly enters

✓ departure is identifiable

✓ the groove remains committed afterward

✓ station-to-station changes are gradual

✓ Route A and Route B remain related

✓ Terminal Approach creates anticipation

✓ the ending feels intentional

✓ FX attach to compositional moments

✓ FX do not constantly interrupt the song

✓ PIT remains subordinate to composition

✓ Bass Console remains authoritative

✓ Constellation diagnostics are understandable

✓ deterministic generation survives

✓ Sonic Lock remains safe
```

## 41. Version identity

```text
RIME UI v0.8
ROUTE ARC + FX CONSTELLATION
```

Banner:

```text
PIT V2
TRANSIT V2
COMPOSITION COMPASS
ROUTE ARC
FX CONSTELLATION
```

Design sentence for `README.md`, `UI_FRONTLOAD.md`, and code comments:

> **The Transit Map determines where the music travels. The Compass determines why. The Route Arc determines how it enters and leaves. The FX Constellation determines what strange weather it passes through.**

This document is the canonical RIME UI v0.8 build target.