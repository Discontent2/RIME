from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Tuple
import json
import math

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageDraw, ImageFont

from .analyzer import MultiScaleAnalysis


def _clamp01(v: float) -> float:
    return max(0.0, min(1.0, float(v)))


@dataclass
class VisualHierarchy:
    macro_authority: float
    meso_authority: float
    micro_authority: float
    primary_subject_strength: float
    primary_subject_x: float
    primary_subject_y: float
    background_weight: float
    anomaly_weight: float

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class MappingIntelligence:
    visual_authority: int
    identity_seed: int
    tonic_pc: int
    kinetic_potential: float
    spectral_brightness_prior: float
    register_depth_prior: float
    bass_weight_prior: float
    transient_prior: float
    roughness_prior: float
    sustain_prior: float
    micro_detail_prior: float
    contrast_accent_prior: float
    hue_color_prior: float
    hierarchy: VisualHierarchy
    causal_map: Dict[str, dict]
    invariants: List[str]

    def to_dict(self) -> dict:
        return asdict(self)


def _pixels(scale) -> np.ndarray:
    return np.asarray(scale.pixels_rgb, dtype=np.float32) / 255.0


def _luminance(rgb: np.ndarray) -> np.ndarray:
    return 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]


def _visual_hierarchy(ms: MultiScaleAnalysis, authority: int) -> VisualHierarchy:
    detail = ms.scales.get(32, ms.core)
    rgb = _pixels(detail)
    lum = _luminance(rgb)
    med_rgb = np.median(rgb.reshape(-1, 3), axis=0)
    color_dist = np.sqrt(np.sum((rgb - med_rgb) ** 2, axis=2) / 3.0)
    lum_dev = np.abs(lum - np.median(lum))
    gx = np.zeros_like(lum); gy = np.zeros_like(lum)
    gx[:, 1:] = np.abs(np.diff(lum, axis=1)); gy[1:, :] = np.abs(np.diff(lum, axis=0))
    salience = 0.48 * color_dist + 0.30 * lum_dev + 0.22 * np.clip(gx + gy, 0.0, 1.0)
    q = float(np.quantile(salience, 0.84))
    mask = salience >= q
    if not np.any(mask):
        mask.flat[int(np.argmax(salience))] = True
    ys, xs = np.where(mask)
    cx = float(xs.mean() / max(1, salience.shape[1] - 1))
    cy = float(ys.mean() / max(1, salience.shape[0] - 1))
    subject_strength = _clamp01(float(salience[mask].mean()) * 2.4)
    background_weight = _clamp01(1.0 - float(mask.mean()) * 2.4)
    anomaly_weight = _clamp01(0.55 * ms.transforms.anomaly.strength + 0.45 * ms.transforms.anomaly.rarity)

    # The visual-authority control changes how strongly the hierarchy constrains downstream mappings,
    # not which layer is allowed to control which musical scale.
    gain = {1: 0.82, 2: 1.0, 3: 1.14}[int(authority)]
    macro = _clamp01((0.56 + 0.18 * ms.scales.get(8, ms.core).symmetry + 0.12 * background_weight) * gain)
    meso = _clamp01((0.52 + 0.20 * ms.core.edge_density + 0.12 * subject_strength) * gain)
    micro = _clamp01((0.36 + 0.28 * detail.edge_density + 0.18 * detail.visual_entropy) * gain)
    return VisualHierarchy(macro, meso, micro, subject_strength, cx, cy, background_weight, anomaly_weight)


