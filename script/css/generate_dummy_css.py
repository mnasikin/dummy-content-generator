#!/usr/bin/env python3
"""
generate_dummy_css.py

Generate dummy file CSS (.css) buat testing upload, preview, dan size validation.
File yang dihasilkan valid, aman, dan isinya berupa CSS statis dengan ukuran
byte-exact atau sedekat mungkin ke target.

Karakteristik:
- Output valid .css
- Aman, tanpa dependency eksternal
- Default generate maksimal 10 file
- Default size terbesar 10MB
- Varian size bebas, gak harus mulai dari 1KB
- Isi file berupa komentar, custom properties, utility classes, dan dummy rules
- Filler akhir pakai komentar CSS supaya ukuran presisi
"""

import argparse
import os
import re
from typing import Dict, List, Tuple

SITE_MENTION = "contohnya.web.id"
DEFAULT_SIZES = [
    "4kb",
    "8kb",
    "16kb",
    "32kb",
    "64kb",
    "128kb",
    "256kb",
    "512kb",
    "1mb",
    "10mb",
]
MAX_DEFAULT_COUNT = 10
DEFAULT_MAX_SIZE_LABEL = "10mb"


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


def header_block(label: str) -> str:
    return (
        "/*\n"
        f" * Dummy CSS File - {SITE_MENTION}\n"
        f" * Ukuran target: {label}\n"
        " * File ini dibuat untuk testing upload, preview, dan validasi ukuran.\n"
        " * Seluruh isi aman dan hanya berisi deklarasi CSS statis.\n"
        " */\n\n"
        ":root {\n"
        "  --dummy-site: 'contohnya.web.id';\n"
        f"  --dummy-target-size: '{label}';\n"
        "  --dummy-color-1: #0f172a;\n"
        "  --dummy-color-2: #1e293b;\n"
        "  --dummy-color-3: #334155;\n"
        "  --dummy-color-4: #64748b;\n"
        "  --dummy-color-5: #94a3b8;\n"
        "}\n\n"
    )


def css_chunk(index: int) -> str:
    return f"""
/* Section {index:05d} */
.component-{index:05d} {{
  display: block;
  position: relative;
  box-sizing: border-box;
  width: calc(100% - {(index % 17) + 1}px);
  min-height: {(index % 9) + 24}px;
  margin: {(index % 11) + 2}px auto;
  padding: {(index % 13) + 4}px {(index % 7) + 8}px;
  border: 1px solid rgba(15, 23, 42, 0.{(index % 8) + 1});
  border-radius: {(index % 12) + 2}px;
  background: linear-gradient(180deg, rgba(248, 250, 252, 0.96), rgba(241, 245, 249, 0.92));
  color: #0f172a;
  font-size: {(index % 6) + 12}px;
  line-height: 1.5;
  letter-spacing: 0.02em;
  overflow: hidden;
}}

.component-{index:05d}::before {{
  content: "dummy-{index:05d}";
  display: inline-block;
  padding: 2px 6px;
  margin-right: 8px;
  border-radius: 999px;
  background-color: rgba(51, 65, 85, 0.08);
  color: #334155;
}}

.component-{index:05d}:hover {{
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(241, 245, 249, 0.96));
  border-color: rgba(30, 41, 59, 0.28);
}}

.grid-{index:05d} {{
  display: grid;
  grid-template-columns: repeat({(index % 4) + 2}, minmax(0, 1fr));
  gap: {(index % 10) + 4}px;
}}

.text-{index:05d} {{
  font-weight: {(index % 5 + 4) * 100};
  text-transform: {'uppercase' if index % 2 == 0 else 'none'};
  text-decoration: {'underline' if index % 3 == 0 else 'none'};
}}

@media (max-width: {(index % 5) * 120 + 480}px) {{
  .component-{index:05d} {{
    width: 100%;
    padding: {(index % 9) + 6}px;
  }}

  .grid-{index:05d} {{
    grid-template-columns: 1fr;
  }}
}}
"""


def make_exact_comment_fill(remaining: int) -> str:
    if remaining <= 0:
        return ""
    if remaining == 1:
        return "\n"
    if remaining == 2:
        return "/\n"
    if remaining == 3:
        return "/**"
    if remaining == 4:
        return "/**/"
    return "/*" + ("x" * (remaining - 4)) + "*/"


def build_css_content(target_bytes: int, label: str) -> str:
    content = header_block(label)
    idx = 1

    while True:
        chunk = css_chunk(idx)
        next_size = len((content + chunk).encode("utf-8"))
        if next_size > target_bytes:
            break
        content += chunk
        idx += 1

    current = len(content.encode("utf-8"))
    remaining = target_bytes - current
    if remaining > 0:
        content += make_exact_comment_fill(remaining)

    encoded = content.encode("utf-8")
    if len(encoded) != target_bytes:
        diff = target_bytes - len(encoded)
        if diff > 0:
            content += make_exact_comment_fill(diff)
        else:
            content = encoded[:target_bytes].decode("utf-8", errors="ignore")
    return content


def main():
    parser = argparse.ArgumentParser(description="Generate dummy CSS ukuran presisi.")
    parser.add_argument(
        "--sizes",
        type=str,
        default=None,
        help="Comma-separated ukuran custom, misal '32kb,128kb,1mb,7mb'. Maks 10 ukuran.",
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
    parser.add_argument("--outdir", type=str, default=".", help="Folder output.")
    parser.add_argument("--prefix", type=str, default="Contohnya-CSS", help="Prefix nama file output.")
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

    for raw_label, size in targets:
        pretty = format_label(raw_label)
        out_path = os.path.join(args.outdir, f"{args.prefix}-{pretty}.css")
        content = build_css_content(size, pretty)
        with open(out_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        actual = os.path.getsize(out_path)
        diff = actual - size
        print(f"{raw_label:>8} -> {out_path} [{actual} bytes, {diff:+d} dari target]")


if __name__ == "__main__":
    main()
