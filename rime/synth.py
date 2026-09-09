from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple, TYPE_CHECKING
import wave

import numpy as np

from .composer import NoteEvent

if TYPE_CHECKING:
    from .genome import MusicalGenome


def _midi_hz(note: int) -> float:
    return 440.0 * (2.0 ** ((note - 69) / 12.0))


def _adsr(n: int, sr: int, attack: float, decay: float, sustain: float, release: float) -> np.ndarray:
    if n <= 1:
        return np.ones(max(1, n), dtype=np.float32)
    env = np.ones(n, dtype=np.float32) * sustain
    a = min(n, max(1, int(attack * sr)))
    d = min(max(0, n - a), max(1, int(decay * sr)))
    r = min(n, max(1, int(release * sr)))
    env[:a] = np.linspace(0.0, 1.0, a, dtype=np.float32)
    if d > 0:
        env[a:a + d] = np.linspace(1.0, sustain, d, dtype=np.float32)
    if r > 0:
        env[-r:] *= np.linspace(1.0, 0.0, r, dtype=np.float32)
    return env


def _fm_chain(freq: float, t: np.ndarray, ratios: tuple[float, float, float, float], indexes: tuple[float, float, float]) -> np.ndarray:
    op4 = np.sin(2 * np.pi * freq * ratios[3] * t)
    op3 = np.sin(2 * np.pi * freq * ratios[2] * t + indexes[2] * op4)
    op2 = np.sin(2 * np.pi * freq * ratios[1] * t + indexes[1] * op3)
    return np.sin(2 * np.pi * freq * ratios[0] * t + indexes[0] * op2)


def _ym_style_voice(freq: float, duration: float, sr: int, velocity: int, role: str, g: "MusicalGenome | None") -> np.ndarray:
    """Image-conditioned 4-operator FM lab voice. Still not a cycle-accurate YM2612."""
    n = max(1, int(duration * sr))
    t = np.arange(n, dtype=np.float32) / sr
    amp = velocity / 127.0
    if g is None:
        dark = cold = harsh = metal = decay = bass_w = openness = noise = 0.5
    else:
        tt = g.timbre
        tr = g.transforms
        dark, cold = tt.darkness, tt.coldness
        # Gaussian persistence becomes timbral evidence: broad persistent shapes
        # smooth carriers, while fragile detail preserves cutting upper partials.
        harsh = tt.fm_harshness * (0.72 + 0.48 * tr.fragile_detail) * (1.04 - 0.22 * tr.blur_softness)
        metal = min(1.0, tt.metallicity * (0.82 + 0.34 * tr.edge_fine))
        decay = min(1.0, tt.decay * (0.88 + 0.28 * tr.large_structure_persistence))
        bass_w, openness, noise = tt.bass_weight, tt.chord_openness, tt.noise_amount

    if role == "bass":
        ratios = (1.0, 2.0 + 0.8 * metal, 1.0, 0.5)
        indexes = (2.5 + 2.7 * harsh, 1.1 + 1.1 * bass_w, 0.55 + 0.65 * metal)
        sig = _fm_chain(freq, t, ratios, indexes)
        sub = np.sin(2 * np.pi * freq * 0.5 * t)
        sig = (0.78 - 0.12 * dark) * sig + (0.22 + 0.12 * dark) * sub
        env = _adsr(n, sr, 0.002 + 0.006 * (1 - bass_w), 0.045 + 0.08 * decay, 0.55 + 0.28 * bass_w, min(0.14, duration * (0.25 + 0.22 * decay)))
        return ((0.26 + 0.12 * bass_w) * amp * sig * env).astype(np.float32)

    if role == "lead":
        ratios = (1.0, 2.0 + 1.2 * metal, 3.0 + 2.0 * cold, 5.0 + 2.0 * metal)
        indexes = (2.2 + 4.0 * harsh, 0.85 + 1.25 * metal, 0.32 + 0.75 * cold)
        sig = _fm_chain(freq, t, ratios, indexes)
        body = np.sin(2 * np.pi * freq * t)
        # Darker images keep a clearer carrier body; harshness stays local in the modulators.
        sig = (0.58 + 0.28 * harsh) * sig + (0.42 - 0.20 * harsh) * body
        env = _adsr(n, sr, 0.004 + 0.006 * (1 - harsh), 0.055 + 0.12 * decay, 0.58 + 0.20 * (1 - dark), min(0.20, duration * (0.26 + 0.30 * decay)))
        return (0.22 * amp * sig * env).astype(np.float32)

    if role == "friction":
        ratios = (1.0, 3.0 + 2.5 * metal, 5.0 + 3.0 * cold, 7.0)
        indexes = (4.0 + 5.0 * harsh, 1.8 + 2.0 * metal, 0.9 + 1.4 * noise)
        sig = _fm_chain(freq, t, ratios, indexes)
        env = _adsr(n, sr, 0.002, 0.04 + 0.06 * decay, 0.18, min(0.18, duration * 0.48))
        return ((0.08 + 0.08 * harsh) * amp * sig * env).astype(np.float32)

    if role == "psg_shadow":
        # Quiet SN76489-style square shadow used behind selected FM lead notes.
        duty = np.sign(np.sin(2 * np.pi * freq * t))
        overtone = 0.22 * np.sign(np.sin(2 * np.pi * freq * 2.0 * t))
        sig = 0.82 * duty + overtone
        env = _adsr(n, sr, 0.0015, 0.025 + 0.045 * decay, 0.44, min(0.10, duration * 0.26))
        return (0.075 * amp * sig * env).astype(np.float32)

    # Harmony: image-conditioned hollow/plucked FM with selective PSG shadow.
    ratios = (1.0, 2.0 + 1.3 * metal, 0.5 + 1.5 * openness, 4.0 + 2.0 * cold)
    indexes = (1.4 + 2.2 * harsh, 0.65 + 1.0 * metal, 0.24 + 0.56 * cold)
    fm = _fm_chain(freq, t, ratios, indexes)
    psg = np.sign(np.sin(2 * np.pi * freq * t))
    psg_mix = min(0.28, 0.04 + 0.16 * metal + 0.08 * cold)
    sig = (1.0 - psg_mix) * fm + psg_mix * psg
    sustain = 0.24 + 0.30 * decay
    env = _adsr(n, sr, 0.004 + 0.012 * openness, 0.10 + 0.18 * decay, sustain, min(0.24, duration * (0.28 + 0.34 * decay)))
    return (0.17 * amp * sig * env).astype(np.float32)


