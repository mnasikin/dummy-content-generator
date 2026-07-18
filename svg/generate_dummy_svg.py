#!/usr/bin/env python3
"""
generate_dummy_svg.py

Generate dummy file SVG berukuran presisi (byte-exact) buat testing
upload/download/parsing gambar vector. Tiap file punya background abstrak
(shape acak dengan gradient), judul "Contohnya.web.id", teks ukuran file,
dan keterangan "Dummy SVG".

SVG itu format teks/XML murni (bukan container terkompresi kayak XLSX),
jadi bisa di-padding byte-exact kayak PDF - gak perlu estimasi.

Gak butuh dependency eksternal, cuma Python standard library.

Cara pakai:
    python3 generate_dummy_svg.py                  # generate 10 varian ukuran default
    python3 generate_dummy_svg.py --sizes 1kb,5mb   # generate ukuran tertentu aja
    python3 generate_dummy_svg.py --outdir ./svg    # ganti folder output
    python3 generate_dummy_svg.py --prefix Contohnya-SVG  # ganti prefix nama file
"""

import argparse
import os
import random
import re

# ---- Teks di dalam SVG, ubah sesuai kebutuhan lo ----
SVG_TITLE = "Contohnya.web.id"
SVG_CAPTION = "Dummy SVG"
# -------------------------------------------------------

WIDTH, HEIGHT = 800, 600

# Max 10MB sesuai request, 10 varian ukuran (decimal: 1KB = 1000 bytes)
DEFAULT_SIZES = {
    "1kb": 1_000,
    "5kb": 5_000,
    "10kb": 10_000,
    "50kb": 50_000,
    "100kb": 100_000,
    "500kb": 500_000,
    "1mb": 1_000_000,
    "2mb": 2_000_000,
    "5mb": 5_000_000,
    "10mb": 10_000_000,
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
    "10mb": 10 * 1024 * 1024,
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


def make_abstract_background(width: int, height: int, n_shapes: int = 14) -> str:
    """Bikin background abstrak: gradient + shape acak (circle/rect/path)."""
    c1, c2 = random.sample(COLORS, 2)
    parts = [
        '<defs>',
        '  <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">',
        f'    <stop offset="0%" stop-color="{c1}" stop-opacity="0.15"/>',
        f'    <stop offset="100%" stop-color="{c2}" stop-opacity="0.15"/>',
        '  </linearGradient>',
        '</defs>',
        f'<rect width="{width}" height="{height}" fill="#FFFDF8"/>',
        f'<rect width="{width}" height="{height}" fill="url(#bgGrad)"/>',
    ]
    for _ in range(n_shapes):
        shape_type = random.choice(["circle", "circle", "rect", "path"])
        color = random.choice(COLORS)
        opacity = round(random.uniform(0.08, 0.25), 2)
        if shape_type == "circle":
            cx, cy, r = random.randint(0, width), random.randint(0, height), random.randint(30, 180)
            parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}" opacity="{opacity}"/>')
        elif shape_type == "rect":
            x, y = random.randint(0, width), random.randint(0, height)
            w, h = random.randint(40, 220), random.randint(40, 220)
            rot = random.randint(0, 360)
            parts.append(
                f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{color}" '
                f'opacity="{opacity}" transform="rotate({rot} {x} {y})"/>'
            )
        else:
            pts = [(random.randint(0, width), random.randint(0, height)) for _ in range(3)]
            d = f"M{pts[0][0]} {pts[0][1]} L{pts[1][0]} {pts[1][1]} L{pts[2][0]} {pts[2][1]} Z"
            parts.append(f'<path d="{d}" fill="{color}" opacity="{opacity}"/>')
    return "\n  ".join(parts)


def build_svg(label: str) -> str:
    """Bangun SVG lengkap (background abstrak + teks) tanpa padding dulu."""
    bg = make_abstract_background(WIDTH, HEIGHT)
    svg = f'''<svg width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" xmlns="http://www.w3.org/2000/svg">
  {bg}
  <text x="60" y="{HEIGHT // 2 - 30}" font-family="Helvetica, Arial, sans-serif" font-size="36" font-weight="bold" fill="#1a1a1a">{SVG_TITLE}</text>
  <text x="60" y="{HEIGHT // 2 + 10}" font-family="Helvetica, Arial, sans-serif" font-size="20" fill="#333333">Ukuran: {label}</text>
  <text x="60" y="{HEIGHT // 2 + 40}" font-family="Helvetica, Arial, sans-serif" font-size="16" fill="#555555">{SVG_CAPTION}</text>
</svg>
'''
    return svg


def pad_svg_to_size(svg_str: str, target_bytes: int) -> str:
    """
    Tambahin padding presisi via XML comment sebelum </svg>, isinya string
    'x' berulang (SVG plain text, gak dikompres, jadi byte count-nya linear
    dan predictable - beda sama XLSX yang container ZIP).
    """
    base_bytes = len(svg_str.encode("utf-8"))
    if base_bytes > target_bytes:
        raise ValueError(
            f"Base SVG ({base_bytes} bytes) sudah lebih besar dari target ({target_bytes} bytes). "
            "Kurangi jumlah shape background atau naikkan target size."
        )
    # <!--  --> menambah overhead 7 bytes ("<!--" + " " + "-->" tanpa spasi persis
    # dihitung otomatis di bawah biar tetap presisi walau berubah.
    comment_wrapper_len = len("<!--\n") + len("\n-->\n")
    padding_len = target_bytes - base_bytes - comment_wrapper_len
    if padding_len < 0:
        padding_len = 0
    padding = "x" * padding_len
    comment = f"<!--\n{padding}\n-->\n"
    padded = svg_str.replace("</svg>", comment + "</svg>")

    # Koreksi kecil kalau meleset dikit (karena replace mengubah posisi, dsb)
    actual = len(padded.encode("utf-8"))
    diff = target_bytes - actual
    if diff != 0:
        padding_len = max(0, padding_len + diff)
        padding = "x" * padding_len
        comment = f"<!--\n{padding}\n-->\n"
        padded = svg_str.replace("</svg>", comment + "</svg>")
    return padded


def main():
    parser = argparse.ArgumentParser(description="Generate dummy SVG ukuran presisi.")
    parser.add_argument(
        "--sizes",
        type=str,
        default=None,
        help="Comma-separated ukuran, misal '1kb,5mb'. Default: 10 varian standar (max 10MB).",
    )
    parser.add_argument("--outdir", type=str, default=".", help="Folder output.")
    parser.add_argument(
        "--prefix", type=str, default="Contohnya-SVG", help="Prefix nama file output."
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
        svg_str = build_svg(format_label(label))
        base_bytes = len(svg_str.encode("utf-8"))
        if base_bytes > size:
            print(f"{label:>8} -> SKIP, base SVG ({base_bytes} bytes) > target ({size} bytes)")
            continue
        padded = pad_svg_to_size(svg_str, size)
        out_path = os.path.join(args.outdir, f"{args.prefix}-{format_label(label)}.svg")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(padded)
        actual = os.path.getsize(out_path)
        status = "OK" if actual == size else f"MELESET ({actual} bytes)"
        print(f"{label:>8} -> {out_path}  [{actual} bytes]  {status}")


if __name__ == "__main__":
    main()
