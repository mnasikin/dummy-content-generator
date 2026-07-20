#!/usr/bin/env python3
"""
generate_dummy_md.py

Generate dummy file Markdown (.md) yang aman dan statis untuk testing
upload, preview, parsing, dan validasi ukuran file.

Output:
- file .md valid
- isi berupa Markdown biasa
- tidak ada shell execution
- tidak ada network access
- tidak ada dynamic code execution
- maksimal generate 10 file
- default ukuran maksimum 10MB

Cara pakai:
python3 generate_dummy_md.py
python3 generate_dummy_md.py --sizes 10kb,25kb,100kb,1mb,10mb
python3 generate_dummy_md.py --outdir ./md
python3 generate_dummy_md.py --prefix Contohnya-MD
"""

import argparse
import os
import re


TITLE = "Contohnya.web.id"
SUBTITLE = "Dummy Markdown File"
MAX_FILES = 10

DEFAULT_SIZES = {
    "10kb": 10_000,
    "25kb": 25_000,
    "50kb": 50_000,
    "100kb": 100_000,
    "250kb": 250_000,
    "500kb": 500_000,
    "1mb": 1_000_000,
    "2mb": 2_000_000,
    "5mb": 5_000_000,
    "10mb": 10_000_000,
}

DEFAULT_SIZES_BINARY = {
    "10kb": 10 * 1024,
    "25kb": 25 * 1024,
    "50kb": 50 * 1024,
    "100kb": 100 * 1024,
    "250kb": 250 * 1024,
    "500kb": 500 * 1024,
    "1mb": 1024 * 1024,
    "2mb": 2 * 1024 * 1024,
    "5mb": 5 * 1024 * 1024,
    "10mb": 10 * 1024 * 1024,
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


def build_base_markdown(label: str) -> str:
    return (
        f"# {TITLE}\n\n"
        f"**{SUBTITLE}**\n\n"
        f"- Format: Markdown\n"
        f"- Label size: {format_label(label)}\n"
        f"- Safety: static content only\n"
        f"- Purpose: upload and preview testing\n\n"
        f"## Ringkasan\n\n"
        f"File ini dibuat untuk kebutuhan dummy testing. "
        f"Konten di dalamnya berupa teks Markdown biasa yang aman dibuka di editor teks atau markdown viewer.\n\n"
        f"## Contoh Konten\n\n"
        f"### Poin\n\n"
        f"- Baris aman 1\n"
        f"- Baris aman 2\n"
        f"- Baris aman 3\n\n"
        f"### Tabel\n\n"
        f"| Kolom | Nilai |\n"
        f"|---|---|\n"
        f"| Nama | {TITLE} |\n"
        f"| Tipe | Markdown |\n"
        f"| Ukuran Label | {format_label(label)} |\n\n"
        f"### Kutipan\n\n"
        f"> Ini adalah file Markdown dummy yang aman dan statis.\n\n"
        f"---\n\n"
    )


def pad_markdown_to_size(base_text: str, target_bytes: int) -> bytes:
    data = base_text.encode("utf-8")
    if len(data) > target_bytes:
        raise ValueError(
            f"Base Markdown ({len(data)} bytes) sudah lebih besar dari target ({target_bytes} bytes)."
        )

    filler_line = (
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, "
        "sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.\n"
    ).encode("utf-8")

    chunks = [data]
    current = len(data)

    while current + len(filler_line) <= target_bytes:
        chunks.append(filler_line)
        current += len(filler_line)

    remaining = target_bytes - current
    if remaining > 0:
        partial = ("x" * remaining).encode("utf-8")
        chunks.append(partial)

    result = b"".join(chunks)
    return result[:target_bytes]


def main():
    parser = argparse.ArgumentParser(description="Generate dummy Markdown ukuran presisi.")
    parser.add_argument(
        "--sizes",
        type=str,
        default=None,
        help="Comma-separated ukuran, misal '10kb,25kb,100kb,1mb,10mb'. Default: varian ukuran umum sampai 10MB.",
    )
    parser.add_argument("--outdir", type=str, default=".", help="Folder output.")
    parser.add_argument(
        "--prefix", type=str, default="Contohnya-MD", help="Prefix nama file output."
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
        labels = [s.strip() for s in args.sizes.split(",") if s.strip()]
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
        base_text = build_base_markdown(label)
        payload = pad_markdown_to_size(base_text, size)

        out_path = os.path.join(args.outdir, f"{args.prefix}-{format_label(label)}.md")
        with open(out_path, "wb") as f:
            f.write(payload)

        actual = os.path.getsize(out_path)
        status = "OK" if actual == size else f"MELESET ({actual} bytes)"
        print(f"{label:>8} -> {out_path} [{actual} bytes] {status}")


if __name__ == "__main__":
    main()
