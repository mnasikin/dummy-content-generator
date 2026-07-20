#!/usr/bin/env python3
"""
generate_dummy_avif.py

Generate dummy file AVIF berukuran presisi (byte-exact-ish target with filler)
buat testing upload/download/parsing gambar. Tiap file berisi gambar AVIF asli
(bukan cuma file acak ber-ekstensi .avif), lalu dipad dengan trailing filler
agar ukurannya pas target.

Install dependency:

Opsi A - pakai pillow-heif:
    python3 -m pip install --break-system-packages --upgrade pillow pillow-heif

Opsi B - pakai pillow-avif-plugin:
    python3 -m pip install --break-system-packages --upgrade pillow pillow-avif-plugin

Catatan:
- pillow-heif bisa di-install via pip dan dipakai sebagai plugin Pillow untuk HEIF/AVIF.
- pillow-avif-plugin menambah support AVIF ke Pillow, dan harus diaktifkan dengan import pillow_avif.
- Pada environment Python yang externally managed, pip bisa butuh flag --break-system-packages.

Script ini mencoba urutan fallback aman:
- pillow_heif.register_avif_opener()
- import pillow_avif
- langsung Pillow save(format="AVIF")

Maksimal generate 10 file.
Default ukuran berhenti di 15MB.

Cara pakai:
python3 generate_dummy_avif.py
python3 generate_dummy_avif.py --sizes 25kb,1mb,15mb
python3 generate_dummy_avif.py --outdir ./avif
python3 generate_dummy_avif.py --prefix Contohnya-AVIF
"""

import argparse
import io
import math
import os
import random
import re

from PIL import Image, ImageDraw, ImageFont


AVIF_TITLE = "Contohnya.web.id"
AVIF_CAPTION = "Dummy File AVIF"
MAX_FILES = 10

DEFAULT_SIZES = {
    "25kb": 25_000,
    "50kb": 50_000,
    "100kb": 100_000,
    "250kb": 250_000,
    "500kb": 500_000,
    "1mb": 1_000_000,
    "2mb": 2_000_000,
    "3mb": 3_000_000,
    "5mb": 5_000_000,
    "15mb": 15_000_000,
}

DEFAULT_SIZES_BINARY = {
    "25kb": 25 * 1024,
    "50kb": 50 * 1024,
    "100kb": 100 * 1024,
    "250kb": 250 * 1024,
    "500kb": 500 * 1024,
    "1mb": 1024 * 1024,
    "2mb": 2 * 1024 * 1024,
    "3mb": 3 * 1024 * 1024,
    "5mb": 5 * 1024 * 1024,
    "15mb": 15 * 1024 * 1024,
}


def ensure_avif_support():
    try:
        from pillow_heif import register_avif_opener
        register_avif_opener()
        return "pillow-heif"
    except Exception:
        pass

    try:
        import pillow_avif  # noqa: F401
        return "pillow-avif-plugin"
    except Exception:
        pass

    test = io.BytesIO()
    try:
        Image.new("RGB", (8, 8), (0, 0, 0)).save(test, format="AVIF")
        return "native-pillow"
    except Exception as e:
        raise SystemExit(
            "AVIF belum didukung di environment ini.\n"
            "Install salah satu dependency berikut:\n"
            "  python3 -m pip install --break-system-packages --upgrade pillow pillow-heif\n"
            "atau:\n"
            "  python3 -m pip install --break-system-packages --upgrade pillow pillow-avif-plugin\n"
            "Kalau pakai pillow-avif-plugin, plugin harus diimport (import pillow_avif).\n"
            f"Detail error: {e}"
        )


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


