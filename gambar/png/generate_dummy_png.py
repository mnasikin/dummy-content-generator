#!/usr/bin/env python3
"""
generate_dummy_png.py

Generate dummy file PNG berukuran presisi (byte-exact) buat testing
upload/download/parsing gambar. Tiap file punya background abstrak
(shape acak dengan gradient), judul "Contohnya.web.id", teks ukuran file,
dan keterangan "Dummy PNG".

PNG itu format container terkompresi, jadi bisa di-padding
byte-exact lewat estimasi + koreksi iteratif (trailing byte setelah IEND
umumnya diabaikan sama kebanyakan decoder/viewer).

Gak butuh dependency eksternal, cuma Python standard library + Pillow (optional).

Cara pakai:
python3 generate_dummy_png.py                     # generate 10 varian ukuran default
python3 generate_dummy_png.py --sizes 50kb,25mb    # generate ukuran tertentu aja
python3 generate_dummy_png.py --outdir ./png       # ganti folder output
python3 generate_dummy_png.py --prefix Contohnya-PNG  # ganti prefix nama file
"""

import argparse
import os
import random
import re

try:
    from PIL import Image, ImageDraw, ImageFont
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False
    print("Warning: Pillow tidak terinstall. Menggunakan fallback approach.")
    print("Install dengan: pip install Pillow")

PNG_TITLE = "Contohnya.web.id"
PNG_CAPTION = "Dummy PNG"

WIDTH, HEIGHT = 800, 600

DEFAULT_SIZES = {
    "50kb": 50_000,
    "100kb": 100_000,
    "250kb": 250_000,
    "500kb": 500_000,
    "1mb": 1_000_000,
    "2mb": 2_000_000,
    "5mb": 5_000_000,
    "10mb": 10_000_000,
    "15mb": 15_000_000,
    "25mb": 25_000_000,
}

DEFAULT_SIZES_BINARY = {
    "1kb": 1024,
    "5kb": 5 * 1024,
    "10kb": 10 * 1024,
    "50kb": 50 * 1024,
    "100kb": 100 * 1024,
    "500kb": 500 * 1024,
    "1mb": 1024 * 1024,
    "2mb": 2 * 1024 * 1024,
    "5mb": 5 * 1024 * 1024,
    "25mb": 25 * 1024 * 1024,
}

COLORS = ["#FF6B4A", "#FFA26B", "#4A90E2", "#7ED6C4", "#FFD56B", "#B693F5"]


def parse_size(s: str, binary: bool = False) -> int:
    s = s.strip().lower()
    m = re.match(r"^([\d.]+)\s*(kb|mb|gb|b)?$", s)
    if not m:
        raise ValueError(f"Gak ngerti format ukuran: {s}")
    num, unit = m.groups()
    num = float(num)
    base = 1024 if binary else 1000
    mult = {"b": 1, "kb": base, "mb": base**2, "gb": base**3, None: 1}[unit]
    return int(num * mult)


def format_label(label: str) -> str:
    m = re.match(r"^([\d.]+)(kb|mb|gb|b)$", label.lower())
    if not m:
        return label
    num, unit = m.groups()
    return f"{num}{unit.upper()}"