def build_mapping_intelligence(ms: MultiScaleAnalysis, visual_authority: int = 2, identity_seed: int | None = None) -> MappingIntelligence:
    if visual_authority not in (1, 2, 3):
        raise ValueError("visual_authority must be 1, 2, or 3")
    seed = int(ms.seed if identity_seed is None else identity_seed)
    macro = ms.scales.get(8, ms.core)
    core = ms.core
    detail = ms.scales.get(32, core)
    p = ms.perimeter
    tr = ms.transforms
    hierarchy = _visual_hierarchy(ms, visual_authority)

    diag = max(tr.directional.diag_down, tr.directional.diag_up)
    imbalance = abs(float(macro.section_energy[0]) - float(macro.section_energy[-1]))
    kinetic = _clamp01(
        0.19 * tr.directional.horizontal
        + 0.17 * tr.directional.vertical
        + 0.17 * diag
        + 0.13 * tr.gaussian.fragile_detail
        + 0.12 * tr.anomaly.strength
        + 0.10 * detail.edge_density
        + 0.07 * p.jaggedness
        + 0.05 * imbalance
    )

    spectral = _clamp01(0.62 * core.brightness + 0.18 * core.saturation + 0.12 * tr.anomaly.bright_anomaly + 0.08 * p.north_air)
    reg_depth = _clamp01(0.58 * (1.0 - core.brightness) + 0.20 * p.south_weight + 0.12 * (1.0 - hierarchy.primary_subject_y) + 0.10 * core.contrast)
    bass_weight = _clamp01(0.50 * (1.0 - macro.brightness) + 0.24 * p.south_weight + 0.16 * hierarchy.macro_authority + 0.10 * macro.contrast)
    transient = _clamp01(0.40 * kinetic + 0.24 * core.contrast + 0.18 * tr.directional.fine + 0.10 * tr.anomaly.strength + 0.08 * detail.visual_entropy)
    rough = _clamp01(0.34 * p.jaggedness + 0.26 * detail.edge_density + 0.18 * detail.visual_entropy + 0.12 * tr.solarization.threshold_instability + 0.10 * tr.anomaly.strength)
    sustain = _clamp01(0.46 * tr.gaussian.large_structure_persistence + 0.24 * tr.gaussian.softness + 0.18 * (1.0 - detail.edge_density) + 0.12 * macro.symmetry)
    micro = _clamp01(0.44 * tr.gaussian.fragile_detail + 0.26 * tr.directional.fine + 0.18 * detail.visual_entropy + 0.12 * tr.anomaly.rarity)
    contrast_accent = _clamp01(0.58 * core.contrast + 0.22 * tr.anomaly.strength + 0.20 * tr.directional.coarse)

    # Hue is deliberately demoted from tonic ownership. It remains a color/timbre prior.
    hue_color = _clamp01(core.saturation * (0.35 + 0.65 * abs(math.sin(core.dominant_hue * math.pi))))

    # Stable tonic: mostly macro brightness / subject vertical position / symmetry + persistent identity seed.
    # Hue contributes only one semitone worth of bias instead of owning all twelve notes.
    tonic_base = (
        int(round(macro.brightness * 5.0))
        + int(round((1.0 - hierarchy.primary_subject_y) * 4.0))
        + int(round(macro.symmetry * 3.0))
        + (seed % 12)
    ) % 12
    hue_nudge = int(round((core.dominant_hue - 0.5) * 2.0)) if core.saturation > 0.22 else 0
    tonic_pc = int((tonic_base + hue_nudge) % 12)

    causal = {
        "brightness": {
            "value": round(core.brightness, 4),
            "targets": ["spectral_brightness", "register_depth"],
            "rule": "brighter image -> brighter spectrum / shallower register depth",
        },
        "large_dark_mass": {
            "value": round(bass_weight, 4),
            "targets": ["bass_weight", "low_register_occupation"],
            "rule": "large dark macro structure -> stronger low-frequency foundation",
        },
        "fine_detail": {
            "value": round(micro, 4),
            "targets": ["PSG_surface", "ornament", "micro_percussion"],
            "rule": "fragile visual detail -> high-frequency musical detail",
        },
        "roughness": {
            "value": round(rough, 4),
            "targets": ["FM_modulation_complexity", "noise_amount"],
            "rule": "rough visual texture -> local FM/noise roughness",
        },
        "smooth_persistence": {
            "value": round(sustain, 4),
            "targets": ["sustain", "drone", "envelope_length"],
            "rule": "large structures that survive blur -> foundational sustained material",
        },
        "contrast": {
            "value": round(contrast_accent, 4),
            "targets": ["accent_strength", "transient_definition"],
            "rule": "visual contrast -> sharper dynamic/transient separation",
        },
        "kinetic_potential": {
            "value": round(kinetic, 4),
            "targets": ["drum_density", "bass_rhythm", "syncopation", "fills"],
            "rule": "directional energy/detail -> musical propulsion even in a still image",
        },
        "hue": {
            "value": round(core.dominant_hue, 4),
            "targets": ["FM_color", "harmonic_color"],
            "rule": "hue colors timbre/harmony but no longer directly selects the tonic",
        },
    }
    invariants = ["identity_seed", "RIME_Sigil", "tonic", "mode", "groove_architecture", "form_architecture"]
    return MappingIntelligence(
        visual_authority=int(visual_authority), identity_seed=seed, tonic_pc=tonic_pc,
        kinetic_potential=kinetic, spectral_brightness_prior=spectral,
        register_depth_prior=reg_depth, bass_weight_prior=bass_weight,
        transient_prior=transient, roughness_prior=rough, sustain_prior=sustain,
        micro_detail_prior=micro, contrast_accent_prior=contrast_accent,
        hue_color_prior=hue_color, hierarchy=hierarchy, causal_map=causal, invariants=invariants,
    )


