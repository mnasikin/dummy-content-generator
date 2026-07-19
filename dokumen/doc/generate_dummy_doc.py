#!/usr/bin/env python3
"""
generate_dummy_doc.py

Generate dummy file Word LAMA (.doc, format binary Word 97-2003) berukuran
mendekati target, buat testing upload/parsing dokumen legacy.

.doc itu format binary (OLE Compound File), BEDA TOTAL dari .docx (yang
XML+ZIP) - gak bisa di-hand-craft/padding manual kayak PDF/CSV/DOCX.
Strateginya: generate .docx dulu (pakai mesin yang sama kayak
generate_dummy_docx.py), terus CONVERT ke .doc pakai LibreOffice headless
(`soffice --convert-to doc`).

KETERBATASAN PENTING:
- Ukuran akhir .doc BISA BEDA dari .docx sumbernya (kadang lebih kecil,
  kadang lebih besar), karena format binary punya karakteristik encoding
  beda dari ZIP+XML. Jadi ini approximate, bukan presisi.
- Proses convert lewat LibreOffice itu lumayan lambat (bukan operasi
  instant kayak nulis file biasa), apalagi kalau dipanggil berkali-kali
  buat banyak ukuran. Sabar aja pas nunggu.

Requirement:
- Node.js + package `docx` (npm install docx) - buat generate .docx dulu
- LibreOffice (`soffice` harus ada di PATH) - buat convert ke .doc

Cara pakai:
    python3 generate_dummy_doc.py                  # generate semua ukuran default
    python3 generate_dummy_doc.py --sizes 1kb,5mb   # generate ukuran tertentu aja
    python3 generate_dummy_doc.py --outdir ./doc    # ganti folder output
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

SITE_MENTION = "contohnya.web.id"
MENTION_EVERY_N = 5

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
NODE_SCRIPT = os.path.join(SCRIPT_DIR, "build_docx.js")

# .doc (binary lama) gak umum dipake buat file gede - dicap lebih rendah
# dari .docx (yang dicap 50MB). LibreOffice convert juga lebih lambat buat
# file gede, jadi mending realistis di ukuran yang wajar buat format lama.
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


def generate_docx_approx(tmp_docx_path: str, target_bytes: int, label: str) -> int:
    """Sama logic kayak generate_dummy_docx.py: estimasi + 1x koreksi."""
    max_reasonable_paragraphs = 150_000
    text_length = 200
    if target_bytes / 65 > max_reasonable_paragraphs:
        text_length = max(200, int(target_bytes / 65 / max_reasonable_paragraphs) * 200)

    sample_n = max(10, min(300, int(target_bytes / (65 * (text_length / 200)) / 20)))
    build_docx(tmp_docx_path, sample_n, label, text_length)
    sample_size = os.path.getsize(tmp_docx_path)
    bytes_per_para = sample_size / sample_n if sample_n else 65.0

    if sample_size >= target_bytes:
        return sample_size

    est_n = max(sample_n, int(target_bytes / bytes_per_para))
    build_docx(tmp_docx_path, est_n, label, text_length)
    final_size = os.path.getsize(tmp_docx_path)

    error_ratio = abs(final_size - target_bytes) / target_bytes
    if error_ratio > 0.05 and final_size != sample_size:
        bytes_per_para_2 = (
            (final_size - sample_size) / (est_n - sample_n) if est_n != sample_n else bytes_per_para
        )
        est_n_2 = max(1, int(target_bytes / bytes_per_para_2))
        build_docx(tmp_docx_path, est_n_2, label, text_length)
        final_size = os.path.getsize(tmp_docx_path)

    return final_size


def convert_to_doc(docx_path: str, out_dir: str, timeout_sec: int = 600) -> str:
    """Convert .docx ke .doc pakai LibreOffice headless. Return path .doc hasil."""
    result = subprocess.run(
        [
            "soffice",
            "--headless",
            "--convert-to",
            "doc",
            "--outdir",
            out_dir,
            docx_path,
        ],
        check=True,
        capture_output=True,
        text=True,
        timeout=timeout_sec,
    )
    base = os.path.splitext(os.path.basename(docx_path))[0]
    doc_path = os.path.join(out_dir, f"{base}.doc")
    if not os.path.exists(doc_path):
        raise RuntimeError(f"Convert gagal, output gak ketemu. LibreOffice log: {result.stdout}")
    return doc_path


def main():
    parser = argparse.ArgumentParser(description="Generate dummy DOC (legacy binary Word).")
    parser.add_argument(
        "--sizes",
        type=str,
        default=None,
        help="Comma-separated ukuran, misal '10kb,50kb,10mb'. Default: 10 varian standar (max 50MB).",
    )
    parser.add_argument("--outdir", type=str, default=".", help="Folder output.")
    parser.add_argument(
        "--prefix", type=str, default="Contohnya-DOC", help="Prefix nama file output."
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
    if shutil.which("soffice") is None:
        print("ERROR: 'soffice' (LibreOffice) gak ketemu di PATH. Install LibreOffice dulu.")
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

    with tempfile.TemporaryDirectory() as tmpdir:
        for label, size in sorted(targets.items(), key=lambda kv: kv[1]):
            fmt_label = format_label(label)
            tmp_docx = os.path.join(tmpdir, f"tmp-{label}.docx")

            # Rasio konversi docx->doc itu GAK konsisten antar ukuran (kadang
            # 1.6x, kadang 3.3x), jadi gak bisa dihitung pakai rasio tetap.
            # Strategi: build docx dengan estimasi awal (target/2), convert,
            # ukur rasio ACTUAL dari hasil itu, lalu 1x koreksi pakai rasio
            # yang baru diukur spesifik buat ukuran ini.
            docx_target_1 = max(1000, int(size / 2))
            docx_size_1 = generate_docx_approx(tmp_docx, docx_target_1, fmt_label)
            doc_path = convert_to_doc(tmp_docx, tmpdir)
            doc_size_1 = os.path.getsize(doc_path)

            ratio = doc_size_1 / docx_size_1 if docx_size_1 else 2.0
            error_ratio = abs(doc_size_1 - size) / size

            if error_ratio > 0.10:
                docx_target_2 = max(1000, int(size / ratio))
                generate_docx_approx(tmp_docx, docx_target_2, fmt_label)
                doc_path = convert_to_doc(tmp_docx, tmpdir)
                doc_size_1 = os.path.getsize(doc_path)

            final_name = f"{args.prefix}-{fmt_label}.doc"
            final_path = os.path.join(args.outdir, final_name)
            shutil.move(doc_path, final_path)

            doc_actual = os.path.getsize(final_path)
            over = doc_actual - size
            print(f"{label:>8} -> {final_path}  [{doc_actual} bytes, {over:+d} dari target]")


if __name__ == "__main__":
    main()
