#!/usr/bin/env python3
"""
generate_dummy_xls.py

Generate dummy file Excel LAMA (.xls, format binary Excel 97-2003)
berukuran mendekati target, buat testing upload/parsing spreadsheet legacy.

.xls itu format binary (BIFF/OLE Compound File), BEDA TOTAL dari .xlsx
(yang XML+ZIP) - gak bisa di-hand-craft/padding manual. Strateginya:
generate .xlsx dulu (pakai openpyxl, mesin yang sama kayak
generate_dummy_xlsx.py), terus CONVERT ke .xls pakai LibreOffice headless
(`soffice --convert-to xls`).

KETERBATASAN PENTING:
- Ukuran akhir .xls BISA JAUH LEBIH GEDE dari .xlsx sumbernya (rasio ~2-3x
  dari observasi, tapi GAK konsisten antar ukuran), karena format binary
  lama gak punya kompresi kayak ZIP. Jadi ini approximate, bukan presisi -
  script ini ukur rasio spesifik per target dan koreksi sekali.
- Proses convert lewat LibreOffice itu lumayan lambat, apalagi buat file
  gede. Sabar aja pas nunggu, dan timeout udah dinaikin ke 600 detik biar
  aman buat file besar.

Requirement:
- Python package `openpyxl` (pip install openpyxl --break-system-packages)
- LibreOffice (`soffice` harus ada di PATH)

Cara pakai:
    python3 generate_dummy_xls.py                  # generate semua ukuran default
    python3 generate_dummy_xls.py --sizes 1kb,5mb   # generate ukuran tertentu aja
    python3 generate_dummy_xls.py --outdir ./xls    # ganti folder output
"""

import argparse
import os
import random
import re
import shutil
import string
import subprocess
import sys
import tempfile

import openpyxl

SITE_MENTION = "contohnya.web.id"
MENTION_EVERY_N_ROWS = 5
HEADER_ROW = ["No", "Keterangan", "Sumber"]

# .xls (binary lama) sama kayak .doc - dicap lebih realistis, gak sampe 100MB
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


def random_text(length: int = 40) -> str:
    return "".join(random.choices(string.ascii_letters + " ", k=length))


def _add_rows(ws, start_row: int, count: int) -> int:
    for i in range(count):
        row_num = start_row + i
        text = random_text()
        sumber = SITE_MENTION if row_num % MENTION_EVERY_N_ROWS == 0 else "-"
        ws.append([row_num, f"Dummy data testing - {text}", sumber])
    return start_row + count - 1


def generate_xlsx(out_path: str, target_bytes: int, max_attempts: int = 10) -> int:
    """Sama logic kayak generate_dummy_xlsx.py: lompatan besar + koreksi coarse."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Data"
    ws.append(HEADER_ROW)
    wb.save(out_path)
    size = os.path.getsize(out_path)
    row_num = 0
    bytes_per_row = 55.0

    target_90 = int(target_bytes * 0.90)
    if size < target_90:
        est_rows = max(1, int((target_90 - size) / bytes_per_row))
        row_num = _add_rows(ws, row_num + 1, est_rows)
        wb.save(out_path)
        new_size = os.path.getsize(out_path)
        bytes_per_row = (new_size - size) / est_rows if est_rows else bytes_per_row
        size = new_size

    attempts = 0
    while size < target_bytes and attempts < max_attempts:
        remaining = target_bytes - size
        add_n = max(1, int(remaining / bytes_per_row))
        prev_size = size
        row_num = _add_rows(ws, row_num + 1, add_n)
        wb.save(out_path)
        size = os.path.getsize(out_path)
        added = size - prev_size
        if add_n and added > 0:
            bytes_per_row = added / add_n
        attempts += 1

    return size


def convert_to_xls(xlsx_path: str, out_dir: str, timeout_sec: int = 600) -> str:
    result = subprocess.run(
        ["soffice", "--headless", "--convert-to", "xls", "--outdir", out_dir, xlsx_path],
        check=True,
        capture_output=True,
        text=True,
        timeout=timeout_sec,
    )
    base = os.path.splitext(os.path.basename(xlsx_path))[0]
    xls_path = os.path.join(out_dir, f"{base}.xls")
    if not os.path.exists(xls_path):
        raise RuntimeError(f"Convert gagal, output gak ketemu. LibreOffice log: {result.stdout}")
    return xls_path


def main():
    parser = argparse.ArgumentParser(description="Generate dummy XLS (legacy binary Excel).")
    parser.add_argument(
        "--sizes",
        type=str,
        default=None,
        help="Comma-separated ukuran, misal '10kb,50kb,10mb'. Default: 10 varian standar (max 50MB).",
    )
    parser.add_argument("--outdir", type=str, default=".", help="Folder output.")
    parser.add_argument(
        "--prefix", type=str, default="Contohnya-XLS-Legacy", help="Prefix nama file output."
    )
    parser.add_argument(
        "--binary",
        action="store_true",
        help="Pakai definisi binary (1 MB = 1024x1024 bytes) instead of decimal (default).",
    )
    args = parser.parse_args()

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
            tmp_xlsx = os.path.join(tmpdir, f"tmp-{label}.xlsx")

            # Rasio konversi xlsx->xls gak konsisten antar ukuran, jadi:
            # 1) build xlsx dengan estimasi awal (target/2.5)
            # 2) convert, ukur rasio ACTUAL
            # 3) 1x koreksi pakai rasio yang baru diukur spesifik buat ukuran ini
            xlsx_target_1 = max(2000, int(size / 2.5))
            xlsx_size_1 = generate_xlsx(tmp_xlsx, xlsx_target_1)
            xls_path = convert_to_xls(tmp_xlsx, tmpdir)
            xls_size_1 = os.path.getsize(xls_path)

            ratio = xls_size_1 / xlsx_size_1 if xlsx_size_1 else 2.5
            error_ratio = abs(xls_size_1 - size) / size

            if error_ratio > 0.10:
                xlsx_target_2 = max(2000, int(size / ratio))
                generate_xlsx(tmp_xlsx, xlsx_target_2)
                xls_path = convert_to_xls(tmp_xlsx, tmpdir)
                xls_size_1 = os.path.getsize(xls_path)

            final_name = f"{args.prefix}-{fmt_label}.xls"
            final_path = os.path.join(args.outdir, final_name)
            shutil.move(xls_path, final_path)

            xls_actual = os.path.getsize(final_path)
            over = xls_actual - size
            print(f"{label:>8} -> {final_path}  [{xls_actual} bytes, {over:+d} dari target]")


if __name__ == "__main__":
    main()
