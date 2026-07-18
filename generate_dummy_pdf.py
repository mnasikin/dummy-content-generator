#!/usr/bin/env python3
"""
generate_dummy_pdf.py

Generate dummy PDF berukuran presisi (byte-exact) buat testing upload/download.
File yang dihasilkan tetap PDF valid (bisa dibuka di reader mana pun),
karena padding-nya masuk sebagai extra stream object, bukan garbage bytes
yang dipaksa berekstensi .pdf.

Install dependency dulu (sekali aja):
    pip install pikepdf reportlab --break-system-packages

Cara pakai:
    python3 generate_dummy_pdf.py                # generate semua ukuran default
    python3 generate_dummy_pdf.py --sizes 1kb,5mb # generate ukuran tertentu aja
    python3 generate_dummy_pdf.py --outdir ./pdf  # ganti folder output
    python3 generate_dummy_pdf.py --prefix dokumen-pdf  # ganti prefix nama file
"""

import argparse
import os
import re

import pikepdf
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# Handcrafted minimal PDF, dipake buat target super kecil (< ~1.5KB)
# dimana reportlab base-nya aja udah kelewat gede.
MINIMAL_PDF = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 200 200] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>
endobj
4 0 obj
<< /Length 58 >>
stream
BT /F1 8 Tf 10 180 Td (Contoh File PDF) Tj ET
endstream
endobj
5 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
xref
0 6
0000000000 65535 f 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
0
%%EOF
"""

# Pakai definisi DECIMAL (1 KB = 1000 bytes, 1 MB = 1_000_000 bytes), bukan
# binary/KiB (1024). Ini biar target "100mb" beneran nongol "100 MB" pas
# dicek di dashboard R2, file manager Mac/Linux, atau browser download bar -
# semua itu defaultnya nampilin ukuran pakai decimal, bukan binary.
# Kalo lo butuh definisi binary (1024-based / KiB-MiB), pass --binary.
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

# ---- Teks di dalam PDF, ubah sesuai kebutuhan lo ----
PDF_TITLE = "Contoh File PDF - Contohnya.web.id"
PDF_SUBTITLE = "Dummy file untuk testing"
# ------------------------------------------------------


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


def make_base_minimal(path: str):
    with open(path, "wb") as f:
        f.write(MINIMAL_PDF)


def make_base_full(path: str, label: str, num_pages: int = 1):
    c = canvas.Canvas(path, pagesize=A4)
    for i in range(num_pages):
        c.setFont("Helvetica-Bold", 20)
        c.drawString(72, 750, PDF_TITLE)
        c.setFont("Helvetica", 12)
        c.drawString(72, 720, f"Ukuran: {label}")
        c.drawString(72, 700, PDF_SUBTITLE)
        c.drawString(72, 680, f"Halaman {i + 1} dari {num_pages}")
        # baris filler biar tiap halaman ada isinya, bukan cuma header doang
        c.setFont("Helvetica", 9)
        for row in range(30):
            c.drawString(72, 650 - row * 16, f"Baris data dummy {i + 1}-{row + 1} — lorem ipsum testing content")
        c.showPage()
    c.save()


def choose_num_pages(target_bytes: int) -> int:
    """
    Makin gede target size-nya, makin banyak halaman beneran yang dibikin
    (bukan cuma 1 halaman + padding tersembunyi). Dicap di 500 halaman biar
    generation-nya tetep cepet buat file yang gede banget (50-100MB).
    """
    pages = target_bytes // 200_000  # kira-kira 1 halaman per 200KB target
    return max(1, min(pages, 500))


def pad_to_size(base_path: str, out_path: str, target_bytes: int, max_attempts: int = 8) -> int:
    """
    Tambahin stream object berisi random bytes (harus random, bukan byte
    berulang, soalnya byte berulang gampang kekompres pas pikepdf save)
    sampai ukuran file pas sama target_bytes.
    """
    base_size = os.path.getsize(base_path)
    if base_size > target_bytes:
        raise ValueError(
            f"Base PDF ({base_size} bytes) udah lebih gede dari target ({target_bytes} bytes). "
            "Pake base yang lebih kecil atau naikin target size."
        )

    guess = max(target_bytes - base_size - 60, 0)  # 60 = rough overhead objek

    for _ in range(max_attempts):
        with pikepdf.open(base_path) as pdf:
            padding = pikepdf.Stream(pdf, os.urandom(guess))
            pdf.Root.DummyPadding = padding
            # compress_streams=False WAJIB, kalo enggak random bytes-nya
            # tetep dicoba dikompres dan ukuran akhir jadi meleset dari target.
            pdf.save(
                out_path,
                compress_streams=False,
                stream_decode_level=pikepdf.StreamDecodeLevel.none,
            )

        actual = os.path.getsize(out_path)
        diff = target_bytes - actual
        if diff == 0:
            break
        guess = max(guess + diff, 0)

    return os.path.getsize(out_path)


def main():
    parser = argparse.ArgumentParser(description="Generate dummy PDF ukuran presisi.")
    parser.add_argument(
        "--sizes",
        type=str,
        default=None,
        help="Comma-separated ukuran, misal '1kb,50kb,10mb'. Default: semua ukuran standar.",
    )
    parser.add_argument("--outdir", type=str, default=".", help="Folder output.")
    parser.add_argument(
        "--prefix", type=str, default="Contohnya-PDF", help="Prefix nama file output."
    )
    parser.add_argument(
        "--binary",
        action="store_true",
        help="Pakai definisi binary (1 MB = 1024x1024 bytes / MiB) instead of decimal (1 MB = 1_000_000 bytes). Default: decimal.",
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

    base_minimal = os.path.join(args.outdir, "_base_minimal.pdf")
    base_full = os.path.join(args.outdir, "_base_full.pdf")
    make_base_minimal(base_minimal)

    for label, size in sorted(targets.items(), key=lambda kv: kv[1]):
        num_pages = choose_num_pages(size)
        make_base_full(base_full, label, num_pages=num_pages)
        base_size = os.path.getsize(base_full)

        # kalo target-nya kekecilan buat nampung num_pages halaman, kurangin
        # halaman-nya sampe muat, atau fallback ke base minimal (1 halaman kecil)
        while base_size > size and num_pages > 1:
            num_pages -= 1
            make_base_full(base_full, label, num_pages=num_pages)
            base_size = os.path.getsize(base_full)

        base = base_full if base_size <= size else base_minimal

        out_path = os.path.join(args.outdir, f"{args.prefix}-{format_label(label)}.pdf")
        actual = pad_to_size(base, out_path, size)
        status = "OK" if actual == size else f"MELESET ({actual} bytes)"
        pages_note = f"{num_pages} halaman" if base is base_full else "1 halaman (target kekecilan)"
        print(f"{label:>8} -> {out_path}  [{actual} bytes, {pages_note}]  {status}")

    os.remove(base_minimal)
    os.remove(base_full)


if __name__ == "__main__":
    main()