def _noise(n: int, rng: np.random.Generator) -> np.ndarray:
    raw = rng.uniform(-1.0, 1.0, n).astype(np.float32)
    hp = raw.copy()
    if n > 1:
        hp[1:] = raw[1:] - 0.78 * raw[:-1]
    return hp


def _drum(note: int, duration: float, sr: int, velocity: int, rng: np.random.Generator, g: "MusicalGenome | None") -> np.ndarray:
    n = max(1, int(duration * sr))
    t = np.arange(n, dtype=np.float32) / sr
    amp = velocity / 127.0
    noise_sig = _noise(n, rng)
    noise_amt = g.timbre.noise_amount if g is not None else 0.5
    bass_w = g.timbre.bass_weight if g is not None else 0.5
    rough = g.rhythm.roughness if g is not None else 0.5
    if note == 36:
        freq = (92 + 26 * bass_w) * np.exp(-t * (17 + 7 * rough)) + (35 + 8 * bass_w)
        phase = 2 * np.pi * np.cumsum(freq) / sr
        click = noise_sig * np.exp(-t * 95)
        sig = (0.94 - 0.08 * noise_amt) * np.sin(phase) * np.exp(-t * (12 + 5 * rough)) + (0.06 + 0.08 * noise_amt) * click
        return ((0.38 + 0.10 * bass_w) * amp * sig).astype(np.float32)
    if note == 38:
        tone = np.sin(2 * np.pi * (170 + 55 * rough) * t) * np.exp(-t * 21)
        sig = (0.62 + 0.24 * noise_amt) * noise_sig * np.exp(-t * (20 + 10 * rough)) + (0.38 - 0.20 * noise_amt) * tone
        return (0.28 * amp * sig).astype(np.float32)
    if note in (42, 46):
        decay_rate = (62 if note == 42 else 25) - 8 * noise_amt
        sig = noise_sig * np.exp(-t * max(10, decay_rate))
        return ((0.10 + 0.07 * noise_amt) * amp * sig).astype(np.float32)
    if note in (45, 47, 50):
        # YM2612-style pitched tom: brief FM body with an image-conditioned fall.
        base = {45: 96, 47: 126, 50: 166}[note]
        fm_bias = g.genesis_drums.fm_percussion_bias if g is not None else 0.5
        freq = base * np.exp(-t * (3.4 + 1.6 * fm_bias))
        phase = 2 * np.pi * np.cumsum(freq) / sr
        mod = np.sin(phase * (1.50 + 0.85 * fm_bias)) * (1.0 + 2.2 * fm_bias)
        sig = np.sin(phase + mod) * np.exp(-t * (11 + 5 * fm_bias)) + 0.06 * noise_amt * noise_sig * np.exp(-t * 28)
        return ((0.22 + 0.08 * fm_bias) * amp * sig).astype(np.float32)
    if note == 56:
        # Inharmonic YM2612 metallic punctuation, intentionally short and local.
        fm_bias = g.genesis_drums.fm_percussion_bias if g is not None else 0.6
        c = 360.0 + 160.0 * fm_bias
        mod = np.sin(2*np.pi*c*1.73*t) * (2.4 + 4.0*fm_bias)
        sig = np.sin(2*np.pi*c*t + mod) * np.exp(-t*(15 + 7*rough))
        sig += 0.28 * np.sin(2*np.pi*c*2.41*t) * np.exp(-t*20)
        return (0.15 * amp * sig).astype(np.float32)
    if note == 37:
        # Tiny ghost click: PSG/FM transient that adds motion without snare weight.
        hp = noise_sig
        sig = hp * np.exp(-t * (95 + 45 * rough))
        return ((0.05 + 0.04 * noise_amt) * amp * sig).astype(np.float32)
    if note == 49:
        # DAC/PSG crash hybrid used only as a structural/fill accent.
        hp = noise_sig
        sig = (0.72*hp + 0.28*noise_sig) * np.exp(-t * (7.5 + 5 * rough))
        return ((0.12 + 0.07 * noise_amt) * amp * sig).astype(np.float32)
    return (0.10 * amp * noise_sig * np.exp(-t * 40)).astype(np.float32)


