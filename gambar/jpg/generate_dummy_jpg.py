#!/usr/bin/env python3
"""
generate_dummy_jpg.py

Generate dummy file JPG berukuran presisi (byte-exact) buat testing
upload/download/parsing gambar. Tiap file punya background abstrak
(shape acak dengan gradient), judul "Contohnya.web.id", teks ukuran file,
dan keterangan "Dummy JPG".

JPG itu format biner terkompresi, jadi bisa di-padding
byte-exact lewat trailing byte di akhir file.

Gak butuh dependency eksternal, cuma Python standard library + Pillow (optional).

Cara pakai:
python3 generate_dummy_jpg.py
python3 generate_dummy_jpg.py --sizes 50kb,25mb
python3 generate_dummy_jpg.py --outdir ./jpg
python3 generate_dummy_jpg.py --prefix Contohnya-JPG
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

JPG_TITLE = "Contohnya.web.id"
JPG_CAPTION = "Dummy JPG"

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
        img = Image.new('RGB', (width, height), '#FFFDF8')
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
                draw.ellipse([(cx-r, cy-r), (cx+r, cy+r)], fill=color, outline=color)
            else:
                x, y = random.randint(0, width), random.randint(0, height)
                w, h = random.randint(40, 220), random.randint(40, 220)
                draw.rectangle([(x, y), (x+w, y+h)], fill=color)

        try:
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        except Exception:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()

        draw.text((60, height // 2 - 30), JPG_TITLE, fill="#1a1a1a", font=font_large)
        draw.text((60, height // 2 + 10), f"Ukuran: {format_label(label)}", fill="#333333", font=font_small)
        draw.text((60, height // 2 + 40), JPG_CAPTION, fill="#555555", font=font_small)

        from io import BytesIO
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=85, optimize=False)
        return buffer.getvalue()
    else:
        from io import BytesIO
        img = Image.new('RGB', (width, height), '#FFFDF8')
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=85, optimize=False)
        return buffer.getvalue()


def pad_jpg_to_size(jpg_bytes: bytes, target_bytes: int) -> bytes:
    base_bytes = len(jpg_bytes)
    if base_bytes > target_bytes:
        raise ValueError(
            f"Base JPG ({base_bytes} bytes) sudah lebih besar dari target ({target_bytes} bytes). "
            "Kurangi jumlah shape background atau naikkan target size."
        )

    padding_len = target_bytes - base_bytes
    padding = b'\x00' * padding_len
    padded = jpg_bytes + padding

    actual = len(padded)
    diff = target_bytes - actual
    if diff != 0:
        padding_len = max(0, padding_len + diff)
        padding = b'\x00' * padding_len
        padded = jpg_bytes + padding

    return padded


def main():
    parser = argparse.ArgumentParser(description="Generate dummy JPG ukuran presisi.")
    parser.add_argument(
        "--sizes",
        type=str,
        default=None,
        help="Comma-separated ukuran, misal '1kb,5mb'. Default: 10 varian standar (max 25MB).",
    )
    parser.add_argument("--outdir", type=str, default=".", help="Folder output.")
    parser.add_argument(
        "--prefix", type=str, default="Contohnya-JPG", help="Prefix nama file output."
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
        jpg_bytes = make_abstract_background(WIDTH, HEIGHT, format_label(label))
        base_bytes = len(jpg_bytes)
        if base_bytes > size:
            print(f"{label:>8} -> SKIP, base JPG ({base_bytes} bytes) > target ({size} bytes)")
            continue
        padded = pad_jpg_to_size(jpg_bytes, size)
        out_path = os.path.join(args.outdir, f"{args.prefix}-{format_label(label)}.jpg")
        with open(out_path, "wb") as f:
            f.write(padded)
        actual = os.path.getsize(out_path)
        status = "OK" if actual == size else f"MELESET ({actual} bytes)"
        print(f"{label:>8} -> {out_path} [{actual} bytes] {status}")


if __name__ == "__main__":
    main()
