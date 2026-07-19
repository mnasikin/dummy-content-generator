#!/usr/bin/env python3
"""
generate_dummy_xlsx.py

Generate dummy file Excel (.xlsx) berukuran presisi (byte-exact) buat testing
upload/download/parsing. Tiap baris berisi teks bebas (dummy), dan secara
berkala nyebutin "contohnya.web.id" di salah satu kolom.

Install dependency dulu (sekali aja):
    pip install openpyxl --break-system-packages

Cara pakai:
    python3 generate_dummy_xlsx.py                  # generate semua ukuran default
    python3 generate_dummy_xlsx.py --sizes 1kb,5mb   # generate ukuran tertentu aja
    python3 generate_dummy_xlsx.py --outdir ./xlsx   # ganti folder output
    python3 generate_dummy_xlsx.py --prefix Contohnya-XLS  # ganti prefix nama file
"""

import argparse
import os
import random
import re
import string

import openpyxl

# ---- Teks di dalam file, ubah sesuai kebutuhan lo ----
SITE_MENTION = "contohnya.web.id"
MENTION_EVERY_N_ROWS = 5  # kolom "Sumber" nyebutin site tiap N baris
HEADER_ROW = ["No", "Keterangan", "Sumber"]
# --------------------------------------------------------

# Pakai definisi DECIMAL (1 KB = 1000 bytes, 1 MB = 1_000_000 bytes) biar
# match sama gimana dashboard/file manager nampilin ukuran.
# Kalau butuh definisi binary (1024-based), pass --binary.
DEFAULT_SIZES = {
    "1kb": 1_000,
    "50kb": 50_000,
    "100kb": 100_000,
    "500kb": 500_000,
    "1mb": 1_000_000,
    "5mb": 5_000_000,
    "10mb": 10_000_000,
    "50mb": 50_000_000,
    "100mb": 100_000_000,
}

DEFAULT_SIZES_BINARY = {
    "1kb": 1024,
    "50kb": 50 * 1024,
    "100kb": 100 * 1024,
    "500kb": 500 * 1024,
    "1mb": 1024 * 1024,
    "5mb": 5 * 1024 * 1024,
    "10mb": 10 * 1024 * 1024,
    "50mb": 50 * 1024 * 1024,
    "100mb": 100 * 1024 * 1024,
}


def parse_size(s: str, binary: bool = False) -> int:
    """Parse '1kb', '500KB', '10mb', atau raw byte number jadi integer bytes."""
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
    """'1kb' -> '1KB', '500kb' -> '500KB', '10mb' -> '10MB', dst."""
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


def generate_xlsx(out_path: str, target_bytes: int, max_attempts: int = 12) -> tuple[int, int]:
    """
    Generate xlsx sampai ukuran file setidaknya target_bytes, seakurat mungkin,
    dengan JUMLAH wb.save() SEMINIMAL MUNGKIN.

    XLSX itu container ZIP terkompresi jadi ukurannya gak linear sempurna
    terhadap jumlah baris, dan wb.save() nulis ulang SELURUH file tiap
    dipanggil (biaya-nya naik seiring file makin gede). Nyimpen 1 baris per
    save() buat nutup gap terakhir itu O(n^2) dan bisa makan waktu puluhan
    menit buat file berukuran MB. Strategi di sini: satu lompatan besar ke
    ~90% target pakai estimasi rate, lalu beberapa iterasi koreksi coarse
    (bukan per-baris) sampai overshoot-nya kecil.

    Return (actual_size, total_rows).
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Data"
    ws.append(HEADER_ROW)
    wb.save(out_path)
    size = os.path.getsize(out_path)
    row_num = 0

    bytes_per_row = 55.0  # tebakan awal berdasarkan rata-rata baris dummy

    # Lompatan pertama: langsung ke ~90% target dalam SATU save()
    target_90 = int(target_bytes * 0.90)
    if size < target_90:
        est_rows = max(1, int((target_90 - size) / bytes_per_row))
        row_num = _add_rows(ws, row_num + 1, est_rows)
        wb.save(out_path)
        new_size = os.path.getsize(out_path)
        bytes_per_row = (new_size - size) / est_rows if est_rows else bytes_per_row
        size = new_size

    # Koreksi coarse: makin deket target, makin dikit baris yang ditambahin,
    # tapi tetep multi-baris per save(), bukan 1 baris per save().
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

    return size, row_num


def main():
    parser = argparse.ArgumentParser(description="Generate dummy XLSX ukuran presisi.")
    parser.add_argument(
        "--sizes",
        type=str,
        default=None,
        help="Comma-separated ukuran, misal '1kb,50kb,10mb'. Default: semua ukuran standar.",
    )
    parser.add_argument("--outdir", type=str, default=".", help="Folder output.")
    parser.add_argument(
        "--prefix", type=str, default="Contohnya-XLS", help="Prefix nama file output."
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
        out_path = os.path.join(args.outdir, f"{args.prefix}-{format_label(label)}.xlsx")
        actual, rows = generate_xlsx(out_path, size)
        # note: XLSX gak bisa byte-exact presisi kayak PDF (kompresi ZIP bikin
        # ukuran akhir gak linear), jadi hasilnya "≥ target, sedekat mungkin"
        over = actual - size
        print(f"{label:>8} -> {out_path}  [{actual} bytes, {rows} baris, +{over} dari target]")


if __name__ == "__main__":
    main()
