#!/usr/bin/env python3
"""
generate_dummy_mp3.py


MP3 gak bisa byte-exact 100% kayak WAV karena ada proses encoding lossy,
frame structure, dan metadata/overhead encoder. Script ini pakai pendekatan
ukur-dan-koreksi durasi WAV sumber lalu encode ulang pakai ffmpeg (CBR) supaya
hasil MP3 mendekati target size.

Catatan:
- Butuh ffmpeg terinstall di sistem.
- Output MP3 disimpan di folder yang sama dengan script (tanpa subfolder baru).
- File WAV sementara otomatis dihapus setelah proses convert selesai.
- File kecil seperti 10KB bisa punya deviasi relatif lebih besar karena overhead
  minimum frame MP3.
"""

import math
import os
import shutil
import subprocess
import sys
import tempfile
import wave
from array import array

SAMPLE_RATE = 44100
CHANNELS = 1
SAMPWIDTH = 2
AMPLITUDE = 16000
SEGMENT_DURATION = 0.4
FADE_MS = 8

SCALE = [261.63, 293.66, 329.63, 392.00, 440.00, 523.25, 587.33, 659.25]

SIZE_VARIANTS = [
    ("10kb", 10_000),
    ("50kb", 50_000),
    ("100kb", 100_000),
    ("500kb", 500_000),
    ("1mb", 1_000_000),
    ("2mb", 2_000_000),
    ("3mb", 3_000_000),
    ("5mb", 5_000_000),
    ("7mb", 7_000_000),
    ("10mb", 10_000_000),
]

OUTPUT_DIR = "."
BITRATE = "128k"
MAX_ATTEMPTS = 8


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


def encode_mp3(wav_path: str, mp3_path: str) -> None:
    cmd = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        wav_path,
        "-vn",
        "-ar",
        str(SAMPLE_RATE),
        "-ac",
        str(CHANNELS),
        "-c:a",
        "libmp3lame",
        "-b:a",
        BITRATE,
        "-map_metadata",
        "-1",
        mp3_path,
    ]
    subprocess.run(cmd, check=True)


def estimate_duration(target_bytes: int, bitrate_kbps: int = 128) -> float:
    bytes_per_sec = (bitrate_kbps * 1000) / 8
    return max(0.15, target_bytes / bytes_per_sec)


def generate_mp3_near_target(mp3_path: str, target_size: int, scale_offset: int):
    duration = estimate_duration(target_size, 128)
    actual = 0

    with tempfile.TemporaryDirectory() as tmpdir:
        wav_path = os.path.join(tmpdir, "temp.wav")
        trial_mp3 = os.path.join(tmpdir, "temp.mp3")

        for _ in range(MAX_ATTEMPTS):
            generate_wav(wav_path, duration, scale_offset)
            encode_mp3(wav_path, trial_mp3)
            actual = os.path.getsize(trial_mp3)
            diff = target_size - actual

            if abs(diff) <= 2048:
                break

            bytes_per_sec = 16000
            duration = max(0.15, duration + (diff / bytes_per_sec))

        shutil.copyfile(trial_mp3, mp3_path)

    return actual


def main():
    ensure_ffmpeg()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Generating {len(SIZE_VARIANTS)} dummy MP3 files...\n")

    for idx, (label, target_size) in enumerate(SIZE_VARIANTS):
        filename = f"Contohnya-MP3-{label}.mp3"
        filepath = os.path.join(OUTPUT_DIR, filename)
        scale_offset = idx % len(SCALE)
        actual_size = generate_mp3_near_target(filepath, target_size, scale_offset)
        diff = actual_size - target_size
        status = "OK-ish" if abs(diff) <= 2048 else f"diff {diff:+d} bytes"
        print(
            f"{filename:16s} target={target_size:>10,} B "
            f"actual={actual_size:>10,} B ({status})"
        )

    print(f"\nDone. Files saved to ./{OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
