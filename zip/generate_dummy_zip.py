#!/usr/bin/env python3
"""
generate_dummy_zip.py

Generate dummy file ZIP berukuran presisi (byte-exact) buat testing
upload/extract/kompresi. Isinya beneran ada data:
- README.txt (nyebutin contohnya.web.id + ukuran target)
- 1 atau lebih file data/dummy-N.bin (random bytes) - buat size gede,
  otomatis dipecah jadi multi item (bukan 1 file .bin raksasa doang)

ZIP dibuat pakai ZIP_STORED (gak dikompres), jadi ukurannya predictable
dan bisa di-hit byte-exact lewat estimasi + koreksi iteratif (mirip
pendekatan padding di generate_dummy_pdf.py).

Gak butuh dependency eksternal, cuma Python standard library.

Cara pakai:
    python3 generate_dummy_zip.py                  # generate 10 varian ukuran default
    python3 generate_dummy_zip.py --sizes 10kb,5mb  # generate ukuran tertentu aja
    python3 generate_dummy_zip.py --outdir ./zip    # ganti folder output
    python3 generate_dummy_zip.py --chunk-cap 10mb  # ganti ukuran maks per item .bin
"""

import argparse
import math
import os
import re
import zipfile

# ---- Teks di dalam README.txt, ubah sesuai kebutuhan lo ----
SITE_MENTION = "contohnya.web.id"
README_TEMPLATE = (
    "Dummy ZIP Archive - {site}\n"
    "Ukuran target: {label}\n"
    "File ini dibuat untuk keperluan testing upload, extract, dan kompresi.\n"
)
# ----------------------------------------------------------------

# 10 varian, gak harus mulai dari 1KB, max 100MB (decimal: 1 KB = 1000 bytes)
DEFAULT_SIZES = {
    "10kb": 10_000,
    "50kb": 50_000,
    "100kb": 100_000,
    "500kb": 500_000,
    "1mb": 1_000_000,
    "5mb": 5_000_000,
    "10mb": 10_000_000,
    "25mb": 25_000_000,
    "50mb": 50_000_000,
    "100mb": 100_000_000,
}

DEFAULT_SIZES_BINARY = {
    "10kb": 10 * 1024,
    "50kb": 50 * 1024,
    "100kb": 100 * 1024,
    "500kb": 500 * 1024,
    "1mb": 1024 * 1024,
    "5mb": 5 * 1024 * 1024,
    "10mb": 10 * 1024 * 1024,
    "25mb": 25 * 1024 * 1024,
    "50mb": 50 * 1024 * 1024,
    "100mb": 100 * 1024 * 1024,
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


def compute_item_sizes(total_bin_bytes: int, chunk_cap: int) -> list:
    """Pecah total_bin_bytes jadi beberapa item, masing-masing maks chunk_cap."""
    if total_bin_bytes <= 0:
        return []
    n = max(1, math.ceil(total_bin_bytes / chunk_cap))
    base = total_bin_bytes // n
    sizes = [base] * n
    sizes[-1] += total_bin_bytes - base * n  # sisa masuk ke item terakhir
    return sizes


def build_zip(out_path: str, target_bytes: int, label: str, chunk_cap: int, max_attempts: int = 8):
    """
    Bangun ZIP berisi README.txt + N file data/dummy-*.bin (random bytes),
    dikoreksi iteratif sampai ukuran file persis target_bytes.
    Return (actual_size, jumlah_item_total_termasuk_readme).
    """
    readme = README_TEMPLATE.format(site=SITE_MENTION, label=label).encode("utf-8")

    n_items = max(1, math.ceil(max(target_bytes - len(readme), 1) / chunk_cap))
    guess_total_bin = max(0, target_bytes - len(readme) - 200)  # 200 = tebakan awal overhead

    actual = None
    sizes = []
    for _ in range(max_attempts):
        sizes = compute_item_sizes(guess_total_bin, chunk_cap)
        if len(sizes) < n_items:
            sizes += [0] * (n_items - len(sizes))

        with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_STORED) as zf:
            zf.writestr("README.txt", readme)
            for i, sz in enumerate(sizes, 1):
                zf.writestr(f"data/dummy-{i}.bin", os.urandom(max(sz, 0)))

        actual = os.path.getsize(out_path)
        diff = target_bytes - actual
        if diff == 0:
            break
        guess_total_bin = max(0, guess_total_bin + diff)

    return actual, len(sizes) + 1  # +1 buat README.txt


def main():
    parser = argparse.ArgumentParser(description="Generate dummy ZIP ukuran presisi.")
    parser.add_argument(
        "--sizes",
        type=str,
        default=None,
        help="Comma-separated ukuran, misal '10kb,5mb'. Default: 10 varian standar (max 100MB).",
    )
    parser.add_argument("--outdir", type=str, default=".", help="Folder output.")
    parser.add_argument(
        "--prefix", type=str, default="Contohnya-ZIP", help="Prefix nama file output."
    )
    parser.add_argument(
        "--chunk-cap",
        type=str,
        default="20mb",
        help="Ukuran maksimum per file .bin di dalam ZIP sebelum dipecah jadi item baru. Default: 20mb.",
    )
    parser.add_argument(
        "--binary",
        action="store_true",
        help="Pakai definisi binary (1 MB = 1024x1024 bytes) instead of decimal (default).",
    )
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    default_table = DEFAULT_SIZES_BINARY if args.binary else DEFAULT_SIZES
    chunk_cap = parse_size(args.chunk_cap, binary=args.binary)

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
        out_path = os.path.join(args.outdir, f"{args.prefix}-{format_label(label)}.zip")
        actual, n_items = build_zip(out_path, size, format_label(label), chunk_cap)
        status = "OK" if actual == size else f"MELESET ({actual} bytes)"
        print(f"{label:>8} -> {out_path}  [{actual} bytes, {n_items} item]  {status}")


if __name__ == "__main__":
    main()
