#!/usr/bin/env python3
"""
generate_dummy_yaml.py

Generate dummy file YAML berukuran presisi (byte-exact) buat testing
upload/parsing config file. Isinya list item berulang dengan teks dummy,
dan mention contohnya.web.id secara berkala.

YAML itu format teks murni (gak dikompres), jadi byte-nya predictable dan
bisa di-hit persis - sama pendekatan kayak generate_dummy_xml.py /
generate_dummy_csv.py / generate_dummy_sql.py.

Max size default 10MB (bukan 100MB) - YAML pada praktiknya (config app,
CI/CD pipeline, Docker Compose, Kubernetes manifest) jarang butuh ukuran
gede banget, sama kayak XML.

Gak butuh dependency eksternal, cuma Python standard library.

Cara pakai:
    python3 generate_dummy_yaml.py                  # generate 10 varian ukuran default
    python3 generate_dummy_yaml.py --sizes 1kb,5mb   # generate ukuran tertentu aja
    python3 generate_dummy_yaml.py --outdir ./yaml   # ganti folder output
    python3 generate_dummy_yaml.py --prefix Contohnya-YAML  # ganti prefix nama file
"""

import argparse
import os
import random
import re
import string

# ---- Teks di dalam YAML, ubah sesuai kebutuhan lo ----
SITE_MENTION = "contohnya.web.id"
MENTION_EVERY_N_ROWS = 5  # field "sumber" nyebutin site tiap N item
HEADER = "# Dummy YAML - contohnya.web.id\nitems:\n"
# --------------------------------------------------------

# Max 10MB, 10 varian - YAML pada praktiknya jarang butuh sampai 100MB
DEFAULT_SIZES = {
    "1kb": 1_000,
    "5kb": 5_000,
    "10kb": 10_000,
    "50kb": 50_000,
    "100kb": 100_000,
    "500kb": 500_000,
    "1mb": 1_000_000,
    "2mb": 2_000_000,
    "5mb": 5_000_000,
    "10mb": 10_000_000,
}

DEFAULT_SIZES_BINARY = {
    "1kb": 1024,
    "5kb": 5 * 1024,
    "10kb": 10 * 1024,
    "50kb": 50 * 1024,
    "100kb": 100 * 1024,
    "500kb": 500 * 1024,
    "1mb": 1024 * 1024,
    "2mb": 2 * 1024 * 1024,
    "5mb": 5 * 1024 * 1024,
    "10mb": 10 * 1024 * 1024,
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


def yaml_escape(s: str) -> str:
    # quote pakai double-quote biar aman dari karakter spesial YAML
    return s.replace("\\", "\\\\").replace('"', '\\"')


def build_yaml(target_bytes: int) -> tuple:
    """
    Bangun YAML persis target_bytes: header (# comment + items:) + banyak
    list item sampai mendekati target, terus di-pad presisi pakai YAML
    comment di akhir biar total byte-nya pas.
    Return (yaml_string, actual_bytes, total_items).
    """
    header_bytes = len(HEADER.encode("utf-8"))
    if header_bytes > target_bytes:
        raise ValueError(
            f"Header YAML ({header_bytes} bytes) sudah lebih besar dari target ({target_bytes} bytes)."
        )

    items = []
    size = header_bytes
    item_num = 0

    while True:
        item_num += 1
        text = yaml_escape(f"Dummy data testing - {random_text()}")
        sumber = SITE_MENTION if item_num % MENTION_EVERY_N_ROWS == 0 else "-"
        item = (
            f"  - id: {item_num}\n"
            f'    keterangan: "{text}"\n'
            f"    sumber: {sumber}\n"
        )
        item_bytes = len(item.encode("utf-8"))
        if size + item_bytes > target_bytes:
            item_num -= 1
            break
        items.append(item)
        size += item_bytes

    # padding presisi pakai YAML comment di akhir (gak perlu newline penutup
    # karena ini baris terakhir file)
    remaining = target_bytes - size
    if remaining == 1:
        items.append("#")
        size += 1
    elif remaining >= 2:
        filler_len = remaining - 1
        padding = "#" + ("x" * filler_len)
        items.append(padding)
        size += len(padding.encode("utf-8"))

    body = HEADER + "".join(items)
    return body, len(body.encode("utf-8")), item_num


def main():
    parser = argparse.ArgumentParser(description="Generate dummy YAML ukuran presisi.")
    parser.add_argument(
        "--sizes",
        type=str,
        default=None,
        help="Comma-separated ukuran, misal '1kb,50kb,5mb'. Default: 10 varian standar (max 10MB).",
    )
    parser.add_argument("--outdir", type=str, default=".", help="Folder output.")
    parser.add_argument(
        "--prefix", type=str, default="Contohnya-YAML", help="Prefix nama file output."
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
        body, actual, items = build_yaml(size)
        out_path = os.path.join(args.outdir, f"{args.prefix}-{format_label(label)}.yaml")
        with open(out_path, "w", encoding="utf-8", newline="") as f:
            f.write(body)
        actual_on_disk = os.path.getsize(out_path)
        status = "OK" if actual_on_disk == size else f"MELESET ({actual_on_disk} bytes)"
        print(f"{label:>8} -> {out_path}  [{actual_on_disk} bytes, {items} item]  {status}")


if __name__ == "__main__":
    main()
