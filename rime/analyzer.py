from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from pathlib import Path
from typing import Dict, List, Tuple
import colorsys
import math

import numpy as np
from PIL import Image

from .transforms import TransformAnalysis, analyze_transforms, transform_preview_image


@dataclass
class ScaleAnalysis:
    grid_size: int
    brightness: float
    saturation: float
    contrast: float
    edge_density: float
    horizontal_activity: float
    vertical_activity: float
    symmetry: float
    visual_entropy: float
    dominant_hue: float
    palette_size: int
    section_energy: List[float]
    section_tension: List[float]
    section_brightness: List[float]
    motif_contour: List[float]
    fine_activity: List[float]
    pixels_rgb: List[List[Tuple[int, int, int]]]

    def to_dict(self, include_pixels: bool = False) -> dict:
        d = asdict(self)
        if not include_pixels:
            d.pop("pixels_rgb", None)
        return d


@dataclass
class PerimeterAnalysis:
    north_brightness: float
    south_brightness: float
    west_brightness: float
    east_brightness: float
    north_edge_density: float
    south_edge_density: float
    west_edge_density: float
    east_edge_density: float
    perimeter_contrast: float
    perimeter_entropy: float
    jaggedness: float
    corner_intensity: float
    west_pickup_bias: float
    east_cadence_bias: float
    south_weight: float
    north_air: float

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class MultiScaleAnalysis:
    source_path: str
    seed: int
    scales: Dict[int, ScaleAnalysis]
    perimeter: PerimeterAnalysis
    transforms: TransformAnalysis

    @property
    def core(self) -> ScaleAnalysis:
        return self.scales[16] if 16 in self.scales else self.scales[sorted(self.scales)[0]]


# Backward-compatible name for single-grid callers.
ImageAnalysis = ScaleAnalysis


def _clamp01(v: float) -> float:
    return float(np.clip(v, 0.0, 1.0))


def _normalized_entropy(values: np.ndarray, bins: int = 16) -> float:
    hist, _ = np.histogram(values, bins=bins, range=(0.0, 1.0))
    probs = hist.astype(float)
    total = probs.sum()
    if total <= 0:
        return 0.0
    probs /= total
    probs = probs[probs > 0]
    ent = -(probs * np.log2(probs)).sum()
    return float(ent / np.log2(bins)) if bins > 1 else 0.0


def _dominant_hue(rgb: np.ndarray) -> float:
    flat = rgb.reshape(-1, 3)
    hues, weights = [], []
    for r, g, b in flat:
        h, s, v = colorsys.rgb_to_hsv(float(r), float(g), float(b))
        if s > 0.08 and v > 0.05:
            hues.append(h)
            weights.append(max(0.05, s * v))
    if not hues:
        return 0.0
    angles = np.asarray(hues) * 2 * np.pi
    w = np.asarray(weights)
    x = np.sum(np.cos(angles) * w)
    y = np.sum(np.sin(angles) * w)
    angle = np.arctan2(y, x)
    if angle < 0:
        angle += 2 * np.pi
    return float(angle / (2 * np.pi))


def _palette_size(image: Image.Image) -> int:
    q = image.quantize(colors=16)
    colors = q.getcolors(maxcolors=256) or []
    return len(colors)


def _image_arrays(img: Image.Image, grid_size: int):
    small = img.resize((grid_size, grid_size), Image.Resampling.LANCZOS)
    arr = np.asarray(small, dtype=np.float32) / 255.0
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    maxc = np.max(arr, axis=2)
    minc = np.min(arr, axis=2)
    sat = np.divide(maxc - minc, np.maximum(maxc, 1e-6))
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return small, arr, sat, lum


