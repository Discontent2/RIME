from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import List, Sequence, Tuple
import math

import numpy as np

from .analyzer import MultiScaleAnalysis, ScaleAnalysis


@dataclass
class RhythmGenome:
    # Image-derived rhythmic control axes.
    pulse_density: float
    kick_density: float
    snare_density: float
    hat_density: float
    syncopation: float
    hat_irregularity: float
    swing: float
    rest_probability: float
    accent_asymmetry: float
    fill_probability: float
    backbeat_strength: float
    bass_drum_lock: float
    groove_cycle_length: int
    doubletime_bias: float
    halftime_bias: float
    percussion_weight: float

    # Mood axes. These are intentionally independent so two equally dark images
    # do not collapse to one groove type.
    weight: float
    motion: float
    openness: float
    order: float
    threat: float
    warmth: float
    urgency: float
    roughness: float
    space: float

    # Sixteen-step image projections used directly by the beat generator.
    kick_lane: List[float]
    snare_lane: List[float]
    hat_lane: List[float]
    accent_lane: List[float]
    rhythm_profile: str
    phase_offset: int
    image_rhythm_strength: int = 2

    def to_dict(self) -> dict:
        return asdict(self)


def _clamp01(v: float) -> float:
    return float(np.clip(v, 0.0, 1.0))


def _norm_lane(values: Sequence[float], floor: float = 0.08) -> List[float]:
    arr = np.asarray(values, dtype=np.float32)
    if arr.size == 0:
        return [0.5] * 16
    lo, hi = float(arr.min()), float(arr.max())
    if hi - lo < 1e-6:
        out = np.full_like(arr, 0.5)
    else:
        out = (arr - lo) / (hi - lo)
    out = floor + (1.0 - floor) * out
    return [float(v) for v in out]


def _resample16(values: Sequence[float]) -> List[float]:
    arr = np.asarray(values, dtype=np.float32)
    if arr.size == 16:
        return [float(v) for v in arr]
    xs = np.linspace(0.0, 1.0, arr.size)
    target = np.linspace(0.0, 1.0, 16)
    return [float(v) for v in np.interp(target, xs, arr)]


def _pixels_to_arrays(scale: ScaleAnalysis) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    rgb = np.asarray(scale.pixels_rgb, dtype=np.float32) / 255.0
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    maxc = np.max(rgb, axis=2)
    minc = np.min(rgb, axis=2)
    sat = np.divide(maxc - minc, np.maximum(maxc, 1e-6))
    gx = np.zeros_like(lum)
    gy = np.zeros_like(lum)
    if lum.shape[1] > 1:
        gx[:, 1:] = np.abs(np.diff(lum, axis=1))
    if lum.shape[0] > 1:
        gy[1:, :] = np.abs(np.diff(lum, axis=0))
    edge = np.clip(gx + gy, 0.0, 1.0)
    return lum, sat, edge


