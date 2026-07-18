#!/usr/bin/env python3
"""
generate_dummy_csv.py

Generate dummy file CSV berukuran presisi (byte-exact) buat testing
upload/parsing data tabular. Kolom: No, Keterangan (teks dummy), Sumber
(nyebutin contohnya.web.id secara berkala).

CSV itu format teks murni (gak dikompres), jadi byte-nya predictable dan
bisa di-hit persis - mirip pendekatan di generate_dummy_pdf.py /
generate_dummy_svg.py, BUKAN kayak generate_dummy_xlsx.py yang butuh
estimasi iteratif karena XLSX itu container ZIP.

Gak butuh dependency eksternal, cuma Python standard library.

Cara pakai:
    python3 generate_dummy_csv.py                  # generate 10 varian ukuran default
    python3 generate_dummy_csv.py --sizes 1kb,5mb   # generate ukuran tertentu aja
    python3 generate_dummy_csv.py --outdir ./csv    # ganti folder output
    python3 generate_dummy_csv.py --prefix Contohnya-CSV  # ganti prefix nama file
"""

import argparse
import os
import random
import re
import string

# ---- Teks di dalam CSV, ubah sesuai kebutuhan lo ----
SITE_MENTION = "contohnya.web.id"
MENTION_EVERY_N_ROWS = 5  # kolom "Sumber" nyebutin site tiap N baris
HEADER = "No,Keterangan,Sumber\n"
# --------------------------------------------------------

DEFAULT_SIZES = {
    "1kb": 1_000,
    "10kb": 10_000,
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
    "10kb": 10 * 1024,
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


def build_csv(target_bytes: int) -> tuple:
    """
    Bangun CSV persis target_bytes: nambahin baris dummy sampai mendekati
    target, terus baris terakhir di-pad presisi (nambahin karakter filler
    di kolom Keterangan) biar total byte-nya pas.
    Return (csv_string, actual_bytes, total_rows).
    """
    header_bytes = len(HEADER.encode("utf-8"))
    if header_bytes > target_bytes:
        raise ValueError(
            f"Header CSV ({header_bytes} bytes) sudah lebih besar dari target ({target_bytes} bytes)."
        )

    rows = []
    size = header_bytes
    row_num = 0

    while True:
        row_num += 1
        text = random_text()
        sumber = SITE_MENTION if row_num % MENTION_EVERY_N_ROWS == 0 else "-"
        row = f"{row_num},Dummy data testing - {text},{sumber}\n"
        row_bytes = len(row.encode("utf-8"))
        if size + row_bytes > target_bytes:
            row_num -= 1
            break
        rows.append(row)
        size += row_bytes

    remaining = target_bytes - size
    if remaining > 0:
        row_num += 1
        sumber = SITE_MENTION if row_num % MENTION_EVERY_N_ROWS == 0 else "-"
        prefix = f"{row_num},"
        suffix = f",{sumber}\n"
        overhead = len(prefix.encode("utf-8")) + len(suffix.encode("utf-8"))
        filler_len = max(0, remaining - overhead)
        filler = "x" * filler_len
        row = f"{prefix}{filler}{suffix}"
        actual_row_bytes = len(row.encode("utf-8"))

        # kalau masih ada sisa gap (baris digit row_num nambah jadi lebih
        # panjang dari perkiraan awal, dst), tambahin/kurangin filler sampai pas
        diff = (target_bytes - size) - actual_row_bytes
        if diff != 0:
            filler_len = max(0, filler_len + diff)
            filler = "x" * filler_len
            row = f"{prefix}{filler}{suffix}"
            actual_row_bytes = len(row.encode("utf-8"))

        rows.append(row)
        size += actual_row_bytes

    body = HEADER + "".join(rows)
    return body, len(body.encode("utf-8")), row_num


def main():
    parser = argparse.ArgumentParser(description="Generate dummy CSV ukuran presisi.")
    parser.add_argument(
        "--sizes",
        type=str,
        default=None,
        help="Comma-separated ukuran, misal '1kb,50kb,10mb'. Default: 10 varian standar.",
    )
    parser.add_argument("--outdir", type=str, default=".", help="Folder output.")
    parser.add_argument(
        "--prefix", type=str, default="Contohnya-CSV", help="Prefix nama file output."
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
        body, actual, rows = build_csv(size)
        out_path = os.path.join(args.outdir, f"{args.prefix}-{format_label(label)}.csv")
        with open(out_path, "w", encoding="utf-8", newline="") as f:
            f.write(body)
        actual_on_disk = os.path.getsize(out_path)
        status = "OK" if actual_on_disk == size else f"MELESET ({actual_on_disk} bytes)"
        print(f"{label:>8} -> {out_path}  [{actual_on_disk} bytes, {rows} baris]  {status}")


if __name__ == "__main__":
    main()
