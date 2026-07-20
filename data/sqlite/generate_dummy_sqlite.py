#!/usr/bin/env python3
"""
generate_dummy_sqlite.py

Generate dummy file SQLite database (.sqlite) buat testing upload/import database.
Isinya tabel + banyak row dummy, dengan mention contohnya.web.id secara berkala.

PENTING:
- SQLite database asli TIDAK bisa byte-exact bebas seperti file teks.
- Ukuran file SQLite selalu kelipatan page_size.
- Jadi script ini akan membuat file SQLite VALID dengan ukuran
  "target atau lebih besar sedikit", bukan presisi 1 byte.

Kalau butuh byte-exact, pakai .sql dump, bukan .sqlite.

Gak butuh dependency eksternal, cuma Python standard library.

Cara pakai:
    python3 generate_dummy_sqlite.py
    python3 generate_dummy_sqlite.py --sizes 10kb,5mb,25mb
    python3 generate_dummy_sqlite.py --outdir ./sqlite
    python3 generate_dummy_sqlite.py --prefix Contohnya-SQLITE
"""

import argparse
import math
import os
import random
import re
import sqlite3
import string


SITE_MENTION = "contohnya.web.id"
MENTION_EVERY_N_ROWS = 5
TABLE_NAME = "dummy_data"
MAX_FILES = 10

DEFAULT_SIZES = {
    "10kb": 10_000,
    "25kb": 25_000,
    "50kb": 50_000,
    "100kb": 100_000,
    "250kb": 250_000,
    "500kb": 500_000,
    "1mb": 1_000_000,
    "5mb": 5_000_000,
    "10mb": 10_000_000,
    "25mb": 25_000_000,
}

DEFAULT_SIZES_BINARY = {
    "10kb": 10 * 1024,
    "25kb": 25 * 1024,
    "50kb": 50 * 1024,
    "100kb": 100 * 1024,
    "250kb": 250 * 1024,
    "500kb": 500 * 1024,
    "1mb": 1024 * 1024,
    "5mb": 5 * 1024 * 1024,
    "10mb": 10 * 1024 * 1024,
    "25mb": 25 * 1024 * 1024,
}

PAGE_SIZE = 512


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


def random_text(length: int = 80) -> str:
    chars = string.ascii_letters + string.digits + " "
    return "".join(random.choices(chars, k=length)).strip()


def init_db(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id INTEGER PRIMARY KEY,
            keterangan TEXT NOT NULL,
            sumber TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS filler_data (
            id INTEGER PRIMARY KEY,
            payload BLOB NOT NULL
        )
    """)
    conn.commit()


def db_size(conn: sqlite3.Connection) -> int:
    page_count = conn.execute("PRAGMA page_count").fetchone()[0]
    page_size = conn.execute("PRAGMA page_size").fetchone()[0]
    return page_count * page_size


def insert_dummy_rows(conn: sqlite3.Connection, start_id: int, count: int) -> int:
    cur = conn.cursor()
    for i in range(count):
        row_id = start_id + i
        sumber = SITE_MENTION if row_id % MENTION_EVERY_N_ROWS == 0 else "-"
        text = f"Dummy data testing - {random_text(96)}"
        cur.execute(
            f"INSERT INTO {TABLE_NAME} (id, keterangan, sumber) VALUES (?, ?, ?)",
            (row_id, text, sumber),
        )
    conn.commit()
    return start_id + count


def insert_blob(conn: sqlite3.Connection, blob_size: int):
    conn.execute("INSERT INTO filler_data (payload) VALUES (?)", (b"x" * blob_size,))
    conn.commit()


def round_up_to_page(target: int, page_size: int) -> int:
    return int(math.ceil(target / page_size) * page_size)


def build_sqlite_file(out_path: str, target_bytes: int) -> tuple:
    if os.path.exists(out_path):
        os.remove(out_path)

    conn = sqlite3.connect(out_path)
    try:
        conn.execute("PRAGMA journal_mode=DELETE")
        conn.execute("PRAGMA synchronous=OFF")
        conn.execute("PRAGMA auto_vacuum=NONE")
        conn.execute(f"PRAGMA page_size={PAGE_SIZE}")

        init_db(conn)

        target_rounded = round_up_to_page(target_bytes, PAGE_SIZE)
        row_id = 1

        while db_size(conn) < target_rounded:
            current = db_size(conn)
            remaining = target_rounded - current

            if remaining > 128 * 1024:
                row_id = insert_dummy_rows(conn, row_id, 500)
            elif remaining > 16 * 1024:
                row_id = insert_dummy_rows(conn, row_id, 50)
            else:
                blob_guess = max(256, remaining - PAGE_SIZE)
                insert_blob(conn, blob_guess)

            conn.commit()

            if db_size(conn) >= target_rounded:
                break

        conn.commit()
        actual = db_size(conn)
        page_size = conn.execute("PRAGMA page_size").fetchone()[0]
        return actual, row_id - 1, page_size, target_rounded
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(description="Generate dummy SQLite database ukuran target.")
    parser.add_argument(
        "--sizes",
        type=str,
        default=None,
        help="Comma-separated ukuran, misal '10kb,50kb,25mb'. Default: 10 varian standar (max 25MB).",
    )
    parser.add_argument("--outdir", type=str, default=".", help="Folder output.")
    parser.add_argument(
        "--prefix", type=str, default="Contohnya-SQLITE", help="Prefix nama file output."
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
        out_path = os.path.join(args.outdir, f"{args.prefix}-{format_label(label)}.sqlite")
        actual, rows, page_size, rounded_target = build_sqlite_file(out_path, size)

        if actual == size:
            status = "EXACT"
        elif actual == rounded_target:
            status = f"VALID (rounded to page size {page_size})"
        elif actual > size:
            status = f"VALID (overshoot {actual - size} bytes)"
        else:
            status = f"KURANG ({size - actual} bytes)"

        print(
            f"{label:>8} -> {out_path} "
            f"[{actual} bytes, {rows} row, page_size={page_size}, target_rounded={rounded_target}] "
            f"{status}"
        )


if __name__ == "__main__":
    main()
