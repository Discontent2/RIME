from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, List, Tuple
import colorsys

import numpy as np
from PIL import Image, ImageFilter, ImageOps


@dataclass
class GaussianPersistence:
    radii: List[int]
    edge_retention: List[float]
    contrast_retention: List[float]
    large_structure_persistence: float
    fragile_detail: float
    softness: float

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class DirectionalEdges:
    horizontal: float
    vertical: float
    diag_down: float
    diag_up: float
    fine: float
    coarse: float
    dominant: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AnomalyAnalysis:
    strength: float
    rarity: float
    warm_anomaly: float
    bright_anomaly: float
    color_distance: float
    lane: List[float]
    center_x: float
    center_y: float

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class SolarizationAnalysis:
    thresholds: List[int]
    change_scores: List[float]
    threshold_instability: float
    selected_threshold: int
    shadow_brightness: float
    shadow_contrast: float
    shadow_hue: float
    shadow_lane: List[float]
    shadow_pixels_rgb: List[List[Tuple[int, int, int]]]

    def to_dict(self, include_pixels: bool = False) -> dict:
        d = asdict(self)
        if not include_pixels:
            d.pop("shadow_pixels_rgb", None)
        return d


@dataclass
class TransformAnalysis:
    gaussian: GaussianPersistence
    directional: DirectionalEdges
    anomaly: AnomalyAnalysis
    solarization: SolarizationAnalysis

    def to_dict(self, include_pixels: bool = False) -> dict:
        return {
            "gaussian": self.gaussian.to_dict(),
            "directional_edges": self.directional.to_dict(),
            "anomaly": self.anomaly.to_dict(),
            "solarization": self.solarization.to_dict(include_pixels=include_pixels),
        }


def _clamp01(v: float) -> float:
    return float(np.clip(v, 0.0, 1.0))


def _lum(arr: np.ndarray) -> np.ndarray:
    return 0.2126 * arr[..., 0] + 0.7152 * arr[..., 1] + 0.0722 * arr[..., 2]


def _edge_mag(lum: np.ndarray) -> np.ndarray:
    gx = np.zeros_like(lum)
    gy = np.zeros_like(lum)
    if lum.shape[1] > 1:
        gx[:, 1:] = np.abs(np.diff(lum, axis=1))
    if lum.shape[0] > 1:
        gy[1:, :] = np.abs(np.diff(lum, axis=0))
    return np.clip(gx + gy, 0.0, 1.0)


def _norm16(values: np.ndarray | List[float]) -> List[float]:
    arr = np.asarray(values, dtype=np.float32).reshape(-1)
    if arr.size == 0:
        return [0.5] * 16
    if arr.size != 16:
        arr = np.interp(np.linspace(0, 1, 16), np.linspace(0, 1, arr.size), arr)
    lo, hi = float(arr.min()), float(arr.max())
    if hi - lo < 1e-7:
        return [0.5] * 16
    arr = (arr - lo) / (hi - lo)
    return [float(v) for v in arr]


def _hue(rgb: np.ndarray) -> float:
    flat = rgb.reshape(-1, 3)
    x = y = wt = 0.0
    for r, g, b in flat:
        h, s, v = colorsys.rgb_to_hsv(float(r), float(g), float(b))
        if s < 0.08 or v < 0.05:
            continue
        w = max(0.03, s * v)
        a = h * 2 * np.pi
        x += np.cos(a) * w
        y += np.sin(a) * w
        wt += w
    if wt <= 0:
        return 0.0
    a = float(np.arctan2(y, x))
    if a < 0:
        a += 2 * np.pi
    return a / (2 * np.pi)


