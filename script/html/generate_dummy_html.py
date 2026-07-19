#!/usr/bin/env python3
"""
generate_dummy_html.py

Generate dummy file HTML berukuran presisi (byte-exact) buat testing
upload/download/parsing file. Tiap file berisi landing page sederhana
yang nyebut "Contohnya.web.id", label ukuran file, dan keterangan
"Dummy File HTML".

HTML itu format teks, jadi gampang di-padding byte-exact pakai comment HTML
supaya ukuran file pas sesuai target.

Gak butuh dependency eksternal, cuma Python standard library.

Cara pakai:
python3 generate_dummy_html.py
python3 generate_dummy_html.py --sizes 10kb,100kb
python3 generate_dummy_html.py --outdir ./html
python3 generate_dummy_html.py --prefix Contohnya-HTML
"""

import argparse
import os
import re

HTML_TITLE = "Contohnya.web.id"
HTML_CAPTION = "Dummy File HTML"

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


def build_base_html(label: str) -> str:
    return f"""<!doctype html>
<html lang="id">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{HTML_TITLE} - {format_label(label)}</title>
  <meta name="description" content="{HTML_CAPTION} untuk testing ukuran file {format_label(label)}.">
  <style>
    :root {{
      --bg1: #0f172a;
      --bg2: #1e293b;
      --accent1: #60a5fa;
      --accent2: #34d399;
      --accent3: #f59e0b;
      --text: #e5eef9;
      --muted: #b9c6d8;
      --card: rgba(255,255,255,.08);
      --border: rgba(255,255,255,.12);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      font-family: Inter, Arial, sans-serif;
      color: var(--text);
      background:
        radial-gradient(circle at top left, rgba(96,165,250,.28), transparent 32%),
        radial-gradient(circle at bottom right, rgba(52,211,153,.22), transparent 28%),
        linear-gradient(135deg, var(--bg1), var(--bg2));
    }}
    .wrap {{
      max-width: 1120px;
      margin: 0 auto;
      padding: 32px 20px 64px;
    }}
    .nav {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 48px;
    }}
    .brand {{
      font-size: 20px;
      font-weight: 800;
      letter-spacing: .2px;
    }}
    .badge {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 14px;
      border: 1px solid var(--border);
      background: rgba(255,255,255,.06);
      border-radius: 999px;
      color: var(--muted);
      font-size: 14px;
    }}
    .hero {{
      display: grid;
      grid-template-columns: 1.2fr .8fr;
      gap: 28px;
      align-items: stretch;
    }}
    .panel {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 24px;
      backdrop-filter: blur(12px);
      box-shadow: 0 18px 60px rgba(0,0,0,.24);
    }}
    .hero-copy {{ padding: 40px; }}
    h1 {{
      margin: 0 0 16px;
      font-size: clamp(38px, 7vw, 72px);
      line-height: 1.02;
    }}
    p {{
      margin: 0 0 14px;
      color: var(--muted);
      font-size: 17px;
      line-height: 1.7;
    }}
    .cta-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-top: 26px;
    }}
    .btn {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-height: 44px;
      padding: 12px 18px;
      border-radius: 14px;
      text-decoration: none;
      font-weight: 700;
      border: 1px solid transparent;
    }}
    .btn-primary {{
      background: linear-gradient(135deg, var(--accent1), var(--accent2));
      color: #08111f;
    }}
    .btn-secondary {{
      border-color: var(--border);
      color: var(--text);
      background: rgba(255,255,255,.04);
    }}
    .hero-side {{
      padding: 28px;
      display: grid;
      gap: 16px;
    }}
    .stat {{
      padding: 18px;
      border-radius: 18px;
      background: rgba(255,255,255,.05);
      border: 1px solid rgba(255,255,255,.08);
    }}
    .stat-label {{
      font-size: 13px;
      color: var(--muted);
      margin-bottom: 8px;
      text-transform: uppercase;
      letter-spacing: .08em;
    }}
    .stat-value {{
      font-size: 28px;
      font-weight: 800;
    }}
    .features {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 18px;
      margin-top: 28px;
    }}
    .feature {{ padding: 22px; }}
    .feature h3 {{ margin: 0 0 10px; font-size: 18px; }}
    .footer {{
      margin-top: 28px;
      color: var(--muted);
      font-size: 14px;
      text-align: center;
    }}
    code {{
      padding: 2px 8px;
      border-radius: 999px;
      background: rgba(255,255,255,.08);
      border: 1px solid rgba(255,255,255,.08);
      color: #fff;
    }}
    @media (max-width: 860px) {{
      .hero {{ grid-template-columns: 1fr; }}
      .features {{ grid-template-columns: 1fr; }}
      .hero-copy {{ padding: 28px; }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="nav">
      <div class="brand">{HTML_TITLE}</div>
      <div class="badge">Dummy File HTML • {format_label(label)}</div>
    </div>

    <section class="hero">
      <div class="panel hero-copy">
        <p style="margin-bottom:10px;color:#93c5fd;font-weight:700;">Testing File Generator</p>
        <h1>Landing page dummy HTML untuk {format_label(label)}</h1>
        <p>File ini dibuat otomatis sebagai <strong>{HTML_CAPTION}</strong> dan menyebut <strong>{HTML_TITLE}</strong> seperti generator format lain.</p>
        <p>Tujuannya buat kebutuhan testing upload, download, parsing, preview, atau validasi ukuran file HTML.</p>
        <div class="cta-row">
          <a class="btn btn-primary" href="#detail">Lihat Detail</a>
          <a class="btn btn-secondary" href="https://contohnya.web.id" target="_blank" rel="noopener noreferrer">Buka Contohnya.web.id</a>
        </div>
      </div>

      <div class="panel hero-side">
        <div class="stat">
          <div class="stat-label">Nama Brand</div>
          <div class="stat-value">{HTML_TITLE}</div>
        </div>
        <div class="stat">
          <div class="stat-label">Tipe File</div>
          <div class="stat-value">Dummy HTML</div>
        </div>
        <div class="stat">
          <div class="stat-label">Target Size</div>
          <div class="stat-value">{format_label(label)}</div>
        </div>
      </div>
    </section>

    <section id="detail" class="features">
      <article class="panel feature">
        <h3>Dummy file</h3>
        <p>Konten ini memang bukan landing page produksi, tapi cukup representatif untuk simulasi file HTML yang wajar.</p>
      </article>
      <article class="panel feature">
        <h3>Siap dites</h3>
        <p>Bisa dipakai buat uji upload manager, file browser, MIME detection, preview HTML, dan pengecekan byte size.</p>
      </article>
      <article class="panel feature">
        <h3>Ukuran presisi</h3>
        <p>Ukuran akhir file dibuat pas dengan target menggunakan padding di dalam comment HTML agar tetap valid.</p>
      </article>
    </section>

    <div class="footer">
      Dibuat otomatis oleh generator dummy file untuk <code>{HTML_TITLE}</code> • Label ukuran: <code>{format_label(label)}</code>
    </div>
  </div>
</body>
</html>
"""


