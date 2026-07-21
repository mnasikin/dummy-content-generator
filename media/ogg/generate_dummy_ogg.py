#!/usr/bin/env python3
"""
generate_dummy_ogg.py

Generate dummy file OGG (.ogg) buat testing upload, preview, dan size validation.

OGG/Vorbis gak bisa byte-exact 100% kayak WAV karena hasil akhirnya dipengaruhi
encoding lossy, bitrate/quality behavior encoder, dan overhead container.
Script ini pakai pendekatan ukur-dan-koreksi durasi WAV sumber lalu encode ulang
pakai ffmpeg supaya hasil OGG mendekati target size.

Catatan:
- Butuh ffmpeg terinstall di sistem.
- Output OGG disimpan di folder yang sama dengan script, kecuali lo set --outdir.
- File WAV sementara otomatis dihapus setelah proses convert selesai.
- File kecil seperti 10KB bisa punya deviasi relatif lebih besar.
"""

import argparse
import math
import os
import re
import shutil
import subprocess
import tempfile
import wave
from array import array
from typing import Dict, List, Tuple

SAMPLE_RATE = 44100
CHANNELS = 1
SAMPWIDTH = 2
AMPLITUDE = 16000
SEGMENT_DURATION = 0.4
FADE_MS = 8

SCALE = [261.63, 293.66, 329.63, 392.00, 440.00, 523.25, 587.33, 659.25]

DEFAULT_SIZES = [
    "10kb",
    "50kb",
    "100kb",
    "500kb",
    "1mb",
    "2mb",
    "3mb",
    "5mb",
    "7mb",
    "10mb",
]

MAX_DEFAULT_COUNT = 10
DEFAULT_MAX_SIZE_LABEL = "10mb"
OUTPUT_DIR = "."
BITRATE = "192k"
BITRATE_KBPS = 192
MAX_ATTEMPTS = 10
TARGET_TOLERANCE = 4096


def parse_size(s: str, binary: bool = False) -> int:
    s = s.strip().lower()
    m = re.match(r"^([\d.]+)\s*(b|kb|mb|gb)?$", s)
    if not m:
        raise ValueError(f"Gak ngerti format ukuran: {s}")
    num, unit = m.groups()
    num = float(num)
    base = 1024 if binary else 1000
    mult = {None: 1, "b": 1, "kb": base, "mb": base**2, "gb": base**3}[unit]
    return int(num * mult)


def format_label(label: str) -> str:
    m = re.match(r"^([\d.]+)\s*(b|kb|mb|gb)$", label.strip().lower())
    if not m:
        return label.strip()
    num, unit = m.groups()
    return f"{num}{unit.upper()}"


def build_default_targets(binary: bool = False) -> Dict[str, int]:
    return {label: parse_size(label, binary=binary) for label in DEFAULT_SIZES}


def filtered_default_labels(max_size_label: str, count: int, binary: bool = False) -> List[str]:
    max_bytes = parse_size(max_size_label, binary=binary)
    labels = [label for label in DEFAULT_SIZES if parse_size(label, binary=binary) <= max_bytes]
    if not labels:
        raise ValueError("Tidak ada default size yang <= --max-size")
    return labels[:count]


def resolve_targets(args) -> List[Tuple[str, int]]:
    if args.sizes:
        labels = [x.strip() for x in args.sizes.split(",") if x.strip()]
        if len(labels) > MAX_DEFAULT_COUNT:
            raise ValueError(f"Maksimal {MAX_DEFAULT_COUNT} ukuran per generate.")
        return sorted(
            [(label.lower(), parse_size(label, binary=args.binary)) for label in labels],
            key=lambda kv: kv[1],
        )

    labels = filtered_default_labels(args.max_size, args.count, binary=args.binary)
    table = build_default_targets(binary=args.binary)
    return [(label, table[label]) for label in labels]


def ensure_ffmpeg():
    if shutil.which("ffmpeg"):
        return
    msg = (
        "Error: ffmpeg gak ketemu di PATH.\n"
        "Install dulu ffmpeg:\n"
        "- Ubuntu/Debian: sudo apt install ffmpeg\n"
        "- macOS (Homebrew): brew install ffmpeg\n"
        "- Windows: download ffmpeg lalu tambahin ke PATH\n"
    )
    raise SystemExit(msg)


def build_pattern(scale_offset: int):
    scale = SCALE[scale_offset:] + SCALE[:scale_offset]
    descending = scale[-2:0:-1]
    return scale + descending