def _gaussian(img: Image.Image) -> GaussianPersistence:
    base = img.resize((96, 96), Image.Resampling.LANCZOS)
    a0 = np.asarray(base, dtype=np.float32) / 255.0
    l0 = _lum(a0)
    e0 = max(1e-6, float(_edge_mag(l0).mean()))
    c0 = max(1e-6, float(l0.std()))
    radii = [0, 2, 4, 8]
    er, cr = [], []
    for r in radii:
        b = base if r == 0 else base.filter(ImageFilter.GaussianBlur(radius=r))
        arr = np.asarray(b, dtype=np.float32) / 255.0
        lum = _lum(arr)
        er.append(_clamp01(float(_edge_mag(lum).mean()) / e0))
        cr.append(_clamp01(float(lum.std()) / c0))
    large = _clamp01(0.58 * cr[-1] + 0.42 * er[-1])
    fragile = _clamp01(1.0 - (0.56 * er[2] + 0.44 * cr[2]))
    softness = _clamp01(0.52 * large + 0.30 * (1.0 - fragile) + 0.18 * cr[1])
    return GaussianPersistence(radii, er, cr, large, fragile, softness)


def _directional(img: Image.Image) -> DirectionalEdges:
    small = img.convert("L").resize((64, 64), Image.Resampling.LANCZOS)
    lum = np.asarray(small, dtype=np.float32) / 255.0
    dx = np.abs(np.diff(lum, axis=1)).mean()
    dy = np.abs(np.diff(lum, axis=0)).mean()
    dd = np.abs(lum[1:, 1:] - lum[:-1, :-1]).mean()
    du = np.abs(lum[1:, :-1] - lum[:-1, 1:]).mean()
    vals = np.asarray([dx, dy, dd, du], dtype=np.float32)
    scale = max(1e-6, float(vals.max()))
    vals = np.clip(vals / scale, 0, 1)
    # Image derivative along x highlights mostly vertical structures, and vice versa.
    vertical = float(vals[0]); horizontal = float(vals[1])
    diag_down = float(vals[2]); diag_up = float(vals[3])
    fine = _clamp01(float(_edge_mag(lum).mean()) * 4.4)
    blurred = np.asarray(small.filter(ImageFilter.GaussianBlur(radius=3)), dtype=np.float32) / 255.0
    coarse = _clamp01(float(_edge_mag(blurred).mean()) * 5.2)
    mapping = {"horizontal": horizontal, "vertical": vertical, "diag_down": diag_down, "diag_up": diag_up}
    dominant = max(mapping, key=mapping.get)
    return DirectionalEdges(horizontal, vertical, diag_down, diag_up, fine, coarse, dominant)


def _anomaly(img: Image.Image) -> AnomalyAnalysis:
    small = img.resize((64, 64), Image.Resampling.LANCZOS)
    rgb = np.asarray(small, dtype=np.float32) / 255.0
    lum = _lum(rgb)
    # Robust dominant environment represented by channel medians.
    med = np.median(rgb.reshape(-1, 3), axis=0)
    dist = np.sqrt(np.sum((rgb - med) ** 2, axis=2) / 3.0)
    lum_dev = np.abs(lum - np.median(lum))
    score = 0.72 * dist + 0.28 * lum_dev
    threshold = float(np.quantile(score, 0.91))
    mask = score >= threshold
    if not np.any(mask):
        mask.flat[int(np.argmax(score))] = True
    rarity = _clamp01(1.0 - float(mask.mean()) * 4.0)
    strength = _clamp01(float(score[mask].mean()) * 1.75)
    bright = _clamp01(float(lum[mask].mean() - lum.mean()) * 2.2 + 0.5)
    # Warmth excess in anomaly pixels against the overall field.
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    warm_map = np.clip(r - 0.5 * (g + b), -1, 1)
    warm = _clamp01(0.5 + float(warm_map[mask].mean() - warm_map.mean()) * 1.6)
    color_distance = _clamp01(float(dist[mask].mean()) * 1.8)
    lane = _norm16((score * mask).mean(axis=0))
    ys, xs = np.where(mask)
    cx = float(xs.mean() / max(1, mask.shape[1] - 1)); cy = float(ys.mean() / max(1, mask.shape[0] - 1))
    return AnomalyAnalysis(strength, rarity, warm, bright, color_distance, lane, cx, cy)


