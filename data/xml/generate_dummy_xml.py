#!/usr/bin/env python3
"""
generate_dummy_xml.py

Generate dummy file XML berukuran presisi (byte-exact) buat testing
upload/parsing data terstruktur. Isinya elemen <item> berulang dengan teks
dummy, dan mention contohnya.web.id secara berkala di elemen <sumber>.

XML itu format teks murni (gak dikompres), jadi byte-nya predictable dan
bisa di-hit persis - sama pendekatan kayak generate_dummy_csv.py /
generate_dummy_sql.py / generate_dummy_pdf.py.

Max size default 10MB (bukan 100MB) - XML pada praktiknya (config file, API
response, feed, dsb) jarang butuh ukuran gede banget, beda dari
PDF/ZIP/dokumen yang wajar sampai puluhan-ratusan MB.

Gak butuh dependency eksternal, cuma Python standard library.

Cara pakai:
    python3 generate_dummy_xml.py                  # generate 10 varian ukuran default
    python3 generate_dummy_xml.py --sizes 1kb,5mb   # generate ukuran tertentu aja
    python3 generate_dummy_xml.py --outdir ./xml    # ganti folder output
    python3 generate_dummy_xml.py --prefix Contohnya-XML  # ganti prefix nama file
"""

import argparse
import os
import random
import re
import string
import xml.sax.saxutils as saxutils

# ---- Teks di dalam XML, ubah sesuai kebutuhan lo ----
SITE_MENTION = "contohnya.web.id"
MENTION_EVERY_N_ROWS = 5  # elemen <sumber> nyebutin site tiap N item
ROOT_OPEN = '<?xml version="1.0" encoding="UTF-8"?>\n<data>\n'
ROOT_CLOSE = "</data>\n"
# --------------------------------------------------------

# Max 10MB, 10 varian - XML pada praktiknya jarang butuh sampai 100MB
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


def build_xml(target_bytes: int) -> tuple:
    """
    Bangun XML persis target_bytes: root <data> + banyak <item> sampai
    mendekati target, terus di-pad presisi pakai XML comment sebelum
    </data> biar total byte-nya pas.
    Return (xml_string, actual_bytes, total_items).
    """
    open_bytes = len(ROOT_OPEN.encode("utf-8"))
    close_bytes = len(ROOT_CLOSE.encode("utf-8"))
    overhead = open_bytes + close_bytes
    if overhead > target_bytes:
        raise ValueError(
            f"Overhead XML ({overhead} bytes) sudah lebih besar dari target ({target_bytes} bytes)."
        )

    items = []
    size = overhead
    item_num = 0

    while True:
        item_num += 1
        text = saxutils.escape(f"Dummy data testing - {random_text()}")
        sumber = SITE_MENTION if item_num % MENTION_EVERY_N_ROWS == 0 else "-"
        item = (
            f"  <item id=\"{item_num}\">\n"
            f"    <keterangan>{text}</keterangan>\n"
            f"    <sumber>{sumber}</sumber>\n"
            f"  </item>\n"
        )
        item_bytes = len(item.encode("utf-8"))
        if size + item_bytes > target_bytes:
            item_num -= 1
            break
        items.append(item)
        size += item_bytes

    # padding presisi pakai XML comment sebelum </data>
    remaining = target_bytes - size
    if remaining > 0:
        if remaining >= 9:  # minimal "<!--" + "-->" = 7, +buffer aman
            filler_len = remaining - 7
            filler = "x" * filler_len
            padding = f"<!--{filler}-->"
            actual_bytes = len(padding.encode("utf-8"))
            diff = remaining - actual_bytes
            if diff != 0:
                filler_len = max(0, filler_len + diff)
                filler = "x" * filler_len
                padding = f"<!--{filler}-->"
            items.append(padding)
            size += len(padding.encode("utf-8"))
        elif remaining > 0:
            # sisa terlalu kecil buat comment valid, isi whitespace aja
            items.append(" " * remaining)
            size += remaining

    body = ROOT_OPEN + "".join(items) + ROOT_CLOSE
    return body, len(body.encode("utf-8")), item_num


def main():
    parser = argparse.ArgumentParser(description="Generate dummy XML ukuran presisi.")
    parser.add_argument(
        "--sizes",
        type=str,
        default=None,
        help="Comma-separated ukuran, misal '1kb,50kb,5mb'. Default: 10 varian standar (max 10MB).",
    )
    parser.add_argument("--outdir", type=str, default=".", help="Folder output.")
    parser.add_argument(
        "--prefix", type=str, default="Contohnya-XML", help="Prefix nama file output."
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
        body, actual, items = build_xml(size)
        out_path = os.path.join(args.outdir, f"{args.prefix}-{format_label(label)}.xml")
        with open(out_path, "w", encoding="utf-8", newline="") as f:
            f.write(body)
        actual_on_disk = os.path.getsize(out_path)
        status = "OK" if actual_on_disk == size else f"MELESET ({actual_on_disk} bytes)"
        print(f"{label:>8} -> {out_path}  [{actual_on_disk} bytes, {items} item]  {status}")


if __name__ == "__main__":
    main()