def _analyze_scale(img: Image.Image, grid_size: int) -> ScaleAnalysis:
    small, arr, sat, luminance = _image_arrays(img, grid_size)
    brightness = float(luminance.mean())
    saturation = float(sat.mean())
    contrast = _clamp01(float(luminance.std()) * 2.5)

    gx = float(np.abs(np.diff(luminance, axis=1)).mean()) if grid_size > 1 else 0.0
    gy = float(np.abs(np.diff(luminance, axis=0)).mean()) if grid_size > 1 else 0.0
    edge_density = _clamp01((gx + gy) * 2.25)
    horizontal_activity = _clamp01(gx * 4.0)
    vertical_activity = _clamp01(gy * 4.0)

    symmetry_error = float(np.abs(arr - np.flip(arr, axis=1)).mean())
    symmetry = _clamp01(1.0 - symmetry_error * 2.0)
    visual_entropy = _clamp01(0.5 * _normalized_entropy(luminance) + 0.5 * _normalized_entropy(sat))

    section_energy, section_tension, section_brightness, fine_activity = [], [], [], []
    for chunk in np.array_split(np.arange(grid_size), 4):
        region_l = luminance[:, chunk]
        region_s = sat[:, chunk]
        reg_brightness = float(region_l.mean())
        reg_contrast = _clamp01(float(np.std(region_l)) * 3.0)
        reg_darkness = 1.0 - reg_brightness
        reg_gx = float(np.abs(np.diff(region_l, axis=1)).mean()) if region_l.shape[1] > 1 else 0.0
        reg_gy = float(np.abs(np.diff(region_l, axis=0)).mean()) if region_l.shape[0] > 1 else 0.0
        reg_edge = _clamp01((reg_gx + reg_gy) * 2.5)
        reg_entropy = _clamp01(_normalized_entropy(region_l))
        energy = 0.26 * float(region_s.mean()) + 0.18 * reg_brightness + 0.32 * reg_contrast + 0.24 * reg_edge
        tension = 0.46 * reg_darkness + 0.34 * reg_contrast + 0.20 * reg_edge
        section_energy.append(_clamp01(energy))
        section_tension.append(_clamp01(tension))
        section_brightness.append(_clamp01(reg_brightness))
        fine_activity.append(_clamp01(0.52 * reg_edge + 0.28 * reg_entropy + 0.20 * reg_contrast))

    # Every image column contributes a vertical center. Normalize all resolutions
    # to 16 contour points so the melodic grammar stays stable.
    raw_contour: List[float] = []
    ys = np.linspace(1.0, 0.0, grid_size)
    for x in range(grid_size):
        col_l = luminance[:, x]
        col_s = sat[:, x]
        local_contrast = np.abs(col_l - col_l.mean())
        weights = 0.12 + col_s + local_contrast + (1.0 - col_l) * 0.38
        total = float(weights.sum())
        center = float(np.dot(ys, weights) / total) if total > 0 else 0.5
        raw_contour.append(_clamp01(center))
    motif_contour = [float(v) for v in np.interp(np.linspace(0, 1, 16), np.linspace(0, 1, len(raw_contour)), raw_contour)]

    pixels = [[tuple(int(v) for v in px) for px in row] for row in np.asarray(small, dtype=np.uint8)]
    return ScaleAnalysis(
        grid_size=grid_size,
        brightness=brightness,
        saturation=saturation,
        contrast=contrast,
        edge_density=edge_density,
        horizontal_activity=horizontal_activity,
        vertical_activity=vertical_activity,
        symmetry=symmetry,
        visual_entropy=visual_entropy,
        dominant_hue=_dominant_hue(arr),
        palette_size=_palette_size(small),
        section_energy=section_energy,
        section_tension=section_tension,
        section_brightness=section_brightness,
        motif_contour=motif_contour,
        fine_activity=fine_activity,
        pixels_rgb=pixels,
    )


def _edge_delta(values: np.ndarray) -> float:
    if len(values) <= 1:
        return 0.0
    return _clamp01(float(np.abs(np.diff(values)).mean()) * 4.0)


