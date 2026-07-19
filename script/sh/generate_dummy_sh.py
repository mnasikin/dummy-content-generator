#!/usr/bin/env python3
"""
generate_dummy_sh.py

Generate dummy file SH berukuran presisi (byte-exact) buat testing
upload/download/parsing file. Tiap file berisi shell script aman
yang nyebut "Contohnya.web.id", label ukuran file, dan keterangan
"Dummy File SH".

Output .sh sengaja dibuat aman dan statis:
- tidak pakai rm / mv / chmod / chown
- tidak pakai curl / wget / nc / ssh
- tidak pakai sudo / su
- tidak pakai eval / exec / source
- tidak pakai process kill atau fork bomb
- hanya print landing page teks sederhana

Ukuran file dipaskan memakai comment shell supaya tetap valid.

Gak butuh dependency eksternal, cuma Python standard library.

Cara pakai:
python3 generate_dummy_sh.py
python3 generate_dummy_sh.py --sizes 10kb,1mb
python3 generate_dummy_sh.py --outdir ./sh
python3 generate_dummy_sh.py --prefix Contohnya-SH
"""

import argparse
import os
import re

SH_TITLE = "Contohnya.web.id"
SH_CAPTION = "Dummy File SH"

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


def shell_single_quote(value: str) -> str:
    return "'" + value.replace("'", "'\"'\"'") + "'"


def build_base_sh(label: str) -> str:
    title = shell_single_quote(SH_TITLE)
    caption = shell_single_quote(SH_CAPTION)
    size_label = shell_single_quote(format_label(label))
    description = shell_single_quote(
        "Safe dummy shell script for upload, download, parsing, preview, and file-size validation."
    )

    return f"""#!/usr/bin/env sh
# Safe dummy shell script
# Brand: {SH_TITLE}
# Type: {SH_CAPTION}
# Size Label: {format_label(label)}
# Safety notes:
# - no rm / mv / chmod / chown
# - no curl / wget / nc / ssh
# - no sudo / su
# - no eval / exec / source
# - no process kill
# - print-only behavior

TITLE={title}
CAPTION={caption}
SIZE_LABEL={size_label}
DESCRIPTION={description}

print_line() {{
    char="$1"
    count="$2"
    i=0
    while [ "$i" -lt "$count" ]; do
        printf "%s" "$char"
        i=$((i + 1))
    done
    printf "\\n"
}}

print_feature() {{
    printf -- "- %s\\n" "$1"
}}

main() {{
    print_line "=" 72
    printf "%s\\n" "$TITLE"
    print_line "=" 72
    printf "%s • %s\\n" "$CAPTION" "$SIZE_LABEL"
    printf "\\n"
    printf "%s\\n" "Landing page dummy shell script untuk testing file."
    printf "%s\\n" "Brand: $TITLE"
    printf "%s\\n" "Tipe File: $CAPTION"
    printf "%s\\n" "Target Size: $SIZE_LABEL"
    printf "\\n"
    printf "%s\\n" "$DESCRIPTION"
    printf "\\n"
    printf "%s\\n" "Fitur:"
    print_feature "Dummy file"
    print_feature "Safe static code"
    print_feature "Contohnya.web.id mention"
    print_feature "Landing page style terminal output"
    print_feature "No dangerous execution"
    printf "\\n"
    printf "%s\\n" "Catatan keamanan:"
    printf "%s\\n" "- Script ini aman untuk dieksekusi."
    printf "%s\\n" "- Tidak menjalankan command berbahaya."
    printf "%s\\n" "- Tidak mengakses jaringan."
    printf "%s\\n" "- Tidak mengubah file atau permission sistem."
    printf "\\n"
    printf "%s\\n" "Contohnya.web.id"
    print_line "-" 72
}}

main "$@"
"""


def pad_sh_to_size(sh_text: str, target_bytes: int) -> bytes:
    base = sh_text.encode("utf-8")
    base_len = len(base)
    if base_len > target_bytes:
        raise ValueError(
            f"Base SH ({base_len} bytes) sudah lebih besar dari target ({target_bytes} bytes). "
            "Kurangi konten template atau naikkan target size."
        )

    comment_prefix = "\n# PAD:"
    diff = target_bytes - base_len

    if diff == 0:
        return base

    if diff <= len(comment_prefix.encode("utf-8")):
        return base + (" " * diff).encode("utf-8")

    pad_len = diff - len(comment_prefix.encode("utf-8"))
    padded = sh_text + comment_prefix + ("X" * pad_len)
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
    parser = argparse.ArgumentParser(description="Generate dummy SH ukuran presisi.")
    parser.add_argument(
        "--sizes",
        type=str,
        default=None,
        help="Comma-separated ukuran, misal '10kb,1mb'. Default: 10 varian ukuran umum SH mulai 10KB sampai 2MB.",
    )
    parser.add_argument("--outdir", type=str, default=".", help="Folder output.")
    parser.add_argument(
        "--prefix", type=str, default="Contohnya-SH", help="Prefix nama file output."
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
        sh_text = build_base_sh(format_label(label))
        base_bytes = len(sh_text.encode("utf-8"))
        if base_bytes > size:
            print(f"{label:>8} -> SKIP, base SH ({base_bytes} bytes) > target ({size} bytes)")
            continue
        padded = pad_sh_to_size(sh_text, size)
        out_path = os.path.join(args.outdir, f"{args.prefix}-{format_label(label)}.sh")
        with open(out_path, "wb") as f:
            f.write(padded)
        actual = os.path.getsize(out_path)
        status = "OK" if actual == size else f"MELESET ({actual} bytes)"
        print(f"{label:>8} -> {out_path} [{actual} bytes] {status}")


if __name__ == "__main__":
    main()