def _pan_gains(pan: float) -> Tuple[float, float]:
    angle = (pan + 1.0) * np.pi / 4.0
    return float(np.cos(angle)), float(np.sin(angle))


def render_wav(
    events: Dict[str, List[NoteEvent]],
    tempo_bpm: int,
    bars: int,
    output_path: str | Path,
    sample_rate: int = 24000,
    steps_per_beat: int = 4,
    seed: int = 0,
    genome: "MusicalGenome | None" = None,
) -> None:
    seconds_per_beat = 60.0 / tempo_bpm
    seconds_per_step = seconds_per_beat / steps_per_beat
    total_steps = bars * 16
    total_seconds = total_steps * seconds_per_step
    total_samples = int(total_seconds * sample_rate)
    mix = np.zeros((total_samples, 2), dtype=np.float32)
    rng = np.random.default_rng(seed)
    role_pan = {"bass": 0.0, "harmony": -0.28, "lead": 0.24, "drums": 0.0}

    for role, evs in events.items():
        for idx, e in enumerate(evs):
            start = int(e.start_step * seconds_per_step * sample_rate)
            duration = max(0.025, e.duration_steps * seconds_per_step)
            if role == "drums":
                tone = _drum(e.pitch, min(duration, 0.62 if e.pitch not in (49, 46) else (1.15 if e.pitch == 49 else 0.78)), sample_rate, e.velocity, rng, genome)
                pan = -0.18 if e.pitch == 42 and idx % 2 == 0 else (0.18 if e.pitch in (46, 49) else 0.0)
            else:
                if role == "harmony" and e.channel == 3:
                    voice = "friction"
                elif role == "lead" and e.channel == 4:
                    voice = "psg_shadow"
                else:
                    voice = role
                tone = _ym_style_voice(_midi_hz(e.pitch), duration, sample_rate, e.velocity, voice, genome)
                pan = (0.34 if voice == "friction" else role_pan[role])
            left, right = _pan_gains(pan)
            end = min(total_samples, start + len(tone))
            if end > start:
                seg = tone[: end - start]
                mix[start:end, 0] += seg * left
                mix[start:end, 1] += seg * right

    if genome is not None and genome.continuity.main_enabled and genome.continuity.main_start_step is not None and genome.continuity.main_end_step is not None:
        start_step = genome.continuity.main_start_step
        end_step = min(total_steps, genome.continuity.main_end_step)
        a = int(start_step * seconds_per_step * sample_rate)
        b = min(total_samples, int(end_step * seconds_per_step * sample_rate))
        if b > a:
            seg = mix[a:b]
            inst = genome.transforms.threshold_instability
            shadow = genome.transforms.shadow_strength
            # v0.007 treats solarization as an event that interrupts an already
            # established song, not as a pre-declared four-bar section.
            local_drive = 1.15 + 1.25 * inst + 0.65 * shadow
            seg = np.tanh(seg * local_drive)
            bits = int(round(8 - 3.0 * inst - 1.0 * shadow))
            bits = max(4, min(8, bits))
            levels = float((1 << bits) - 1)
            seg = np.round(np.clip(seg, -1.0, 1.0) * levels) / levels
            veil = rng.uniform(-1.0, 1.0, seg.shape).astype(np.float32)
            seg = seg + veil * (0.004 + 0.012 * inst)
            mix[a:b] = seg

    if genome is not None and genome.continuity.foreshadow_enabled and genome.continuity.foreshadow_start_step is not None and genome.continuity.foreshadow_end_step is not None:
        a = int(genome.continuity.foreshadow_start_step * seconds_per_step * sample_rate)
        b = min(total_samples, int(genome.continuity.foreshadow_end_step * seconds_per_step * sample_rate))
        if b > a:
            seg = mix[a:b]
            # A foreshadow is only a hairline crack: softer gain, slight
            # quantization and no full breakdown-style destruction.
            shadow = genome.transforms.shadow_strength
            seg = np.tanh(seg * (1.05 + 0.40 * shadow)) * (0.82 + 0.10 * (1.0 - shadow))
            bits = 8 if genome.transforms.threshold_instability < 0.45 else 7
            levels = float((1 << bits) - 1)
            seg = np.round(np.clip(seg, -1.0, 1.0) * levels) / levels
            mix[a:b] = seg

    drive = 1.06 + (0.22 * genome.timbre.fm_harshness if genome is not None else 0.12)
    mix = np.tanh(mix * drive)
    peak = float(np.max(np.abs(mix))) if mix.size else 1.0
    if peak > 0:
        mix = mix / peak * 0.89
    pcm = (mix * 32767.0).astype(np.int16)
    with wave.open(str(output_path), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm.tobytes())