def apply_mapping_invariants(genome, reference) -> None:
    """Lock song identity for controlled image-transformation experiments."""
    genome.seed = reference.seed
    genome.variation_seed = reference.variation_seed
    genome.root_pc = reference.root_pc
    genome.root_name = reference.root_name
    genome.mode = reference.mode
    genome.sigil_degrees = list(reference.sigil_degrees)
    genome.sigil_rhythm = list(reference.sigil_rhythm)
    genome.architecture = reference.architecture
    genome.atmosphere.primary = reference.atmosphere.primary
    genome.atmosphere.secondary = reference.atmosphere.secondary
    genome.genesis_drums.architecture = reference.genesis_drums.architecture
    genome.drum_family = reference.drum_family
    genome.form_name = reference.form_name
    genome.phrase_labels = list(reference.phrase_labels)
    genome.phrase_stage = list(reference.phrase_stage)


def make_mapping_variants(source_path: str | Path, kind: str, output_dir: str | Path) -> Dict[str, Path]:
    source_path = Path(source_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    img = Image.open(source_path).convert("RGB")
    variants: Dict[str, Image.Image] = {}

    if kind in {"brightness", "full"}:
        variants["brightness_plus20"] = ImageEnhance.Brightness(img).enhance(1.20)
        variants["brightness_minus20"] = ImageEnhance.Brightness(img).enhance(0.80)
    if kind in {"contrast", "full"}:
        variants["contrast_high"] = ImageEnhance.Contrast(img).enhance(1.35)
        variants["contrast_low"] = ImageEnhance.Contrast(img).enhance(0.70)
    if kind in {"blur", "full"}:
        variants["blur_r4"] = img.filter(ImageFilter.GaussianBlur(radius=4))
    if kind in {"saturation", "full"}:
        variants["desaturated"] = ImageEnhance.Color(img).enhance(0.35)
    if kind in {"flip", "full"}:
        variants["flip_horizontal"] = ImageOps.mirror(img)
    if kind in {"crop", "full"}:
        w, h = img.size
        dx, dy = int(w * 0.10), int(h * 0.10)
        crop = img.crop((dx, dy, w - dx, h - dy)).resize((w, h), Image.Resampling.LANCZOS)
        variants["center_crop80"] = crop

    paths: Dict[str, Path] = {}
    for name, variant in variants.items():
        p = output_dir / f"{source_path.stem}_{name}.png"
        variant.save(p)
        paths[name] = p
    return paths


def mapping_expectation_score(base, variant, name: str) -> Tuple[float, List[str]]:
    """Return a lightweight interpretable equivariance score for a controlled transform."""
    notes: List[str] = []
    checks: List[bool] = []
    bm, vm = base.mapping_intelligence, variant.mapping_intelligence

    # Invariants are checked separately from surface-direction expectations.
    invariant_ok = (
        base.root_pc == variant.root_pc and base.mode == variant.mode
        and base.sigil_degrees == variant.sigil_degrees
        and base.genesis_drums.architecture == variant.genesis_drums.architecture
    )
    checks.append(invariant_ok)
    notes.append("identity invariants " + ("PASS" if invariant_ok else "CHECK"))

    if name == "brightness_plus20":
        ok = vm.spectral_brightness_prior >= bm.spectral_brightness_prior and vm.register_depth_prior <= bm.register_depth_prior
        checks.append(ok); notes.append("brighter -> brighter spectrum / shallower register " + ("PASS" if ok else "CHECK"))
    elif name == "brightness_minus20":
        ok = vm.spectral_brightness_prior <= bm.spectral_brightness_prior and vm.register_depth_prior >= bm.register_depth_prior
        checks.append(ok); notes.append("darker -> darker spectrum / deeper register " + ("PASS" if ok else "CHECK"))
    elif name == "contrast_high":
        ok = vm.contrast_accent_prior >= bm.contrast_accent_prior
        checks.append(ok); notes.append("higher contrast -> stronger accents " + ("PASS" if ok else "CHECK"))
    elif name == "contrast_low":
        ok = vm.contrast_accent_prior <= bm.contrast_accent_prior
        checks.append(ok); notes.append("lower contrast -> softer accents " + ("PASS" if ok else "CHECK"))
    elif name == "blur_r4":
        ok = vm.micro_detail_prior <= bm.micro_detail_prior and vm.sustain_prior >= bm.sustain_prior - 0.08
        checks.append(ok); notes.append("blur -> less micro detail / preserve sustain " + ("PASS" if ok else "CHECK"))
    elif name == "desaturated":
        ok = vm.hue_color_prior <= bm.hue_color_prior + 0.02
        checks.append(ok); notes.append("desaturation -> weaker hue/timbre color authority " + ("PASS" if ok else "CHECK"))
    elif name == "flip_horizontal":
        ok = base.root_pc == variant.root_pc and base.mode == variant.mode
        checks.append(ok); notes.append("horizontal flip -> tonal identity invariant " + ("PASS" if ok else "CHECK"))
    elif name == "center_crop80":
        # crop stability tolerates surface movement while preserving identity
        ok = base.root_pc == variant.root_pc and base.mode == variant.mode
        checks.append(ok); notes.append("crop -> preserve tonic/mode family " + ("PASS" if ok else "CHECK"))

    score = sum(1.0 for x in checks if x) / max(1, len(checks))
    return round(score, 4), notes


def save_mapping_report_png(report: dict, output_path: str | Path) -> None:
    W = 1500
    rows = report.get("variants", [])
    H = 330 + max(1, len(rows)) * 115
    img = Image.new("RGB", (W, H), (14, 17, 24))
    draw = ImageDraw.Draw(img)
    try:
        font_big = ImageFont.truetype("DejaVuSans-Bold.ttf", 34)
        font = ImageFont.truetype("DejaVuSans.ttf", 19)
        font_b = ImageFont.truetype("DejaVuSans-Bold.ttf", 20)
    except Exception:
        font_big = font = font_b = ImageFont.load_default()
    draw.text((40, 28), "RIME v0.012 // EQUIVARIANT MUSIFICATION REPORT", font=font_big, fill=(234, 241, 255))
    draw.text((42, 80), f"Mapping confidence: {report.get('mapping_confidence', 0):.0%}   •   Identity seed: {report.get('identity_seed','')}", font=font, fill=(159, 175, 204))
    y = 130
    base = report.get("base", {})
    draw.rounded_rectangle((40, y, W-40, y+125), radius=14, fill=(30, 35, 48))
    draw.text((60, y+18), "BASE MAPPING", font=font_b, fill=(102, 225, 255))
    txt = f"tonic {base.get('root','?')} {base.get('mode','?')}  •  kinetic {base.get('kinetic',0):.2f}  •  spectral {base.get('spectral',0):.2f}  •  transient {base.get('transient',0):.2f}  •  micro {base.get('micro',0):.2f}"
    draw.text((60, y+58), txt, font=font, fill=(235, 239, 248))
    draw.text((60, y+88), "Invariant family: tonic / mode / RIME Sigil / groove architecture / form", font=font, fill=(159, 175, 204))
    y += 155
    for row in rows:
        draw.rounded_rectangle((40, y, W-40, y+95), radius=12, fill=(25, 29, 40))
        status = "PASS" if row.get("score",0) >= 0.999 else "CHECK"
        color = (92, 221, 144) if status == "PASS" else (255, 191, 94)
        draw.text((60, y+14), row.get("name","variant"), font=font_b, fill=color)
        draw.text((330, y+14), f"score {row.get('score',0):.0%}", font=font_b, fill=color)
        note = " • ".join(row.get("notes", []))
        draw.text((60, y+50), note[:145], font=font, fill=(210, 217, 233))
        y += 115
    img.save(output_path)
