#!/usr/bin/env python3
"""
generate_dummy_sql.py

Generate dummy file SQL dump (.sql) berukuran presisi (byte-exact) buat
testing upload/import database. Isinya CREATE TABLE + banyak INSERT INTO
statement berisi data dummy, dengan mention contohnya.web.id secara berkala.

SQL dump itu format teks murni (gak dikompres), jadi byte-nya predictable
dan bisa di-hit persis - sama pendekatan kayak generate_dummy_csv.py /
generate_dummy_pdf.py / generate_dummy_svg.py.

Gak butuh dependency eksternal, cuma Python standard library.

Cara pakai:
    python3 generate_dummy_sql.py                  # generate 10 varian ukuran default
    python3 generate_dummy_sql.py --sizes 10kb,5mb  # generate ukuran tertentu aja
    python3 generate_dummy_sql.py --outdir ./sql    # ganti folder output
    python3 generate_dummy_sql.py --prefix Contohnya-SQL  # ganti prefix nama file
"""

import argparse
import os
import random
import re
import string

# ---- Teks di dalam SQL dump, ubah sesuai kebutuhan lo ----
SITE_MENTION = "contohnya.web.id"
MENTION_EVERY_N_ROWS = 5  # kolom "sumber" nyebutin site tiap N baris
TABLE_NAME = "dummy_data"
HEADER_TEMPLATE = (
    "-- Dummy SQL Dump - {site}\n"
    "-- Ukuran target: {label}\n"
    "-- File ini dibuat untuk keperluan testing upload dan import database.\n\n"
    "CREATE TABLE {table} (\n"
    "  id INT PRIMARY KEY,\n"
    "  keterangan VARCHAR(255),\n"
    "  sumber VARCHAR(255)\n"
    ");\n\n"
)
# --------------------------------------------------------------

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


def random_text(length: int = 30) -> str:
    return "".join(random.choices(string.ascii_letters + " ", k=length))


def sql_escape(s: str) -> str:
    return s.replace("'", "''")


def build_sql(target_bytes: int, label: str) -> tuple:
    """
    Bangun SQL dump persis target_bytes: header (CREATE TABLE) + banyak
    INSERT INTO sampai mendekati target, terus di-pad presisi pakai SQL
    comment block di akhir biar total byte-nya pas.
    Return (sql_string, actual_bytes, total_rows).
    """
    header = HEADER_TEMPLATE.format(site=SITE_MENTION, label=label, table=TABLE_NAME)
    header_bytes = len(header.encode("utf-8"))
    if header_bytes > target_bytes:
        raise ValueError(
            f"Header SQL ({header_bytes} bytes) sudah lebih besar dari target ({target_bytes} bytes)."
        )

    rows = []
    size = header_bytes
    row_num = 0

    while True:
        row_num += 1
        text = sql_escape(f"Dummy data testing - {random_text()}")
        sumber = SITE_MENTION if row_num % MENTION_EVERY_N_ROWS == 0 else "-"
        row = f"INSERT INTO {TABLE_NAME} (id, keterangan, sumber) VALUES ({row_num}, '{text}', '{sumber}');\n"
        row_bytes = len(row.encode("utf-8"))
        if size + row_bytes > target_bytes:
            row_num -= 1
            break
        rows.append(row)
        size += row_bytes

    # padding presisi pakai SQL comment block di akhir (gak perlu newline
    # penutup karena ini baris terakhir file, jadi bisa nutup gap sekecil
    # apapun - minimal cuma "--" 2 byte + filler)
    remaining = target_bytes - size
    if remaining == 1:
        rows.append("x")  # kasus super jarang: sisa 1 byte doang
        size += 1
    elif remaining >= 2:
        filler_len = remaining - 2
        padding_line = "--" + ("x" * filler_len)
        rows.append(padding_line)
        size += len(padding_line.encode("utf-8"))

    body = header + "".join(rows)
    return body, len(body.encode("utf-8")), row_num


def main():
    parser = argparse.ArgumentParser(description="Generate dummy SQL dump ukuran presisi.")
    parser.add_argument(
        "--sizes",
        type=str,
        default=None,
        help="Comma-separated ukuran, misal '10kb,50kb,10mb'. Default: 10 varian standar (max 100MB).",
    )
    parser.add_argument("--outdir", type=str, default=".", help="Folder output.")
    parser.add_argument(
        "--prefix", type=str, default="Contohnya-SQL", help="Prefix nama file output."
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
        body, actual, rows = build_sql(size, format_label(label))
        out_path = os.path.join(args.outdir, f"{args.prefix}-{format_label(label)}.sql")
        with open(out_path, "w", encoding="utf-8", newline="") as f:
            f.write(body)
        actual_on_disk = os.path.getsize(out_path)
        status = "OK" if actual_on_disk == size else f"MELESET ({actual_on_disk} bytes)"
        print(f"{label:>8} -> {out_path}  [{actual_on_disk} bytes, {rows} baris INSERT]  {status}")


if __name__ == "__main__":
    main()