def make_abstract_background(width: int, height: int, label: str = "") -> bytes:
    c1, c2 = random.sample(COLORS, 2)

    if PILLOW_AVAILABLE:
        img = Image.new("RGB", (width, height), "#FFFDF8")
        draw = ImageDraw.Draw(img)

        for i in range(height):
            r = int(int(c1[1:3], 16) * (1 - i / height) + int(c2[1:3], 16) * (i / height))
            g = int(int(c1[3:5], 16) * (1 - i / height) + int(c2[3:5], 16) * (i / height))
            b = int(int(c1[5:7], 16) * (1 - i / height) + int(c2[5:7], 16) * (i / height))
            draw.rectangle([(0, i), (width, i + 1)], fill=(r, g, b))

        for _ in range(14):
            shape_type = random.choice(["circle", "circle", "rect", "rect"])
            color = random.choice(COLORS)

            if shape_type == "circle":
                cx, cy, r = random.randint(0, width), random.randint(0, height), random.randint(30, 180)
                draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], fill=color, outline=color)
            else:
                x, y = random.randint(0, width), random.randint(0, height)
                w, h = random.randint(40, 220), random.randint(40, 220)
                draw.rectangle([(x, y), (x + w, y + h)], fill=color)

        try:
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        except Exception:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()

        draw.text((60, height // 2 - 30), PNG_TITLE, fill="#1a1a1a", font=font_large)
        draw.text((60, height // 2 + 10), f"Ukuran: {format_label(label)}", fill="#333333", font=font_small)
        draw.text((60, height // 2 + 40), PNG_CAPTION, fill="#555555", font=font_small)

        from io import BytesIO
        buffer = BytesIO()
        img.save(buffer, format="PNG", compress_level=9)
        return buffer.getvalue()
    else:
        from io import BytesIO
        img = Image.new("RGB", (width, height), "#FFFDF8")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()


def pad_png_to_size(png_bytes: bytes, target_bytes: int) -> bytes:
    base_bytes = len(png_bytes)
    if base_bytes > target_bytes:
        raise ValueError(
            f"Base PNG ({base_bytes} bytes) sudah lebih besar dari target ({target_bytes} bytes). "
            "Kurangi jumlah shape background atau naikkan target size."
        )

    iend_pos = png_bytes.rfind(b"IEND") - 4
    if iend_pos < 0:
        padding_len = target_bytes - base_bytes
        return png_bytes + b"\x00" * padding_len

    head = png_bytes[:iend_pos]
    tail = png_bytes[iend_pos:]

    overhead = 12
    needed_total = target_bytes - base_bytes
    if needed_total < overhead:
        return png_bytes + b"\x00" * needed_total

    data_len = needed_total - overhead
    data = b"\x00" * data_len

    import struct
    import zlib

    chunk_type = b"dmDA"
    length_field = struct.pack(">I", data_len)
    crc = struct.pack(">I", zlib.crc32(chunk_type + data) & 0xFFFFFFFF)
    custom_chunk = length_field + chunk_type + data + crc

    padded = head + custom_chunk + tail

    actual = len(padded)
    diff = target_bytes - actual
    if diff != 0:
        padded = padded + (b"\x00" * diff if diff > 0 else b"")
        padded = padded[:target_bytes]

    return padded


def main():
    parser = argparse.ArgumentParser(description="Generate dummy PNG ukuran presisi.")
    parser.add_argument(
        "--sizes",
        type=str,
        default=None,
        help="Comma-separated ukuran, misal '1kb,5mb'. Default: 10 varian standar (max 25MB).",
    )
    parser.add_argument("--outdir", type=str, default=".", help="Folder output.")
    parser.add_argument(
        "--prefix", type=str, default="Contohnya-PNG", help="Prefix nama file output."
    )
    parser.add_argument(
        "--binary",
        action="store_true",
        help="Pakai definisi binary (1 MB = 1024x1024 bytes) instead of decimal (default).",
    )
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    default_table = DEFAULT_SIZES_BINARY if args.binary else DEFAULT_SIZES

    if args.sizes:
        labels = [s.strip() for s in args.sizes.split(",")]
        targets = {}
        for label in labels:
            if label.lower() in default_table:
                targets[label.lower()] = default_table[label.lower()]
            else:
                targets[label.lower()] = parse_size(label, binary=args.binary)
    else:
        targets = default_table

    for label, size in sorted(targets.items(), key=lambda kv: kv[1]):
        png_bytes = make_abstract_background(WIDTH, HEIGHT, format_label(label))
        base_bytes = len(png_bytes)
        if base_bytes > size:
            print(f"{label:>8} -> SKIP, base PNG ({base_bytes} bytes) > target ({size} bytes)")
            continue
        padded = pad_png_to_size(png_bytes, size)
        out_path = os.path.join(args.outdir, f"{args.prefix}-{format_label(label)}.png")
        with open(out_path, "wb") as f:
            f.write(padded)
        actual = os.path.getsize(out_path)
        status = "OK" if actual == size else f"MELESET ({actual} bytes)"
        print(f"{label:>8} -> {out_path} [{actual} bytes] {status}")


if __name__ == "__main__":
    main()
