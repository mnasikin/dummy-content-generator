#!/usr/bin/env python3
"""
generate_dummy_ico.py

Generate dummy file ICO berukuran presisi (byte-exact-ish target with filler)
buat testing upload/download/parsing file. Tiap file berisi ikon .ico valid
dengan visual sederhana bertema "Contohnya.web.id" dan label "Dummy File ICO".

Output .ico aman:
- bukan file executable
- tidak mengandung script
- hanya container icon Windows (.ico)
- cocok untuk testing upload, preview, MIME, dan validasi ukuran file

Catatan:
- ICO dasar dibuat manual tanpa dependency eksternal.
- Agar ukuran file pas target, data di akhir file dipad dengan trailing bytes.
  Banyak parser/previewer tetap membaca icon pertama dengan normal karena
  struktur ICO valid ada di awal file.
- Jika target terlalu kecil untuk menampung ICO minimum, file akan di-skip.

Cara pakai:
python3 generate_dummy_ico.py
python3 generate_dummy_ico.py --sizes 25kb,1mb
python3 generate_dummy_ico.py --outdir ./ico
python3 generate_dummy_ico.py --prefix Contohnya-ICO
"""

import argparse
import os
import re
import struct
import zlib

ICO_TITLE = "Contohnya.web.id"
ICO_CAPTION = "Dummy File ICO"

DEFAULT_SIZES = {
    "10kb": 10_000,
    "25kb": 25_000,
    "50kb": 50_000,
    "100kb": 100_000,
    "150kb": 150_000,
    "250kb": 250_000,
    "500kb": 500_000,
    "750kb": 750_000,
    "1mb": 1_000_000,
    "1.5mb": 1_500_000,
    "2mb": 2_000_000,
}

DEFAULT_SIZES_BINARY = {
    "10kb": 10 * 1024,
    "25kb": 25 * 1024,
    "50kb": 50 * 1024,
    "100kb": 100 * 1024,
    "150kb": 150 * 1024,
    "250kb": 250 * 1024,
    "500kb": 500 * 1024,
    "750kb": 750 * 1024,
    "1mb": 1024 * 1024,
    "1.5mb": int(1.5 * 1024 * 1024),
    "2mb": 2 * 1024 * 1024,
}


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


def png_chunk(chunk_type: bytes, data: bytes) -> bytes:
    crc = zlib.crc32(chunk_type)
    crc = zlib.crc32(data, crc) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + chunk_type + data + struct.pack(">I", crc)


def make_rgba_icon(size: int, label: str):
    pixels = bytearray()
    bg_top = (35, 23, 60, 255)
    bg_bottom = (93, 56, 120, 255)
    accent = (255, 180, 80, 255)
    white = (245, 245, 250, 255)
    border = (170, 120, 220, 255)

    for y in range(size):
        t = y / max(1, size - 1)
        r = int(bg_top[0] * (1 - t) + bg_bottom[0] * t)
        g = int(bg_top[1] * (1 - t) + bg_bottom[1] * t)
        b = int(bg_top[2] * (1 - t) + bg_bottom[2] * t)

        row = bytearray([0])  # PNG filter type 0
        for x in range(size):
            rr, gg, bb, aa = r, g, b, 255

            pad = max(2, size // 16)
            if x < pad or y < pad or x >= size - pad or y >= size - pad:
                rr, gg, bb, aa = border

            cx, cy = size // 2, size // 2
            dx, dy = x - cx, y - cy
            rad = size * 0.22
            if dx * dx + dy * dy <= rad * rad:
                rr, gg, bb, aa = accent

            if abs(x - cx) < max(1, size // 24) and abs(y - cy) < size // 5:
                rr, gg, bb, aa = white
            if abs(y - cy) < max(1, size // 24) and abs(x - cx) < size // 5:
                rr, gg, bb, aa = white

            row.extend((rr, gg, bb, aa))
        pixels.extend(row)

    return bytes(pixels)


def build_png(size: int, label: str) -> bytes:
    raw = make_rgba_icon(size, label)
    compressed = zlib.compress(raw, level=9)

    png = bytearray()
    png.extend(b"\x89PNG\r\n\x1a\n")
    ihdr = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    png.extend(png_chunk(b"IHDR", ihdr))

    text_payload = (
        f"Title={ICO_TITLE}\nType={ICO_CAPTION}\nSize={label}\nDescription=Safe dummy icon file"
    ).encode("utf-8")
    png.extend(png_chunk(b"tEXt", text_payload))
    png.extend(png_chunk(b"IDAT", compressed))
    png.extend(png_chunk(b"IEND", b""))
    return bytes(png)


def build_ico(label: str) -> bytes:
    png_16 = build_png(16, label)
    png_32 = build_png(32, label)
    png_48 = build_png(48, label)
    png_64 = build_png(64, label)

    images = [
        (16, 16, png_16),
        (32, 32, png_32),
        (48, 48, png_48),
        (64, 64, png_64),
    ]

    header = struct.pack("<HHH", 0, 1, len(images))
    directory = bytearray()
    data = bytearray()

    offset = 6 + (16 * len(images))
    for w, h, img in images:
        width_byte = 0 if w >= 256 else w
        height_byte = 0 if h >= 256 else h
        directory.extend(
            struct.pack(
                "<BBBBHHII",
                width_byte,
                height_byte,
                0,
                0,
                1,
                32,
                len(img),
                offset,
            )
        )
        data.extend(img)
        offset += len(img)

    return header + directory + data


def pad_ico_to_size(ico_bytes: bytes, target_bytes: int) -> bytes:
    base_len = len(ico_bytes)
    if base_len > target_bytes:
        raise ValueError(
            f"Base ICO ({base_len} bytes) sudah lebih besar dari target ({target_bytes} bytes)."
        )
    if base_len == target_bytes:
        return ico_bytes
    filler = b"\x00" * (target_bytes - base_len)
    return ico_bytes + filler


def main():
    parser = argparse.ArgumentParser(description="Generate dummy ICO ukuran presisi.")
    parser.add_argument(
        "--sizes",
        type=str,
        default=None,
        help="Comma-separated ukuran, misal '10kb,1mb'. Default: varian ukuran umum ICO mulai 10KB sampai 2MB.",
    )
    parser.add_argument("--outdir", type=str, default=".", help="Folder output.")
    parser.add_argument(
        "--prefix", type=str, default="Contohnya-ICO", help="Prefix nama file output."
    )
    parser.add_argument(
        "--binary",
        action="store_true",
        help="Pakai definisi binary (1 KB = 1024 bytes) instead of decimal (default).",
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
        ico_base = build_ico(format_label(label))
        base_bytes = len(ico_base)
        if base_bytes > size:
            print(f"{label:>8} -> SKIP, base ICO ({base_bytes} bytes) > target ({size} bytes)")
            continue

        padded = pad_ico_to_size(ico_base, size)
        out_path = os.path.join(args.outdir, f"{args.prefix}-{format_label(label)}.ico")

        with open(out_path, "wb") as f:
            f.write(padded)

        actual = os.path.getsize(out_path)
        status = "OK" if actual == size else f"MELESET ({actual} bytes)"
        print(f"{label:>8} -> {out_path} [{actual} bytes] {status}")


if __name__ == "__main__":
    main()
