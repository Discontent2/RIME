from __future__ import annotations

import math
from typing import Dict, List, Sequence, Tuple


def foundation_occupancy(events: Dict[str, Sequence[object]], total_steps: int) -> List[bool]:
    """Step-grid occupancy for the musical floor: bass, harmony and drums.

    Bass/harmony sustain across their duration. Drum hits occupy one 16th step.
    Lead is intentionally excluded so a lonely motif cannot disguise a collapsed groove.
    """
    occupied = [False] * max(0, int(total_steps))
    for track in ("bass", "harmony"):
        for e in events.get(track, ()):
            a = max(0, int(math.floor(float(e.start_step))))
            b = min(total_steps, int(math.ceil(float(e.start_step) + max(1.0, float(e.duration_steps)))))
            for step in range(a, b):
                occupied[step] = True
    for e in events.get("drums", ()):
        step = int(math.floor(float(e.start_step)))
        if 0 <= step < total_steps:
            occupied[step] = True
    return occupied


def detect_stop_runs(events: Dict[str, Sequence[object]], total_steps: int, min_stop_steps: int = 4) -> List[Tuple[int, int]]:
    """Return [start,end) foundation-collapse runs at least min_stop_steps long.

    Initial and final empty space are not counted as stops because no established
    musical motion has yet been interrupted (or the piece has already ended).
    """
    occupied = foundation_occupancy(events, total_steps)
    active = [i for i, value in enumerate(occupied) if value]
    if not active:
        return []
    first, last = active[0], active[-1]
    runs: List[Tuple[int, int]] = []
    i = first
    while i <= last:
        if occupied[i]:
            i += 1
            continue
        a = i
        while i <= last and not occupied[i]:
            i += 1
        b = i
        if b - a >= max(1, int(min_stop_steps)):
            runs.append((a, b))
    return runs


def stop_mid_seconds(run: Tuple[int, int], tempo: float) -> float:
    a, b = run
    return ((a + b) * 0.5) * 15.0 / max(1e-9, float(tempo))


def rolling_max_stops(runs: Sequence[Tuple[int, int]], tempo: float, window_seconds: float = 80.0) -> int:
    times = sorted(stop_mid_seconds(run, tempo) for run in runs)
    best = 0
    left = 0
    win = max(0.001, float(window_seconds))
    for right, t in enumerate(times):
        while left <= right and t - times[left] > win:
            left += 1
        best = max(best, right - left + 1)
    return best


def foundation_coverage(events: Dict[str, Sequence[object]], total_steps: int) -> float:
    occ = foundation_occupancy(events, total_steps)
    return sum(1 for x in occ if x) / max(1, len(occ))


def core_onset_steps(events: Dict[str, Sequence[object]], start_step: int = 0, end_step: int | None = None) -> List[int]:
    """Meaningful propulsion attacks: bass starts + non-hat percussion starts."""
    if end_step is None:
        end_step = 10**9
    out: set[int] = set()
    for e in events.get("bass", ()):
        s = int(round(float(e.start_step)))
        if start_step <= s < end_step:
            out.add(s)
    for e in events.get("drums", ()):
        if getattr(e, "pitch", None) in (42, 46):
            continue
        s = int(round(float(e.start_step)))
        if start_step <= s < end_step:
            out.add(s)
    return sorted(out)


def drive_metrics(
    events: Dict[str, Sequence[object]],
    bars: int,
    launch_step: int,
    target_onsets_per_bar: int,
    max_gap_steps: int,
    excluded_ranges: Sequence[Tuple[int, int]] = (),
) -> dict:
    """Measure post-launch propulsion independently of sustained-note occupancy."""
    launch_bar = max(0, int(launch_step) // 16)
    eligible_bars: List[int] = []
    counts: Dict[int, int] = {}
    low_bars: List[int] = []
    all_gaps: List[int] = []

    def excluded(a: int, b: int) -> bool:
        return any(a < y and b > x for x, y in excluded_ranges)

    for bar in range(launch_bar, int(bars)):
        a, b = bar * 16, (bar + 1) * 16
        if excluded(a, b):
            continue
        eligible_bars.append(bar)
        ons = core_onset_steps(events, a, b)
        counts[bar] = len(ons)
        if len(ons) < int(target_onsets_per_bar):
            low_bars.append(bar)
        local = [0] + [s - a for s in ons] + [16]
        all_gaps.extend(local[i + 1] - local[i] for i in range(len(local) - 1))

    coverage = 1.0 - len(low_bars) / max(1, len(eligible_bars))
    avg_gap = sum(all_gaps) / max(1, len(all_gaps))
    max_gap = max(all_gaps) if all_gaps else 16

    # A false launch is a consecutive pair of low-drive ordinary bars after
    # launch. Single sparse bars can still breathe without reading as a restart.
    false_launches = 0
    run = 0
    for bar in eligible_bars:
        if bar in low_bars:
            run += 1
            if run == 2:
                false_launches += 1
        else:
            run = 0

    return {
        "eligible_bars": len(eligible_bars),
        "low_drive_bars": low_bars,
        "drive_coverage": round(coverage, 4),
        "average_core_onset_gap_steps": round(avg_gap, 4),
        "max_core_onset_gap_steps": int(max_gap),
        "false_launches": false_launches,
        "bar_core_onset_counts": counts,
        "gap_target_steps": int(max_gap_steps),
    }