def _analyze_perimeter(img: Image.Image, grid_size: int = 32) -> PerimeterAnalysis:
    _, _, _, lum = _image_arrays(img, grid_size)
    north, south = lum[0, :], lum[-1, :]
    west, east = lum[:, 0], lum[:, -1]
    perimeter = np.concatenate([north, east[1:], south[-2::-1], west[-2:0:-1]])
    diffs = np.abs(np.diff(np.r_[perimeter, perimeter[0]]))

    north_b = float(north.mean())
    south_b = float(south.mean())
    west_b = float(west.mean())
    east_b = float(east.mean())
    north_e = _edge_delta(north)
    south_e = _edge_delta(south)
    west_e = _edge_delta(west)
    east_e = _edge_delta(east)
    perimeter_contrast = _clamp01(float(perimeter.std()) * 3.0)
    perimeter_entropy = _clamp01(_normalized_entropy(perimeter))
    jaggedness = _clamp01(float(diffs.mean()) * 4.5 + float(diffs.std()) * 2.0)
    corners = np.array([lum[0, 0], lum[0, -1], lum[-1, -1], lum[-1, 0]])
    corner_intensity = _clamp01(float(np.abs(corners - perimeter.mean()).mean()) * 3.5)

    return PerimeterAnalysis(
        north_brightness=north_b,
        south_brightness=south_b,
        west_brightness=west_b,
        east_brightness=east_b,
        north_edge_density=north_e,
        south_edge_density=south_e,
        west_edge_density=west_e,
        east_edge_density=east_e,
        perimeter_contrast=perimeter_contrast,
        perimeter_entropy=perimeter_entropy,
        jaggedness=jaggedness,
        corner_intensity=corner_intensity,
        west_pickup_bias=_clamp01(0.55 * west_e + 0.25 * (1.0 - west_b) + 0.20 * perimeter_entropy),
        east_cadence_bias=_clamp01(0.50 * east_e + 0.30 * (1.0 - east_b) + 0.20 * perimeter_contrast),
        south_weight=_clamp01(0.55 * (1.0 - south_b) + 0.30 * south_e + 0.15 * perimeter_contrast),
        north_air=_clamp01(0.55 * north_b + 0.25 * north_e + 0.20 * perimeter_entropy),
    )


def analyze_image(path: str | Path, grid_size: int = 16) -> ScaleAnalysis:
    img = Image.open(Path(path)).convert("RGB")
    return _analyze_scale(img, grid_size)


def analyze_multiscale(path: str | Path, grid_mode: str = "layered", single_grid: int = 16) -> MultiScaleAnalysis:
    path = Path(path)
    raw = path.read_bytes()
    seed = int.from_bytes(sha256(raw).digest()[:8], "big")
    img = Image.open(path).convert("RGB")

    if grid_mode == "single":
        sizes = [single_grid]
    elif grid_mode == "layered64":
        sizes = [8, 16, 32, 64]
    else:
        sizes = [8, 16, 32]

    scales = {size: _analyze_scale(img, size) for size in sizes}
    # Guarantee a 16x16 core for layered composition, even if future modes change.
    if grid_mode != "single" and 16 not in scales:
        scales[16] = _analyze_scale(img, 16)
    return MultiScaleAnalysis(str(path), seed, scales, _analyze_perimeter(img, 32), analyze_transforms(img))


def save_pixel_preview(path: str | Path, output_path: str | Path, grid_size: int = 16, scale: int = 32) -> None:
    img = Image.open(path).convert("RGB")
    small = img.resize((grid_size, grid_size), Image.Resampling.LANCZOS)
    preview = small.resize((grid_size * scale, grid_size * scale), Image.Resampling.NEAREST)
    preview.save(output_path)


def save_transform_preview(path: str | Path, output_path: str | Path, kind: str) -> None:
    img = Image.open(path).convert("RGB")
    preview = transform_preview_image(img, kind)
    preview.save(output_path)
