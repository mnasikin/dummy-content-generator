#!/usr/bin/env python3
"""
generate_dummy_tiff.py


Generate dummy file TIFF berukuran presisi (byte-exact-ish target with filler)
buat testing upload/download/parsing file. Tiap file berisi image .tiff valid
dengan visual sederhana bertema "Contohnya.web.id" dan label "Dummy File TIFF".


Output .tiff aman:
- bukan file executable
- tidak mengandung script
- hanya image TIFF statis
- cocok untuk testing upload, preview, MIME, dan validasi ukuran file


Catatan:
- TIFF dasar dibuat manual tanpa dependency eksternal.
- Agar ukuran file pas target, data di akhir file dipad dengan trailing bytes.
  Banyak parser/previewer tetap membaca image pertama dengan normal karena
  struktur TIFF valid ada di awal file.
- Jika target terlalu kecil untuk menampung TIFF minimum, file akan di-skip.


Cara pakai:
python3 generate_dummy_tiff.py
python3 generate_dummy_tiff.py --sizes 25kb,1mb
python3 generate_dummy_tiff.py --outdir ./tiff
python3 generate_dummy_tiff.py --prefix Contohnya-TIFF
"""


import argparse
import os
import re
import struct
import zlib


TIFF_TITLE = "Contohnya.web.id"
TIFF_CAPTION = "Dummy File TIFF"


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



def crc32_bytes(data: bytes) -> int:
    return zlib.crc32(data) & 0xFFFFFFFF



def pack_ifd_entry(tag, typ, count, value):
    return struct.pack("<HHII", tag, typ, count, value)



def make_pixel_data(width: int, height: int, label: str) -> bytes:
    seed = crc32_bytes(label.encode("utf-8"))
    pixels = bytearray()

    bg_top = (35, 23, 60)
    bg_bottom = (93, 56, 120)
    accent = (255, 180, 80)
    white = (245, 245, 250)
    border = (170, 120, 220)

    cx, cy = width // 2, height // 2
    rad = int(min(width, height) * 0.22)
    pad = max(2, width // 16)

    for y in range(height):
        t = y / max(1, height - 1)
        r = int(bg_top[0] * (1 - t) + bg_bottom[0] * t)
        g = int(bg_top[1] * (1 - t) + bg_bottom[1] * t)
        b = int(bg_top[2] * (1 - t) + bg_bottom[2] * t)

        row = bytearray()
        for x in range(width):
            rr, gg, bb = r, g, b

            if x < pad or y < pad or x >= width - pad or y >= height - pad:
                rr, gg, bb = border

            dx, dy = x - cx, y - cy
            if dx * dx + dy * dy <= rad * rad:
                rr, gg, bb = accent

            if abs(x - cx) < max(1, width // 24) and abs(y - cy) < height // 5:
                rr, gg, bb = white
            if abs(y - cy) < max(1, height // 24) and abs(x - cx) < width // 5:
                rr, gg, bb = white

            wobble = ((x * 17 + y * 31 + seed) % 7) - 3
            rr = max(0, min(255, rr + wobble))
            gg = max(0, min(255, gg + wobble))
            bb = max(0, min(255, bb + wobble))

            row.extend((rr, gg, bb))
        pixels.extend(row)

    return bytes(pixels)



def build_tiff(label: str) -> bytes:
    width = 64
    height = 64
    bits_per_sample = (8, 8, 8)
    samples_per_pixel = 3
    rows_per_strip = height
    compression = 1
    photometric = 2
    planar_config = 1
    resolution_num = 72
    resolution_den = 1

    software_text = b"Contohnya.web.id Dummy File TIFF\x00"
    image_desc_text = (
        f"Title={TIFF_TITLE}\nType={TIFF_CAPTION}\nSize={label}\nDescription=Safe dummy TIFF image"
    ).encode("utf-8") + b"\x00"

    pixel_data = make_pixel_data(width, height, label)
    strip_byte_count = len(pixel_data)

    tag_count = 15
    header_size = 8
    ifd_offset = header_size
    ifd_size = 2 + (tag_count * 12) + 4
    extra_offset = ifd_offset + ifd_size

    bits_offset = extra_offset
    bits_data = struct.pack("<HHH", *bits_per_sample)
    extra_offset += len(bits_data)

    xres_offset = extra_offset
    xres_data = struct.pack("<II", resolution_num, resolution_den)
    extra_offset += len(xres_data)

    yres_offset = extra_offset
    yres_data = struct.pack("<II", resolution_num, resolution_den)
    extra_offset += len(yres_data)

    software_offset = extra_offset
    extra_offset += len(software_text)

    image_desc_offset = extra_offset
    extra_offset += len(image_desc_text)

    pixel_offset = extra_offset

    entries = [
        (256, 4, 1, width),
        (257, 4, 1, height),
        (258, 3, 3, bits_offset),
        (259, 3, 1, compression),
        (262, 3, 1, photometric),
        (270, 2, len(image_desc_text), image_desc_offset),
        (273, 4, 1, pixel_offset),
        (277, 3, 1, samples_per_pixel),
        (278, 4, 1, rows_per_strip),
        (279, 4, 1, strip_byte_count),
        (282, 5, 1, xres_offset),
        (283, 5, 1, yres_offset),
        (284, 3, 1, planar_config),
        (296, 3, 1, 2),
        (305, 2, len(software_text), software_offset),
    ]

    out = bytearray()
    out.extend(b"II")
    out.extend(struct.pack("<H", 42))
    out.extend(struct.pack("<I", ifd_offset))
    out.extend(struct.pack("<H", tag_count))

    for tag, typ, count, value in entries:
        out.extend(pack_ifd_entry(tag, typ, count, value))

    out.extend(struct.pack("<I", 0))
    out.extend(bits_data)
    out.extend(xres_data)
    out.extend(yres_data)
    out.extend(software_text)
    out.extend(image_desc_text)
    out.extend(pixel_data)
    return bytes(out)



def pad_tiff_to_size(tiff_bytes: bytes, target_bytes: int) -> bytes:
    base_len = len(tiff_bytes)
    if base_len > target_bytes:
        raise ValueError(
            f"Base TIFF ({base_len} bytes) sudah lebih besar dari target ({target_bytes} bytes)."
        )
    if base_len == target_bytes:
        return tiff_bytes
    filler = b"\x00" * (target_bytes - base_len)
    return tiff_bytes + filler



def main():
    parser = argparse.ArgumentParser(description="Generate dummy TIFF ukuran presisi.")
    parser.add_argument(
        "--sizes",
        type=str,
        default=None,
        help="Comma-separated ukuran, misal '10kb,1mb'. Default: varian ukuran umum TIFF mulai 10KB sampai 2MB.",
    )
    parser.add_argument("--outdir", type=str, default=".", help="Folder output.")
    parser.add_argument(
        "--prefix", type=str, default="Contohnya-TIFF", help="Prefix nama file output."
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
        tiff_base = build_tiff(format_label(label))
        base_bytes = len(tiff_base)
        if base_bytes > size:
            print(f"{label:>8} -> SKIP, base TIFF ({base_bytes} bytes) > target ({size} bytes)")
            continue

        padded = pad_tiff_to_size(tiff_base, size)
        out_path = os.path.join(args.outdir, f"{args.prefix}-{format_label(label)}.tiff")

        with open(out_path, "wb") as f:
            f.write(padded)

        actual = os.path.getsize(out_path)
        status = "OK" if actual == size else f"MELESET ({actual} bytes)"
        print(f"{label:>8} -> {out_path} [{actual} bytes] {status}")



if __name__ == "__main__":
    main()
