#!/usr/bin/env python3
"""
generate_dummy_rtf.py

Generate dummy file RTF (.rtf) buat testing upload, preview, dan size validation.

Karakter:
- Output valid Rich Text Format (.rtf), bukan file rename extension.
- Isinya aman, statis, dan harmless.
- Ukuran file diusahakan mendekati target dengan filler text RTF yang valid.
- Support custom variant size lewat parameter CLI.

Catatan:
- Karena RTF itu text-based, script ini bisa bikin ukuran sangat presisi.
- Tidak butuh dependency eksternal.
"""

import argparse
import os
import re
from typing import Dict, List, Tuple

DEFAULT_SIZES = [
    "10kb",
    "25kb",
    "50kb",
    "100kb",
    "250kb",
    "500kb",
    "1mb",
    "2mb",
    "5mb",
    "10mb",
]

MAX_DEFAULT_COUNT = 10
DEFAULT_MAX_SIZE_LABEL = "10mb"
OUTPUT_DIR = "."
DEFAULT_PREFIX = "Contohnya-RTF"


def parse_size(s: str, binary: bool = False) -> int:
    s = s.strip().lower()
    m = re.match(r"^([\d.]+)\s*(b|kb|mb|gb)?$", s)
    if not m:
        raise ValueError(f"Gak ngerti format ukuran: {s}")
    num, unit = m.groups()
    num = float(num)
    base = 1024 if binary else 1000
    mult = {None: 1, "b": 1, "kb": base, "mb": base**2, "gb": base**3}[unit]
    return int(num * mult)


def format_label(label: str) -> str:
    m = re.match(r"^([\d.]+)\s*(b|kb|mb|gb)$", label.strip().lower())
    if not m:
        return label.strip()
    num, unit = m.groups()
    return f"{num}{unit.upper()}"


def build_default_targets(binary: bool = False) -> Dict[str, int]:
    return {label: parse_size(label, binary=binary) for label in DEFAULT_SIZES}


def filtered_default_labels(max_size_label: str, count: int, binary: bool = False) -> List[str]:
    max_bytes = parse_size(max_size_label, binary=binary)
    labels = [label for label in DEFAULT_SIZES if parse_size(label, binary=binary) <= max_bytes]
    if not labels:
        raise ValueError("Tidak ada default size yang <= --max-size")
    return labels[:count]


def resolve_targets(args) -> List[Tuple[str, int]]:
    if args.sizes:
        labels = [x.strip() for x in args.sizes.split(",") if x.strip()]
        if len(labels) > MAX_DEFAULT_COUNT:
            raise ValueError(f"Maksimal {MAX_DEFAULT_COUNT} ukuran per generate.")
        return sorted(
            [(label.lower(), parse_size(label, binary=args.binary)) for label in labels],
            key=lambda kv: kv[1],
        )

    labels = filtered_default_labels(args.max_size, args.count, binary=args.binary)
    table = build_default_targets(binary=args.binary)
    return [(label, table[label]) for label in labels]


def rtf_escape(text: str) -> str:
    return text.replace("\\", r"\\").replace("{", r"\{").replace("}", r"\}")


def build_rtf_header(title: str, note: str) -> str:
    title = rtf_escape(title)
    note = rtf_escape(note)

    return (
        "{\\rtf1\\ansi\\deff0\n"
        "{\\fonttbl{\\f0 Arial;}{\\f1 Courier New;}}\n"
        "{\\colortbl;\\red34\\green34\\blue34;\\red70\\green90\\blue160;\\red90\\green90\\blue90;}\n"
        "\\viewkind4\\uc1\\pard\\sa180\\sl276\\slmult1\n"
        f"\\cf2\\b\\fs32 {title}\\b0\\cf1\\fs22\\par\n"
        f"\\i {note}\\i0\\par\n"
        "\\cf3 Generated safe dummy RTF file for upload testing, preview, and size validation.\\cf1\\par\n"
        "\\par\n"
    )


def build_rtf_footer() -> str:
    return "\\par\n}\n"


def filler_block(index: int) -> str:
    return (
        f"\\pard\\sa120\\sl240\\slmult1\\f0\\fs22 "
        f"Dummy paragraph {index}. "
        "This is a safe generated rich text document for testing upload workflows, "
        "preview rendering, parsing, and size validation. "
        "It contains repeated neutral content with simple formatting. "
        "\\b Bold sample\\b0, \\i italic sample\\i0, "
        "\\ul underline sample\\ul0. "
        "\\par\n"
        "\\pard\\li360\\sa120\\f1\\fs20 "
        "sample_field=name; sample_type=rtf; sample_status=valid; sample_mode=dummy; "
        "sample_purpose=testing-preview-validation; "
        "\\par\n"
    )


