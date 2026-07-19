#!/usr/bin/env python3
"""
generate_dummy_tar.py

Generate dummy file TAR (.tar, uncompressed) buat testing upload/extract.
Isinya beneran ada data:
- README.txt (nyebutin contohnya.web.id + ukuran target)
- 1 atau lebih file data/dummy-N.bin (random bytes) - buat size gede,
  otomatis dipecah jadi multi item

CATATAN PENTING soal presisi ukuran:
TAR itu format berbasis block 512-byte, dan library tarfile Python SELALU
membulatkan ukuran akhir file ke kelipatan 10.240 bytes (20 block, standar
"tar record size" POSIX/GNU tar), berapa pun persis isi datanya. Ini
batasan format, bukan bug script. Jadi hasil akhirnya "sedekat mungkin ke
target, dibulatkan ke atas ke kelipatan 10.240 bytes terdekat" - BEDA dari
generate_dummy_zip.py yang bisa byte-exact 100% (ZIP gak punya batasan ini).

Gak butuh dependency eksternal, cuma Python standard library.

Cara pakai:
    python3 generate_dummy_tar.py                   # generate 10 varian ukuran default
    python3 generate_dummy_tar.py --sizes 10kb,5mb   # generate ukuran tertentu aja
    python3 generate_dummy_tar.py --outdir ./tar     # ganti folder output
    python3 generate_dummy_tar.py --chunk-cap 10mb   # ganti ukuran maks per item .bin
"""

import argparse
import io
import math
import os
import re
import tarfile

# ---- Teks di dalam README.txt, ubah sesuai kebutuhan lo ----
SITE_MENTION = "contohnya.web.id"
README_TEMPLATE = (
    "Dummy TAR Archive - {site}\n"
    "Ukuran target: {label}\n"
    "File ini dibuat untuk keperluan testing upload, extract, dan arsip.\n"
)
# ----------------------------------------------------------------

TAR_RECORD_SIZE = 10240  # tarfile selalu bulatin output ke kelipatan ini

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
    if total_bin_bytes <= 0:
        return []
    n = max(1, math.ceil(total_bin_bytes / chunk_cap))
    base = total_bin_bytes // n
    sizes = [base] * n
    sizes[-1] += total_bin_bytes - base * n
    return sizes


def build_tar(out_path: str, target_bytes: int, label: str, chunk_cap: int) -> tuple:
    """
    Bangun TAR berisi README.txt + N file data/dummy-*.bin (random bytes).
    Ukuran akhir dibulatkan otomatis oleh tarfile ke kelipatan 10.240 bytes
    terdekat di atas kebutuhan konten - gak bisa dihindari, batasan format.
    Return (actual_size, jumlah_item_total_termasuk_readme).
    """
    readme = README_TEMPLATE.format(site=SITE_MENTION, label=label).encode("utf-8")

    n_items = max(1, math.ceil(max(target_bytes - len(readme), 1) / chunk_cap))
    # kurangin dikit dari target buat kompensasi overhead header tar per-entry
    # (masing2 entry butuh 1 block/512 byte buat header + padding ke block)
    overhead_est = (n_items + 1) * 512 + 1024  # +1024 buat 2 block kosong penutup
    total_bin = max(0, target_bytes - len(readme) - overhead_est)
    sizes = compute_item_sizes(total_bin, chunk_cap)
    if len(sizes) < n_items:
        sizes += [0] * (n_items - len(sizes))

    with tarfile.open(out_path, "w") as tf:
        info = tarfile.TarInfo("README.txt")
        info.size = len(readme)
        tf.addfile(info, io.BytesIO(readme))
        for i, sz in enumerate(sizes, 1):
            data = os.urandom(max(sz, 0))
            info = tarfile.TarInfo(f"data/dummy-{i}.bin")
            info.size = len(data)
            tf.addfile(info, io.BytesIO(data))

    return os.path.getsize(out_path), len(sizes) + 1


def main():
    parser = argparse.ArgumentParser(description="Generate dummy TAR (uncompressed).")
    parser.add_argument(
        "--sizes",
        type=str,
        default=None,
        help="Comma-separated ukuran, misal '10kb,5mb'. Default: 10 varian standar (max 100MB).",
    )
    parser.add_argument("--outdir", type=str, default=".", help="Folder output.")
    parser.add_argument(
        "--prefix", type=str, default="Contohnya-TAR", help="Prefix nama file output."
    )
    parser.add_argument(
        "--chunk-cap",
        type=str,
        default="20mb",
        help="Ukuran maksimum per file .bin di dalam TAR sebelum dipecah jadi item baru. Default: 20mb.",
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
        out_path = os.path.join(args.outdir, f"{args.prefix}-{format_label(label)}.tar")
        actual, n_items = build_tar(out_path, size, format_label(label), chunk_cap)
        diff = actual - size
        note = "pas" if diff == 0 else f"+{diff} bytes (dibulatkan ke block tar terdekat)"
        print(f"{label:>8} -> {out_path}  [{actual} bytes, {n_items} item]  {note}")


if __name__ == "__main__":
    main()