def _solarization(img: Image.Image) -> SolarizationAnalysis:
    base = img.resize((32, 32), Image.Resampling.LANCZOS)
    base_arr = np.asarray(base, dtype=np.float32) / 255.0
    base_l = _lum(base_arr)
    thresholds = [64, 96, 128, 160, 192]
    scores: List[float] = []
    shadows: List[Image.Image] = []
    for t in thresholds:
        s = ImageOps.solarize(base, threshold=t)
        shadows.append(s)
        arr = np.asarray(s, dtype=np.float32) / 255.0
        lum = _lum(arr)
        structural = float(np.abs(_edge_mag(lum) - _edge_mag(base_l)).mean())
        tonal = float(np.abs(lum - base_l).mean())
        scores.append(_clamp01(0.58 * structural * 3.0 + 0.42 * tonal * 1.8))
    best_i = int(np.argmax(scores))
    chosen = shadows[best_i]
    arr = np.asarray(chosen, dtype=np.float32) / 255.0
    lum = _lum(arr)
    # Instability measures both peak sensitivity and variation across thresholds.
    instability = _clamp01(0.72 * max(scores) + 0.28 * float(np.std(scores)) * 3.0)
    shadow_lane = _norm16(0.62 * _edge_mag(lum).mean(axis=0) + 0.38 * np.abs(lum.mean(axis=0) - lum.mean()))
    pixels = [[tuple(int(v) for v in px) for px in row] for row in np.asarray(chosen, dtype=np.uint8)]
    return SolarizationAnalysis(
        thresholds=thresholds,
        change_scores=scores,
        threshold_instability=instability,
        selected_threshold=thresholds[best_i],
        shadow_brightness=float(lum.mean()),
        shadow_contrast=_clamp01(float(lum.std()) * 2.5),
        shadow_hue=_hue(arr),
        shadow_lane=shadow_lane,
        shadow_pixels_rgb=pixels,
    )


def analyze_transforms(img: Image.Image) -> TransformAnalysis:
    rgb = img.convert("RGB")
    return TransformAnalysis(
        gaussian=_gaussian(rgb),
        directional=_directional(rgb),
        anomaly=_anomaly(rgb),
        solarization=_solarization(rgb),
    )


def transform_preview_image(img: Image.Image, kind: str, max_side: int = 1024) -> Image.Image:
    src = img.convert("RGB")
    if max(src.size) > max_side:
        ratio = max_side / max(src.size)
        src = src.resize((max(1, int(src.width * ratio)), max(1, int(src.height * ratio))), Image.Resampling.LANCZOS)
    if kind == "solarized":
        # Recompute best threshold at display resolution using the same 32px selector.
        ta = _solarization(src)
        return ImageOps.solarize(src, threshold=ta.selected_threshold)
    if kind == "blur8":
        return src.filter(ImageFilter.GaussianBlur(radius=8))
    if kind == "anomaly":
        small = src.resize((256, 256), Image.Resampling.LANCZOS)
        rgb = np.asarray(small, dtype=np.float32) / 255.0
        med = np.median(rgb.reshape(-1, 3), axis=0)
        lum = _lum(rgb)
        dist = np.sqrt(np.sum((rgb - med) ** 2, axis=2) / 3.0)
        score = 0.72 * dist + 0.28 * np.abs(lum - np.median(lum))
        q = float(np.quantile(score, 0.91))
        norm = np.clip((score - q) / max(1e-6, float(score.max() - q)), 0, 1)
        heat = np.zeros((256, 256, 3), dtype=np.uint8)
        heat[..., 0] = (norm * 255).astype(np.uint8)
        heat[..., 1] = (norm * 120).astype(np.uint8)
        heat[..., 2] = (norm * 45).astype(np.uint8)
        return Image.fromarray(heat, mode="RGB")
    raise ValueError(f"unknown transform preview kind: {kind}")