def pad_html_to_size(html_text: str, target_bytes: int) -> bytes:
    base = html_text.encode('utf-8')
    base_len = len(base)
    if base_len > target_bytes:
        raise ValueError(
            f"Base HTML ({base_len} bytes) sudah lebih besar dari target ({target_bytes} bytes). "
            "Kurangi konten template atau naikkan target size."
        )

    comment_open = "\n<!-- PAD:"
    comment_close = "-->"
    overhead = len((comment_open + comment_close).encode('utf-8'))
    diff = target_bytes - base_len

    if diff == 0:
        return base

    if diff < overhead:
        return base + (" " * diff).encode('utf-8')

    pad_len = diff - overhead
    padding = "X" * pad_len
    padded = html_text + comment_open + padding + comment_close
    data = padded.encode('utf-8')

    actual = len(data)
    remain = target_bytes - actual
    if remain > 0:
        insert = "X" * remain
        padded = html_text + comment_open + padding + insert + comment_close
        data = padded.encode('utf-8')
    elif remain < 0:
        padding = padding[:remain]
        padded = html_text + comment_open + padding + comment_close
        data = padded.encode('utf-8')

    return data[:target_bytes]


def main():
    parser = argparse.ArgumentParser(description="Generate dummy HTML ukuran presisi.")
    parser.add_argument(
        "--sizes",
        type=str,
        default=None,
        help="Comma-separated ukuran, misal '10kb,1mb'. Default: 10 varian ukuran umum HTML mulai 10KB sampai 2MB.",
    )
    parser.add_argument("--outdir", type=str, default=".", help="Folder output.")
    parser.add_argument(
        "--prefix", type=str, default="Contohnya-HTML", help="Prefix nama file output."
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
        html_text = build_base_html(format_label(label))
        base_bytes = len(html_text.encode('utf-8'))
        if base_bytes > size:
            print(f"{label:>8} -> SKIP, base HTML ({base_bytes} bytes) > target ({size} bytes)")
            continue
        padded = pad_html_to_size(html_text, size)
        out_path = os.path.join(args.outdir, f"{args.prefix}-{format_label(label)}.html")
        with open(out_path, "wb") as f:
            f.write(padded)
        actual = os.path.getsize(out_path)
        status = "OK" if actual == size else f"MELESET ({actual} bytes)"
        print(f"{label:>8} -> {out_path} [{actual} bytes] {status}")


if __name__ == "__main__":
    main()