def generate_wav(filepath: str, duration_sec: float, scale_offset: int) -> None:
    num_samples = max(1, int(round(duration_sec * SAMPLE_RATE)))
    segment_len = int(SEGMENT_DURATION * SAMPLE_RATE)
    fade_len = int(FADE_MS / 1000 * SAMPLE_RATE)
    pattern = build_pattern(scale_offset)

    samples = array("h")
    filled = 0
    note_i = 0

    while filled < num_samples:
        freq = pattern[note_i % len(pattern)]
        seg_len = min(segment_len, num_samples - filled)

        for i in range(seg_len):
            val = AMPLITUDE * math.sin(2 * math.pi * freq * i / SAMPLE_RATE)
            if i < fade_len:
                val *= i / fade_len if fade_len else 1
            elif i > seg_len - fade_len:
                val *= (seg_len - i) / fade_len if fade_len else 1
            samples.append(int(val))

        filled += seg_len
        note_i += 1

    with wave.open(filepath, "w") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(SAMPWIDTH)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(samples.tobytes())


def encode_ogg(wav_path: str, ogg_path: str) -> None:
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", wav_path,
        "-vn",
        "-ar", str(SAMPLE_RATE),
        "-ac", str(CHANNELS),
        "-c:a", "libvorbis",
        "-b:a", BITRATE,
        "-minrate", BITRATE,
        "-maxrate", BITRATE,
        "-bufsize", "384k",
        "-map_metadata", "-1",
        ogg_path,
    ]
    subprocess.run(cmd, check=True)


def estimate_duration(target_bytes: int, bitrate_kbps: int = BITRATE_KBPS) -> float:
    bytes_per_sec = (bitrate_kbps * 1000) / 8
    return max(0.12, target_bytes / bytes_per_sec)


def generate_ogg_near_target(ogg_path: str, target_size: int, scale_offset: int) -> int:
    duration = estimate_duration(target_size, BITRATE_KBPS)
    best_actual = None
    best_diff = None
    best_blob = None

    with tempfile.TemporaryDirectory() as tmpdir:
        wav_path = os.path.join(tmpdir, "temp.wav")
        trial_ogg = os.path.join(tmpdir, "temp.ogg")

        for _ in range(MAX_ATTEMPTS):
            generate_wav(wav_path, duration, scale_offset)
            encode_ogg(wav_path, trial_ogg)
            actual = os.path.getsize(trial_ogg)
            diff = actual - target_size

            if best_diff is None or abs(diff) < abs(best_diff):
                best_actual = actual
                best_diff = diff
                with open(trial_ogg, "rb") as f:
                    best_blob = f.read()

            if abs(diff) <= TARGET_TOLERANCE:
                break

            measured_bytes_per_sec = actual / max(duration, 0.001)
            if measured_bytes_per_sec <= 0:
                measured_bytes_per_sec = (BITRATE_KBPS * 1000) / 8
            duration = max(0.12, duration + ((target_size - actual) / measured_bytes_per_sec))

        with open(ogg_path, "wb") as f:
            f.write(best_blob)

    return best_actual


def main():
    parser = argparse.ArgumentParser(description="Generate dummy OGG ukuran mendekati target.")
    parser.add_argument(
        "--sizes",
        type=str,
        default=None,
        help="Comma-separated ukuran custom, misal '10kb,100kb,1mb'. Maks 10 ukuran.",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=MAX_DEFAULT_COUNT,
        help="Jumlah varian default yang digenerate. Maks 10. Default 10.",
    )
    parser.add_argument(
        "--max-size",
        type=str,
        default=DEFAULT_MAX_SIZE_LABEL,
        help="Batas size terbesar untuk varian default. Default 10mb.",
    )
    parser.add_argument("--outdir", type=str, default=OUTPUT_DIR, help="Folder output.")
    parser.add_argument("--prefix", type=str, default="Contohnya-OGG", help="Prefix nama file output.")
    parser.add_argument(
        "--binary",
        action="store_true",
        help="Pakai definisi binary (1 MB = 1024x1024 bytes) instead of decimal.",
    )
    args = parser.parse_args()

    if args.count < 1:
        raise ValueError("--count minimal 1")
    if args.count > MAX_DEFAULT_COUNT:
        raise ValueError(f"--count maksimal {MAX_DEFAULT_COUNT}")

    ensure_ffmpeg()
    os.makedirs(args.outdir, exist_ok=True)
    targets = resolve_targets(args)

    print(f"Generating {len(targets)} dummy OGG files...\n")

    for idx, (raw_label, target_size) in enumerate(targets):
        pretty = format_label(raw_label)
        filename = f"{args.prefix}-{pretty}.ogg"
        filepath = os.path.join(args.outdir, filename)
        scale_offset = idx % len(SCALE)
        actual_size = generate_ogg_near_target(filepath, target_size, scale_offset)
        diff = actual_size - target_size
        status = "OK-ish" if abs(diff) <= TARGET_TOLERANCE else f"diff {diff:+d} bytes"
        print(
            f"{filename:20s} target={target_size:>10,} B "
            f"actual={actual_size:>10,} B ({status})"
        )

    print(f"\nDone. Files saved to {args.outdir}/")


if __name__ == "__main__":
    main()
