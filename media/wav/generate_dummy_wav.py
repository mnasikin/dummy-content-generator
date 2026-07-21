"""
generate_dummy_wav.py


Pure stdlib (wave, struct, math, array) - no external plugin/library needed,
unlike MP3/OGG/FLAC yang butuh encoder eksternal.

WAV = raw PCM + 44-byte header, jadi size-nya byte-exact ke target
(pakai basis desimal 1 kB = 1000 byte, 1 MB = 1.000.000 byte, biar
match sama angka yang ditunjukin file explorer/OS pada umumnya).

Tiap file mainin melodi kecil (arpeggio naik-turun pentatonic scale),
jadi suaranya berubah-ubah dalam 1 file, bukan beep monoton dari awal
sampai akhir. Tiap size variant juga mulai dari nada awal yang beda,
jadi antar file kedengeran beda juga.
"""

import wave
import math
import os
from array import array

SAMPLE_RATE = 44100
CHANNELS = 1
SAMPWIDTH = 2  # 16-bit PCM
HEADER_SIZE = 44
AMPLITUDE = 16000  # headroom di bawah 32767 biar ga clipping

# pentatonic scale (Hz), C4 pentatonic - terdengar enak/harmonis walau random urutan
SCALE = [261.63, 293.66, 329.63, 392.00, 440.00, 523.25, 587.33, 659.25]

SEGMENT_DURATION = 0.4  # detik per nada
FADE_MS = 8  # fade in/out tiap segmen biar ga ada klik/pop antar nada

# label, target size dalam byte (basis desimal: 1 kB = 1000, 1 MB = 1_000_000)
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


def build_pattern(scale_offset: int):
    """Rotate scale per file, lalu bikin pola naik-turun (arpeggio)."""
    scale = SCALE[scale_offset:] + SCALE[:scale_offset]
    descending = scale[-2:0:-1]  # turun dari nada kedua-teratas ke nada kedua-terbawah
    return scale + descending


def generate_wav(filepath: str, target_size: int, scale_offset: int) -> int:
    data_bytes = target_size - HEADER_SIZE
    data_bytes -= data_bytes % (SAMPWIDTH * CHANNELS)  # genapin ke kelipatan sample
    num_samples = data_bytes // (SAMPWIDTH * CHANNELS)

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
                val *= i / fade_len
            elif i > seg_len - fade_len:
                val *= (seg_len - i) / fade_len
            samples.append(int(val))

        filled += seg_len
        note_i += 1

    with wave.open(filepath, "w") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(SAMPWIDTH)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(samples.tobytes())

    return os.path.getsize(filepath)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Generating {len(SIZE_VARIANTS)} dummy WAV files...\n")

    for idx, (label, target_size) in enumerate(SIZE_VARIANTS):
        filename = f"Contohnya-WAV-{label}.wav"
        filepath = os.path.join(OUTPUT_DIR, filename)
        scale_offset = idx % len(SCALE)
        actual_size = generate_wav(filepath, target_size, scale_offset)
        diff = actual_size - target_size
        status = "OK" if diff == 0 else f"diff {diff:+d} bytes"
        print(
            f"{filename:16s} target={target_size:>10,} B  "
            f"actual={actual_size:>10,} B  ({status})"
        )

    print(f"\nDone. Files saved to ./{OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
