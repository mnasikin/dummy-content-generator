#!/usr/bin/env python3
"""
generate_dummy_py.py

Generate dummy file Python berukuran presisi (byte-exact) buat testing
upload/download/parsing file. Tiap file berisi script Python aman
yang nyebut "Contohnya.web.id", label ukuran file, dan keterangan
"Dummy File PY".

Output .py sengaja dibuat aman dan statis:
- tidak pakai eval / exec
- tidak pakai os.system / subprocess
- tidak pakai network access
- tidak pakai file delete / rename
- tidak pakai import modul berbahaya
- hanya print landing page teks sederhana

Ukuran file dipaskan memakai comment Python supaya tetap valid.

Gak butuh dependency eksternal, cuma Python standard library.
Generator ini juga cuma pakai argparse, os, dan re.

Cara pakai:
python3 generate_dummy_py.py
python3 generate_dummy_py.py --sizes 10kb,1mb
python3 generate_dummy_py.py --outdir ./py
python3 generate_dummy_py.py --prefix Contohnya-PY
"""

import argparse
import os
import re

PY_TITLE = "Contohnya.web.id"
PY_CAPTION = "Dummy File PY"

DEFAULT_SIZES = {
    "10kb": 10_000,
    "25kb": 25_000,
    "50kb": 50_000,
    "100kb": 100_000,
    "150kb": 150_000,
    "250kb": 250_000,
    "500kb": 500_000,
    "750kb": 750_000,
    "1mb": 1_000_000,
    "2mb": 2_000_000,
}

DEFAULT_SIZES_BINARY = {
    "10kb": 10 * 1024,
    "25kb": 25 * 1024,
    "50kb": 50 * 1024,
    "100kb": 100 * 1024,
    "150kb": 150 * 1024,
    "250kb": 250 * 1024,
    "500kb": 500 * 1024,
    "750kb": 750 * 1024,
    "1mb": 1024 * 1024,
    "2mb": 2 * 1024 * 1024,
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


def build_base_py(label: str) -> str:
    return f'''#!/usr/bin/env python3
"""
Safe dummy Python file
Brand: {PY_TITLE}
Type: {PY_CAPTION}
Size Label: {format_label(label)}

Safety notes:
- no eval
- no exec
- no os.system
- no subprocess
- no network access
- no file deletion
- no dangerous imports
"""

TITLE = {PY_TITLE!r}
CAPTION = {PY_CAPTION!r}
SIZE_LABEL = {format_label(label)!r}
DESCRIPTION = "Safe dummy Python file for upload, download, parsing, preview, and file-size validation."

FEATURES = [
    "Dummy file",
    "Safe static code",
    "Contohnya.web.id mention",
    "Landing page style terminal output",
    "No dangerous execution",
]


def separator(char: str = "=" , width: int = 72) -> str:
    return char * width


def render_card(title: str, value: str) -> str:
    line = f"{{title}}: {{value}}"
    return line


def render_feature_list(items):
    lines = []
    for item in items:
        lines.append(f"- {{item}}")
    return "\\n".join(lines)


def render_landing_text() -> str:
    parts = [
        separator("="),
        f"{{TITLE}}",
        separator("="),
        f"{{CAPTION}} • {{SIZE_LABEL}}",
        "",
        "Landing page dummy Python untuk testing file.",
        f"Brand: {{TITLE}}",
        f"Tipe File: {{CAPTION}}",
        f"Target Size: {{SIZE_LABEL}}",
        "",
        DESCRIPTION,
        "",
        "Fitur:",
        render_feature_list(FEATURES),
        "",
        "Catatan keamanan:",
        "- Script ini aman untuk dieksekusi.",
        "- Tidak menjalankan shell command.",
        "- Tidak mengakses jaringan.",
        "- Tidak membaca atau menghapus file lain.",
        "",
        "Contohnya.web.id",
        separator("-"),
    ]
    return "\\n".join(parts)


def main() -> None:
    print(render_landing_text())


if __name__ == "__main__":
    main()
'''


def pad_py_to_size(py_text: str, target_bytes: int) -> bytes:
    base = py_text.encode("utf-8")
    base_len = len(base)
    if base_len > target_bytes:
        raise ValueError(
            f"Base PY ({base_len} bytes) sudah lebih besar dari target ({target_bytes} bytes). "
            "Kurangi konten template atau naikkan target size."
        )

    comment_prefix = "\n# PAD:"
    diff = target_bytes - base_len

    if diff == 0:
        return base

    if diff <= len(comment_prefix.encode("utf-8")):
        return base + (" " * diff).encode("utf-8")

    pad_len = diff - len(comment_prefix.encode("utf-8"))
    padded = py_text + comment_prefix + ("X" * pad_len)
    data = padded.encode("utf-8")

    actual = len(data)
    remain = target_bytes - actual

    if remain > 0:
        padded += "X" * remain
        data = padded.encode("utf-8")
    elif remain < 0:
        padded = padded[:remain]
        data = padded.encode("utf-8")

    return data[:target_bytes]


def main():
    parser = argparse.ArgumentParser(description="Generate dummy PY ukuran presisi.")
    parser.add_argument(
        "--sizes",
        type=str,
        default=None,
        help="Comma-separated ukuran, misal '10kb,1mb'. Default: 10 varian ukuran umum PY mulai 10KB sampai 2MB.",
    )
    parser.add_argument("--outdir", type=str, default=".", help="Folder output.")
    parser.add_argument(
        "--prefix", type=str, default="Contohnya-PY", help="Prefix nama file output."
    )
    parser.add_argument(
        "--binary",
        action="store_true",
        help="Pakai definisi binary (1 KB = 1024 bytes) instead of decimal (default).",
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
        py_text = build_base_py(format_label(label))
        base_bytes = len(py_text.encode("utf-8"))
        if base_bytes > size:
            print(f"{label:>8} -> SKIP, base PY ({base_bytes} bytes) > target ({size} bytes)")
            continue
        padded = pad_py_to_size(py_text, size)
        out_path = os.path.join(args.outdir, f"{args.prefix}-{format_label(label)}.py")
        with open(out_path, "wb") as f:
            f.write(padded)
        actual = os.path.getsize(out_path)
        status = "OK" if actual == size else f"MELESET ({actual} bytes)"
        print(f"{label:>8} -> {out_path} [{actual} bytes] {status}")


if __name__ == "__main__":
    main()
