from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from mido import Message, MetaMessage, MidiFile, MidiTrack, bpm2tempo

from .composer import NoteEvent


TRACK_LABELS = {
    "bass": "RIME YM2612 FM Bass",
    "harmony": "RIME FM Harmony + Friction",
    "lead": "RIME YM2612 FM Lead",
    "drums": "RIME Genesis DAC + PSG + FM Drums",
}


def export_midi(events: Dict[str, List[NoteEvent]], tempo_bpm: int, output_path: str | Path, steps_per_beat: int = 4) -> None:
    mid = MidiFile(type=1, ticks_per_beat=480)
    ticks_per_step = mid.ticks_per_beat // steps_per_beat

    meta = MidiTrack()
    mid.tracks.append(meta)
    meta.append(MetaMessage("track_name", name="RIME v0.005 Conductor", time=0))
    meta.append(MetaMessage("set_tempo", tempo=bpm2tempo(tempo_bpm), time=0))
    meta.append(MetaMessage("time_signature", numerator=4, denominator=4, time=0))
    meta.append(MetaMessage("text", text="Genesis-oriented composition; MIDI is an interchange representation, not YM2612 register data.", time=0))

    program_map = {"bass": 38, "harmony": 81, "lead": 80, "drums": 0}

    for name in ["bass", "harmony", "lead", "drums"]:
        track = MidiTrack()
        mid.tracks.append(track)
        track.append(MetaMessage("track_name", name=TRACK_LABELS[name], time=0))
        if name != "drums":
            channel = events[name][0].channel if events[name] else 0
            track.append(Message("program_change", program=program_map[name], channel=channel, time=0))

        timeline = []
        for e in events[name]:
            start = int(round(e.start_step * ticks_per_step))
            end = int(round((e.start_step + e.duration_steps) * ticks_per_step))
            timeline.append((start, 1, e))
            timeline.append((end, 0, e))
        timeline.sort(key=lambda x: (x[0], x[1]))

        last_tick = 0
        for tick, kind, e in timeline:
            delta = max(0, tick - last_tick)
            if kind == 1:
                track.append(Message("note_on", note=e.pitch, velocity=e.velocity, channel=e.channel, time=delta))
            else:
                track.append(Message("note_off", note=e.pitch, velocity=0, channel=e.channel, time=delta))
            last_tick = tick

    mid.save(output_path)