def build_filler_chunk(start_index: int, count: int = 20) -> str:
    return "".join(filler_block(start_index + i) for i in range(count))


def generate_rtf_near_target(path: str, target_size: int, title: str, note: str) -> int:
    header = build_rtf_header(title, note)
    footer = build_rtf_footer()

    min_size = len((header + footer).encode("utf-8"))
    if target_size < min_size:
        raise ValueError(
            f"Target size terlalu kecil untuk RTF valid. Minimum sekitar {min_size} bytes."
        )

    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(header)
        current_size = len(header.encode("utf-8"))
        block_index = 1

        while True:
            chunk = build_filler_chunk(block_index, count=20)
            chunk_size = len(chunk.encode("utf-8"))
            footer_size = len(footer.encode("utf-8"))

            if current_size + chunk_size + footer_size > target_size:
                break

            f.write(chunk)
            current_size += chunk_size
            block_index += 20

        remaining = target_size - current_size - footer_size
        if remaining > 0:
            base_line = (
                "\\pard\\sa120\\sl240\\slmult1\\f0\\fs20 "
                "Padding content for size tuning. "
            )
            base_bytes = base_line.encode("utf-8")
            if len(base_bytes) < remaining:
                f.write(base_line)
                current_size += len(base_bytes)
                remaining = target_size - current_size - footer_size

            if remaining > 0:
                pad_text_prefix = "X" * max(0, remaining - len("\\par\n".encode("utf-8")))
                pad_line = pad_text_prefix + "\\par\n"
                pad_bytes = pad_line.encode("utf-8")

                if len(pad_bytes) > remaining:
                    excess = len(pad_bytes) - remaining
                    pad_text_prefix = pad_text_prefix[:-excess]
                    pad_line = pad_text_prefix + "\\par\n"
                    pad_bytes = pad_line.encode("utf-8")

                if len(pad_bytes) <= remaining:
                    f.write(pad_line)
                    current_size += len(pad_bytes)

        f.write(footer)

    actual_size = os.path.getsize(path)
    return actual_size


def main():
    parser = argparse.ArgumentParser(description="Generate dummy RTF ukuran mendekati target.")
    parser.add_argument(
        "--sizes",
        type=str,
        default=None,
        help="Comma-separated ukuran custom, misal '10kb,100kb,1mb'. Maks 10 ukuran.",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=MAX_DEFAULT_COUNT,
        help="Jumlah varian default yang digenerate. Maks 10. Default 10.",
    )
    parser.add_argument(
        "--max-size",
        type=str,
        default=DEFAULT_MAX_SIZE_LABEL,
        help="Batas size terbesar untuk varian default. Default 10mb.",
    )
    parser.add_argument("--outdir", type=str, default=OUTPUT_DIR, help="Folder output.")
    parser.add_argument("--prefix", type=str, default=DEFAULT_PREFIX, help="Prefix nama file output.")
    parser.add_argument(
        "--title",
        type=str,
        default="contohnya.web.id",
        help="Judul dokumen di dalam file RTF.",
    )
    parser.add_argument(
        "--note",
        type=str,
        default="dummy file for testing",
        help="Keterangan/subjudul di dalam file RTF.",
    )
    parser.add_argument(
        "--binary",
        action="store_true",
        help="Pakai definisi binary (1 MB = 1024x1024 bytes) instead of decimal.",
    )
    args = parser.parse_args()

    if args.count < 1:
        raise ValueError("--count minimal 1")
    if args.count > MAX_DEFAULT_COUNT:
        raise ValueError(f"--count maksimal {MAX_DEFAULT_COUNT}")

    os.makedirs(args.outdir, exist_ok=True)
    targets = resolve_targets(args)

    print(f"Generating {len(targets)} dummy RTF files...\n")

    for raw_label, target_size in targets:
        pretty = format_label(raw_label)
        filename = f"{args.prefix}-{pretty}.rtf"
        filepath = os.path.join(args.outdir, filename)
        actual_size = generate_rtf_near_target(filepath, target_size, args.title, args.note)
        diff = actual_size - target_size
        status = "OK" if abs(diff) <= 256 else f"diff {diff:+d} bytes"

        print(
            f"{filename:22s} target={target_size:>10,} B "
            f"actual={actual_size:>10,} B ({status})"
        )

    print(f"\nDone. Files saved to {args.outdir}/")


if __name__ == "__main__":
    main()