def choose_canvas(target_size: int):
    edge = int(max(256, min(2200, math.sqrt(max(target_size // 6, 256 * 256)))))
    return edge, edge


def fit_text(draw, text, font, max_width):
    text = str(text)
    while text:
        bbox = draw.textbbox((0, 0), text, font=font)
        if (bbox[2] - bbox[0]) <= max_width:
            return text
        text = text[:-1]
    return ""


def make_image(label: str, target_size: int) -> Image.Image:
    width, height = choose_canvas(target_size)
    rnd = random.Random(hash((label, target_size)) & 0xFFFFFFFF)
    img = Image.new("RGB", (width, height))
    px = img.load()

    c1 = (rnd.randint(10, 80), rnd.randint(30, 120), rnd.randint(70, 160))
    c2 = (rnd.randint(110, 220), rnd.randint(60, 180), rnd.randint(20, 120))

    for y in range(height):
        t = y / max(1, height - 1)
        r = int(c1[0] * (1 - t) + c2[0] * t)
        g = int(c1[1] * (1 - t) + c2[1] * t)
        b = int(c1[2] * (1 - t) + c2[2] * t)
        for x in range(width):
            wobble = int(18 * math.sin((x * 0.02) + (y * 0.013)))
            px[x, y] = (
                max(0, min(255, r + wobble)),
                max(0, min(255, g + wobble // 2)),
                max(0, min(255, b - wobble // 2)),
            )

    draw = ImageDraw.Draw(img, "RGBA")
    for _ in range(22):
        x1 = rnd.randint(0, width - 1)
        y1 = rnd.randint(0, height - 1)
        x2 = rnd.randint(x1, min(width, x1 + rnd.randint(40, max(60, width // 2))))
        y2 = rnd.randint(y1, min(height, y1 + rnd.randint(40, max(60, height // 2))))
        color = (
            rnd.randint(20, 255),
            rnd.randint(20, 255),
            rnd.randint(20, 255),
            rnd.randint(40, 120),
        )
        if rnd.random() < 0.5:
            draw.ellipse([x1, y1, x2, y2], fill=color)
        else:
            draw.rounded_rectangle([x1, y1, x2, y2], radius=rnd.randint(8, 40), fill=color)

    overlay_h = max(120, height // 5)
    draw.rounded_rectangle(
        [20, height - overlay_h - 20, width - 20, height - 20],
        radius=18,
        fill=(0, 0, 0, 180),
        outline=(255, 255, 255, 220),
        width=2,
    )

    font_big = ImageFont.load_default()
    font_small = ImageFont.load_default()
    title = fit_text(draw, AVIF_TITLE, font_big, width - 80)
    sub1 = fit_text(draw, format_label(label), font_small, width - 80)
    sub2 = fit_text(draw, AVIF_CAPTION, font_small, width - 80)

    draw.text((40, height - overlay_h), title, fill=(255, 255, 255), font=font_big)
    draw.text((40, height - overlay_h + 28), sub1, fill=(230, 230, 230), font=font_small)
    draw.text((40, height - overlay_h + 52), sub2, fill=(200, 200, 200), font=font_small)

    return img


def build_avif(label: str, target_size: int) -> bytes:
    img = make_image(label, target_size)
    buf = io.BytesIO()
    img.save(buf, format="AVIF", quality=90)
    return buf.getvalue()


def pad_avif_to_size(avif_bytes: bytes, target_bytes: int) -> bytes:
    base_len = len(avif_bytes)
    if base_len > target_bytes:
        raise ValueError(
            f"Base AVIF ({base_len} bytes) sudah lebih besar dari target ({target_bytes} bytes)."
        )
    if base_len == target_bytes:
        return avif_bytes
    filler = b"\x00" * (target_bytes - base_len)
    return avif_bytes + filler


def main():
    parser = argparse.ArgumentParser(description="Generate dummy AVIF ukuran presisi.")
    parser.add_argument(
        "--sizes",
        type=str,
        default=None,
        help="Comma-separated ukuran, misal '25kb,1mb,15mb'. Default: varian ukuran umum AVIF sampai 15MB.",
    )
    parser.add_argument("--outdir", type=str, default=".", help="Folder output.")
    parser.add_argument(
        "--prefix", type=str, default="Contohnya-AVIF", help="Prefix nama file output."
    )
    parser.add_argument(
        "--binary",
        action="store_true",
        help="Pakai definisi binary (1 KB = 1024 bytes) instead of decimal (default).",
    )
    args = parser.parse_args()

    ensure_avif_support()

    os.makedirs(args.outdir, exist_ok=True)
    default_table = DEFAULT_SIZES_BINARY if args.binary else DEFAULT_SIZES

    if args.sizes:
        labels = [s.strip() for s in args.sizes.split(",")]
        if len(labels) > MAX_FILES:
            raise SystemExit(f"Maksimal {MAX_FILES} ukuran per run")
        targets = {}
        for label in labels:
            if label.lower() in default_table:
                targets[label.lower()] = default_table[label.lower()]
            else:
                targets[label.lower()] = parse_size(label, binary=args.binary)
    else:
        targets = default_table

    if len(targets) > MAX_FILES:
        raise SystemExit(f"Maksimal generate {MAX_FILES} file")

    for label, size in sorted(targets.items(), key=lambda kv: kv[1]):
        avif_base = build_avif(format_label(label), size)
        base_bytes = len(avif_base)
        if base_bytes > size:
            print(f"{label:>8} -> SKIP, base AVIF ({base_bytes} bytes) > target ({size} bytes)")
            continue

        padded = pad_avif_to_size(avif_base, size)
        out_path = os.path.join(args.outdir, f"{args.prefix}-{format_label(label)}.avif")

        with open(out_path, "wb") as f:
            f.write(padded)

        actual = os.path.getsize(out_path)
        status = "OK" if actual == size else f"MELESET ({actual} bytes)"
        print(f"{label:>8} -> {out_path} [{actual} bytes] {status}")


if __name__ == "__main__":
    main()