def _band_projection(lum: np.ndarray, sat: np.ndarray, edge: np.ndarray) -> tuple[List[float], List[float], List[float], List[float]]:
    h = lum.shape[0]
    t1 = max(1, h // 3)
    t2 = max(t1 + 1, 2 * h // 3)

    upper_l, upper_s, upper_e = lum[:t1], sat[:t1], edge[:t1]
    mid_l, mid_s, mid_e = lum[t1:t2], sat[t1:t2], edge[t1:t2]
    low_l, low_s, low_e = lum[t2:], sat[t2:], edge[t2:]

    # Lower mass/darkness strongly suggests kick positions.
    kick = 0.47 * (1.0 - low_l.mean(axis=0)) + 0.36 * low_e.mean(axis=0) + 0.17 * low_s.mean(axis=0)

    # Mid-frame edges and local contrast suggest snare/percussive accents.
    mid_contrast = np.abs(mid_l - mid_l.mean(axis=0, keepdims=True)).mean(axis=0)
    snare = 0.50 * mid_e.mean(axis=0) + 0.30 * mid_contrast + 0.20 * (1.0 - mid_l.mean(axis=0))

    # Fine bright/edge detail near the top controls hats and high percussion.
    upper_delta = np.zeros(upper_l.shape[1], dtype=np.float32)
    if upper_l.shape[1] > 1:
        upper_delta[1:] = np.abs(np.diff(upper_l.mean(axis=0)))
    hat = 0.50 * upper_e.mean(axis=0) + 0.24 * upper_s.mean(axis=0) + 0.18 * upper_delta + 0.08 * upper_l.mean(axis=0)

    # Accent lane integrates all regions but prioritizes local discontinuities.
    all_delta = np.zeros(lum.shape[1], dtype=np.float32)
    if lum.shape[1] > 1:
        all_delta[1:] = np.abs(np.diff(lum.mean(axis=0)))
    accent = 0.52 * edge.mean(axis=0) + 0.28 * all_delta + 0.20 * np.abs(lum.mean(axis=0) - lum.mean())

    return tuple(_norm_lane(_resample16(v)) for v in (kick, snare, hat, accent))


def _hue_warmth(hue: float, saturation: float) -> float:
    # Circular closeness to red/orange around hue 0.06, diminished when the
    # image is nearly monochrome.
    d = abs(hue - 0.06)
    d = min(d, 1.0 - d)
    closeness = max(0.0, 1.0 - d / 0.36)
    return _clamp01(0.18 + 0.82 * closeness * (0.35 + 0.65 * saturation))


def _profile(weight: float, motion: float, order: float, threat: float, urgency: float, space: float, roughness: float) -> str:
    if space > 0.70 and motion < 0.40:
        return "suspended"
    if threat > 0.66 and urgency < 0.43:
        return "ritual"
    if order > 0.69 and motion > 0.56:
        return "motoric"
    if roughness > 0.66 and motion > 0.54:
        return "fractured"
    if threat > 0.58 and motion < 0.58:
        return "stalking"
    if urgency > 0.66:
        return "driving"
    if weight > 0.66 and motion < 0.48:
        return "heavy_pulse"
    return "adaptive"


def build_rhythm_genome(ms: MultiScaleAnalysis, density_bias: int = 0, edge_bias: int = 1, rhythm_strength: int = 2, identity_seed: int | None = None) -> RhythmGenome:
    core = ms.core
    detail = ms.scales.get(32, core)
    macro = ms.scales.get(8, core)
    p = ms.perimeter
    lum, sat, edge = _pixels_to_arrays(detail)
    kick_lane, snare_lane, hat_lane, accent_lane = _band_projection(lum, sat, edge)

    darkness = 1.0 - core.brightness
    lr_energy = abs(float(macro.section_energy[0]) - float(macro.section_energy[-1]))
    tb_activity = abs(core.horizontal_activity - core.vertical_activity)

    weight = _clamp01(0.44 * darkness + 0.30 * p.south_weight + 0.16 * core.contrast + 0.10 * (1.0 - core.brightness))
    motion = _clamp01(0.36 * detail.edge_density + 0.26 * detail.visual_entropy + 0.18 * core.horizontal_activity + 0.12 * core.vertical_activity + 0.08 * lr_energy)
    openness = _clamp01(0.40 * core.brightness + 0.24 * p.north_air + 0.20 * (1.0 - detail.edge_density) + 0.16 * (1.0 - core.contrast))
    order = _clamp01(0.52 * core.symmetry + 0.28 * (1.0 - detail.visual_entropy) + 0.20 * (1.0 - p.jaggedness))
    threat = _clamp01(0.38 * darkness + 0.28 * core.contrast + 0.20 * p.jaggedness + 0.14 * detail.edge_density)
    warmth = _hue_warmth(core.dominant_hue, core.saturation)
    urgency = _clamp01(0.36 * motion + 0.26 * core.contrast + 0.20 * core.saturation + 0.18 * p.jaggedness)
    roughness = _clamp01(0.38 * p.jaggedness + 0.30 * detail.edge_density + 0.20 * detail.visual_entropy + 0.12 * tb_activity)
    space = _clamp01(0.42 * (1.0 - detail.edge_density) + 0.26 * (1.0 - detail.visual_entropy) + 0.20 * openness + 0.12 * core.symmetry)

    lane_offbeat = float(np.mean([accent_lane[i] for i in range(16) if i % 4 != 0]))
    lane_downbeat = float(np.mean([accent_lane[i] for i in (0, 4, 8, 12)]))
    asymmetry = _clamp01(lr_energy * 1.7 + abs(p.west_brightness - p.east_brightness) * 0.8)

    pulse_density = _clamp01(0.24 + 0.40 * motion + 0.18 * urgency + 0.10 * roughness - 0.16 * space + density_bias * 0.08)
    kick_density = _clamp01(0.22 + 0.36 * weight + 0.22 * motion + 0.12 * float(np.mean(kick_lane)) - 0.10 * space + density_bias * 0.06)
    snare_density = _clamp01(0.16 + 0.30 * motion + 0.22 * roughness + 0.16 * float(np.mean(snare_lane)) + 0.08 * threat - 0.08 * space)
    hat_density = _clamp01(0.18 + 0.42 * motion + 0.20 * urgency + 0.16 * float(np.mean(hat_lane)) - 0.14 * space + density_bias * 0.06)
    syncopation = _clamp01(0.18 + 0.36 * lane_offbeat + 0.22 * roughness + 0.18 * (1.0 - order) + 0.06 * asymmetry - 0.20 * lane_downbeat)
    hat_irregularity = _clamp01(0.18 + 0.42 * roughness + 0.26 * (1.0 - order) + 0.14 * float(np.std(hat_lane)))
    swing = _clamp01((0.03 + 0.18 * asymmetry + 0.12 * warmth + 0.10 * (1.0 - order)) * (0.45 + 0.55 * motion)) * 0.34
    rest_probability = _clamp01(0.10 + 0.48 * space + 0.18 * openness - 0.24 * urgency - density_bias * 0.07)
    accent_asymmetry = asymmetry
    fill_probability = _clamp01(0.10 + 0.30 * roughness + 0.24 * urgency + 0.18 * p.east_cadence_bias + 0.10 * detail.visual_entropy)
    backbeat_strength = _clamp01(0.18 + 0.48 * order + 0.20 * (1.0 - syncopation) + 0.14 * core.symmetry)
    bass_drum_lock = _clamp01(0.30 + 0.36 * weight + 0.26 * order + 0.08 * threat)
    doubletime_bias = _clamp01(0.10 + 0.44 * urgency + 0.30 * motion + 0.16 * hat_density)
    halftime_bias = _clamp01(0.14 + 0.44 * weight + 0.24 * threat + 0.18 * space - 0.22 * urgency)
    percussion_weight = _clamp01(0.22 + 0.38 * weight + 0.24 * roughness + 0.16 * threat)

    if order > 0.72:
        cycle = 1 if core.symmetry > 0.80 else 2
    elif detail.visual_entropy > 0.66 or asymmetry > 0.50:
        cycle = 4
    else:
        cycle = 2

    stable_seed = ms.seed if identity_seed is None else int(identity_seed)
    phase_offset = int((stable_seed ^ int(core.dominant_hue * 65535)) % 4)
    profile = _profile(weight, motion, order, threat, urgency, space, roughness)

    return RhythmGenome(
        pulse_density=pulse_density,
        kick_density=kick_density,
        snare_density=snare_density,
        hat_density=hat_density,
        syncopation=syncopation,
        hat_irregularity=hat_irregularity,
        swing=swing,
        rest_probability=rest_probability,
        accent_asymmetry=accent_asymmetry,
        fill_probability=fill_probability,
        backbeat_strength=backbeat_strength,
        bass_drum_lock=bass_drum_lock,
        groove_cycle_length=cycle,
        doubletime_bias=doubletime_bias,
        halftime_bias=halftime_bias,
        percussion_weight=percussion_weight,
        weight=weight,
        motion=motion,
        openness=openness,
        order=order,
        threat=threat,
        warmth=warmth,
        urgency=urgency,
        roughness=roughness,
        space=space,
        kick_lane=kick_lane,
        snare_lane=snare_lane,
        hat_lane=hat_lane,
        accent_lane=accent_lane,
        rhythm_profile=profile,
        phase_offset=phase_offset,
        image_rhythm_strength=rhythm_strength,
    )
