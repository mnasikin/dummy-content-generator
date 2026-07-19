#!/usr/bin/env python3
"""
generate_dummy_docx.py

Generate dummy file Word (.docx) berukuran mendekati target, buat testing
upload/parsing dokumen. Isinya banyak paragraf teks dummy, dengan mention
contohnya.web.id secara berkala.

DOCX itu container ZIP terkompresi (mirip XLSX), jadi ukurannya gak linear
sempurna terhadap jumlah paragraf - gak bisa byte-exact kayak PDF/CSV/SQL.
Strateginya: estimasi jumlah paragraf dari bytes-per-paragraf hasil sample,
generate, ukur, koreksi kalau masih jauh.

Generate file DOCX-nya dilakukan lewat docx-js (npm), dipanggil dari script
Node kecil (build_docx.js) yang harus ada satu folder sama script ini.

Requirement: Node.js + package `docx` (npm install docx)

Cara pakai:
    python3 generate_dummy_docx.py                  # generate semua ukuran default
    python3 generate_dummy_docx.py --sizes 1kb,5mb   # generate ukuran tertentu aja
    python3 generate_dummy_docx.py --outdir ./docx   # ganti folder output
"""

import argparse
import os
import re
import subprocess
import sys

SITE_MENTION = "contohnya.web.id"
MENTION_EVERY_N = 5

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
NODE_SCRIPT = os.path.join(SCRIPT_DIR, "build_docx.js")

DEFAULT_SIZES = {
    "10kb": 10_000,
    "50kb": 50_000,
    "100kb": 100_000,
    "500kb": 500_000,
    "1mb": 1_000_000,
    "5mb": 5_000_000,
    "10mb": 10_000_000,
    "20mb": 20_000_000,
    "35mb": 35_000_000,
    "50mb": 50_000_000,
}

DEFAULT_SIZES_BINARY = {
    "10kb": 10 * 1024,
    "50kb": 50 * 1024,
    "100kb": 100 * 1024,
    "500kb": 500 * 1024,
    "1mb": 1024 * 1024,
    "5mb": 5 * 1024 * 1024,
    "10mb": 10 * 1024 * 1024,
    "20mb": 20 * 1024 * 1024,
    "35mb": 35 * 1024 * 1024,
    "50mb": 50 * 1024 * 1024,
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


def build_docx(out_path: str, num_paragraphs: int, label: str, text_length: int = 200) -> None:
    subprocess.run(
        [
            "node",
            "--max-old-space-size=2560",
            NODE_SCRIPT,
            out_path,
            str(max(num_paragraphs, 1)),
            label,
            SITE_MENTION,
            str(MENTION_EVERY_N),
            str(text_length),
        ],
        check=True,
        capture_output=True,
    )


def generate_docx(out_path: str, target_bytes: int, label: str) -> tuple:
    """
    Generate DOCX dengan CUMA 2-3 kali build total. Buat target gede, teks
    per paragraf dibikin lebih panjang (bukan nambah jumlah paragraf tanpa
    batas) - ini penting biar jumlah OBJECT JS (Paragraph/TextRun) yang
    dibangun docx-js gak meledak dan bikin proses Node OOM-killed buat
    target puluhan-ratusan MB.
    Return (actual_size, num_paragraphs).
    """
    # Cap jumlah paragraf di ~150rb, sisanya diakomodasi lewat teks lebih panjang
    max_reasonable_paragraphs = 150_000
    text_length = 200
    if target_bytes / 65 > max_reasonable_paragraphs:
        text_length = max(200, int(target_bytes / 65 / max_reasonable_paragraphs) * 200)

    sample_n = max(10, min(300, int(target_bytes / (65 * (text_length / 200)) / 20)))
    build_docx(out_path, sample_n, label, text_length)
    sample_size = os.path.getsize(out_path)
    bytes_per_para = sample_size / sample_n if sample_n else 65.0

    if sample_size >= target_bytes:
        return sample_size, sample_n

    est_n = max(sample_n, int(target_bytes / bytes_per_para))
    build_docx(out_path, est_n, label, text_length)
    final_size = os.path.getsize(out_path)

    error_ratio = abs(final_size - target_bytes) / target_bytes
    if error_ratio > 0.02 and final_size != sample_size:
        bytes_per_para_2 = (final_size - sample_size) / (est_n - sample_n) if est_n != sample_n else bytes_per_para
        est_n_2 = max(1, int(target_bytes / bytes_per_para_2))
        build_docx(out_path, est_n_2, label, text_length)
        final_size = os.path.getsize(out_path)
        est_n = est_n_2

    return final_size, est_n


def main():
    parser = argparse.ArgumentParser(description="Generate dummy DOCX ukuran mendekati target.")
    parser.add_argument(
        "--sizes",
        type=str,
        default=None,
        help="Comma-separated ukuran, misal '10kb,50kb,10mb'. Default: 10 varian standar.",
    )
    parser.add_argument("--outdir", type=str, default=".", help="Folder output.")
    parser.add_argument(
        "--prefix", type=str, default="Contohnya-DOCX", help="Prefix nama file output."
    )
    parser.add_argument(
        "--binary",
        action="store_true",
        help="Pakai definisi binary (1 MB = 1024x1024 bytes) instead of decimal (default).",
    )
    args = parser.parse_args()

    if not os.path.exists(NODE_SCRIPT):
        print(f"ERROR: {NODE_SCRIPT} gak ketemu. Pastiin build_docx.js ada di folder yang sama.")
        sys.exit(1)

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
        out_path = os.path.join(args.outdir, f"{args.prefix}-{format_label(label)}.docx")
        actual, n_para = generate_docx(out_path, size, format_label(label))
        over = actual - size
        print(f"{label:>8} -> {out_path}  [{actual} bytes, {n_para} paragraf, +{over} dari target]")


if __name__ == "__main__":
    main()
