#!/usr/bin/env python3
"""
generate_dummy_gz.py

Generate dummy file .gz buat testing upload/extract. Isi file .gz ini adalah
stream TAR yang dikompres gzip, jadi setelah di-gunzip hasilnya berupa archive
TAR yang berisi:
- README.txt
- 1 atau lebih file data/dummy-N.bin

Catatan penting:
- Extension output tetap .gz (bukan .tar.gz), sesuai permintaan.
- Secara isi, file ini adalah gzip-compressed tar stream supaya setelah diextract
  ada struktur README.txt + folder/files .bin.
- Aman, tanpa shell execution, network, atau payload berbahaya.

Cara pakai:
python3 generate_dummy_gz.py
python3 generate_dummy_gz.py --sizes 64kb,256kb,1mb,7mb
python3 generate_dummy_gz.py --count 6
python3 generate_dummy_gz.py --max-size 25mb
python3 generate_dummy_gz.py --outdir ./gz-files --prefix Contohnya-GZ
python3 generate_dummy_gz.py --chunk-cap 10mb
python3 generate_dummy_gz.py --binary
"""

import argparse
import io
import math
import os
import re
import tarfile
from typing import Dict, List, Tuple

SITE_MENTION = "contohnya.web.id"
README_TEMPLATE = (
    "Dummy GZ Archive - {site}\n"
    "Ukuran target: {label}\n"
    "File ini dibuat untuk testing upload, extract, dan validasi ukuran.\n"
    "Isi arsip: README.txt + file data/dummy-N.bin.\n"
)

DEFAULT_SIZES = [
    "32kb",
    "64kb",
    "128kb",
    "256kb",
    "512kb",
    "1mb",
    "2mb",
    "5mb",
    "10mb",
    "50mb",
]

MAX_DEFAULT_COUNT = 10
DEFAULT_MAX_SIZE_LABEL = "50mb"
DEFAULT_CHUNK_CAP = "20mb"


def parse_size(s: str, binary: bool = False) -> int:
    s = s.strip().lower()
    m = re.match(r"^([\d.]+)\s*(b|kb|mb|gb)?$", s)
    if not m:
        raise ValueError(f"Gak ngerti format ukuran: {s}")
    num, unit = m.groups()
    num = float(num)
    base = 1024 if binary else 1000
    mult = {None: 1, "b": 1, "kb": base, "mb": base**2, "gb": base**3}[unit]
    return int(num * mult)


def format_label(label: str) -> str:
    m = re.match(r"^([\d.]+)\s*(b|kb|mb|gb)$", label.strip().lower())
    if not m:
        return label.strip()
    num, unit = m.groups()
    return f"{num}{unit.upper()}"


def build_default_targets(binary: bool = False) -> Dict[str, int]:
    return {label: parse_size(label, binary=binary) for label in DEFAULT_SIZES}


def filtered_default_labels(max_size_label: str, count: int, binary: bool = False) -> List[str]:
    max_bytes = parse_size(max_size_label, binary=binary)
    labels = [label for label in DEFAULT_SIZES if parse_size(label, binary=binary) <= max_bytes]
    if not labels:
        raise ValueError("Tidak ada default size yang <= --max-size")
    return labels[:count]


def resolve_targets(args) -> List[Tuple[str, int]]:
    if args.sizes:
        labels = [x.strip() for x in args.sizes.split(",") if x.strip()]
        if len(labels) > MAX_DEFAULT_COUNT:
            raise ValueError(f"Maksimal {MAX_DEFAULT_COUNT} ukuran per generate.")
        return sorted(
            [(label.lower(), parse_size(label, binary=args.binary)) for label in labels],
            key=lambda kv: kv[1],
        )

    labels = filtered_default_labels(args.max_size, args.count, binary=args.binary)
    table = build_default_targets(binary=args.binary)
    return [(label, table[label]) for label in labels]


def compute_item_sizes(total_bin_bytes: int, chunk_cap: int) -> List[int]:
    if total_bin_bytes <= 0:
        return []
    n = max(1, math.ceil(total_bin_bytes / chunk_cap))
    base = total_bin_bytes // n
    sizes = [base] * n
    sizes[-1] += total_bin_bytes - base * n
    return sizes


def build_gz_tar_stream(out_path: str, target_bytes: int, label: str, chunk_cap: int, max_attempts: int = 5):
    readme = README_TEMPLATE.format(site=SITE_MENTION, label=label).encode("utf-8")
    n_items = max(1, math.ceil(max(target_bytes - len(readme), 1) / chunk_cap))
    guess_total_bin = max(0, target_bytes - len(readme) - 1024)

    actual = 0
    sizes: List[int] = []

    for _ in range(max_attempts):
        sizes = compute_item_sizes(guess_total_bin, chunk_cap)
        if len(sizes) < n_items:
            sizes += [0] * (n_items - len(sizes))

        with tarfile.open(out_path, mode="w:gz", compresslevel=6) as tf:
            info = tarfile.TarInfo("README.txt")
            info.size = len(readme)
            tf.addfile(info, io.BytesIO(readme))

            for i, sz in enumerate(sizes, 1):
                data = os.urandom(max(sz, 0))
                info = tarfile.TarInfo(f"data/dummy-{i}.bin")
                info.size = len(data)
                tf.addfile(info, io.BytesIO(data))

        actual = os.path.getsize(out_path)
        diff = target_bytes - actual
        if abs(diff) <= 128:
            break
        guess_total_bin = max(0, guess_total_bin + diff)

    return actual, len(sizes) + 1


def main():
    parser = argparse.ArgumentParser(description="Generate dummy .gz berisi tar stream dengan README.txt + data/dummy-N.bin.")
    parser.add_argument(
        "--sizes",
        type=str,
        default=None,
        help="Comma-separated ukuran custom, misal '64kb,1mb,7mb'. Maks 10 ukuran.",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=MAX_DEFAULT_COUNT,
        help="Jumlah varian default yang digenerate. Maks 10. Default 10.",
    )
    parser.add_argument(
        "--max-size",
        type=str,
        default=DEFAULT_MAX_SIZE_LABEL,
        help="Batas size terbesar untuk varian default. Default 50mb.",
    )
    parser.add_argument("--outdir", type=str, default=".", help="Folder output.")
    parser.add_argument("--prefix", type=str, default="Contohnya-GZ", help="Prefix nama file output.")
    parser.add_argument(
        "--chunk-cap",
        type=str,
        default=DEFAULT_CHUNK_CAP,
        help="Ukuran maksimum per file data/dummy-*.bin sebelum dipecah jadi item baru. Default 20mb.",
    )
    parser.add_argument(
        "--binary",
        action="store_true",
        help="Pakai definisi binary (1 MB = 1024x1024 bytes) instead of decimal.",
    )
    args = parser.parse_args()

    if args.count < 1:
        raise ValueError("--count minimal 1")
    if args.count > MAX_DEFAULT_COUNT:
        raise ValueError(f"--count maksimal {MAX_DEFAULT_COUNT}")

    os.makedirs(args.outdir, exist_ok=True)
    chunk_cap = parse_size(args.chunk_cap, binary=args.binary)
    targets = resolve_targets(args)

    for raw_label, size in targets:
        pretty = format_label(raw_label)
        out_path = os.path.join(args.outdir, f"{args.prefix}-{pretty}.gz")
        actual, n_items = build_gz_tar_stream(out_path, size, pretty, chunk_cap)
        diff = actual - size
        print(f"{raw_label:>8} -> {out_path} [{actual} bytes, {n_items} item, {diff:+d} dari target]")


if __name__ == "__main__":
    main()
