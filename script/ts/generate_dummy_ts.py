#!/usr/bin/env python3
"""
generate_dummy_ts.py

Generate dummy file TS berukuran presisi (byte-exact) buat testing
upload/download/parsing file. Tiap file berisi script TypeScript aman
yang nyebut "Contohnya.web.id", label ukuran file, dan keterangan
"Dummy File TS".

Output .ts sengaja dibuat aman dan statis:
- tidak pakai eval / new Function
- tidak pakai fetch / XHR / WebSocket
- tidak pakai import / require
- tidak pakai localStorage / sessionStorage
- tidak pakai innerHTML dari string dinamis
- hanya render landing page sederhana dengan textContent
- memakai type annotation yang aman dan jelas

Ukuran file dipaskan memakai block comment supaya tetap valid.

Gak butuh dependency eksternal, cuma Python standard library.

Cara pakai:
python3 generate_dummy_ts.py
python3 generate_dummy_ts.py --sizes 10kb,1mb
python3 generate_dummy_ts.py --outdir ./ts
python3 generate_dummy_ts.py --prefix Contohnya-TS
"""

import argparse
import os
import re

TS_TITLE = "Contohnya.web.id"
TS_CAPTION = "Dummy File TS"

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


def build_base_ts(label: str) -> str:
    return f"""/*!
 * Safe dummy TypeScript file
 * Brand: {TS_TITLE}
 * Type: {TS_CAPTION}
 * Size Label: {format_label(label)}
 * Notes:
 * - no eval
 * - no dynamic function constructor
 * - no network access
 * - no storage access
 * - safe static DOM rendering only
 */

type FeatureItem = {{
  title: string;
  text: string;
}};

type AppConfig = {{
  title: string;
  type: string;
  size: string;
  description: string;
  features: readonly string[];
}};

const APP_CONFIG: AppConfig = {{
  title: {TS_TITLE!r},
  type: {TS_CAPTION!r},
  size: {format_label(label)!r},
  description: 'Safe dummy TypeScript file for upload, download, parsing, preview, and file-size validation.',
  features: [
    'Dummy file',
    'Safe static code',
    'Contohnya.web.id mention',
    'Landing page style output',
    'No dangerous execution',
  ] as const,
}};

const FEATURE_CARDS: readonly FeatureItem[] = [
  {{
    title: 'Safe code',
    text: 'Output TS hanya merender konten statis secara aman dengan textContent tanpa eval, Function, network call, atau storage access.',
  }},
  {{
    title: 'Siap dites',
    text: 'Bisa dipakai buat uji upload manager, file browser, MIME detection, preview TypeScript, dan pengecekan byte size.',
  }},
  {{
    title: 'Ukuran presisi',
    text: 'Ukuran akhir file dibuat pas dengan target menggunakan padding di dalam comment block agar file tetap valid sebagai TypeScript.',
  }},
];

function createNode<K extends keyof HTMLElementTagNameMap>(
  tag: K,
  className?: string,
  text?: string
): HTMLElementTagNameMap[K] {{
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (typeof text === 'string') node.textContent = text;
  return node;
}}

function append(parent: HTMLElement, children: Node[]): HTMLElement {{
  children.forEach((child: Node) => {{
    parent.appendChild(child);
  }});
  return parent;
}}

function injectStyles(): void {{
  if (typeof document === 'undefined' || !document.head) return;

  const style: HTMLStyleElement = document.createElement('style');
  style.textContent = `
    :root {{
      --bg1: #0f172a;
      --bg2: #1e293b;
      --accent1: #60a5fa;
      --accent2: #34d399;
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
    .dummy-ts-wrap {{
      max-width: 1120px;
      margin: 0 auto;
      padding: 32px 20px 64px;
    }}
    .dummy-ts-nav {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 48px;
      flex-wrap: wrap;
    }}
    .dummy-ts-brand {{
      font-size: 20px;
      font-weight: 800;
      letter-spacing: .2px;
    }}
    .dummy-ts-badge {{
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
    .dummy-ts-hero {{
      display: grid;
      grid-template-columns: 1.2fr .8fr;
      gap: 28px;
      align-items: stretch;
    }}
    .dummy-ts-panel {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 24px;
      backdrop-filter: blur(12px);
      box-shadow: 0 18px 60px rgba(0,0,0,.24);
    }}
    .dummy-ts-copy {{
      padding: 40px;
    }}
    .dummy-ts-kicker {{
      margin: 0 0 10px;
      color: #93c5fd;
      font-weight: 700;
    }}
    .dummy-ts-title {{
      margin: 0 0 16px;
      font-size: clamp(38px, 7vw, 72px);
      line-height: 1.02;
    }}
    .dummy-ts-text {{
      margin: 0 0 14px;
      color: var(--muted);
      font-size: 17px;
      line-height: 1.7;
    }}
    .dummy-ts-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-top: 26px;
    }}
    .dummy-ts-btn {{
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
    .dummy-ts-btn-primary {{
      background: linear-gradient(135deg, var(--accent1), var(--accent2));
      color: #08111f;
    }}
    .dummy-ts-btn-secondary {{
      border-color: var(--border);
      color: var(--text);
      background: rgba(255,255,255,.04);
    }}
    .dummy-ts-side {{
      padding: 28px;
      display: grid;
      gap: 16px;
    }}
    .dummy-ts-stat {{
      padding: 18px;
      border-radius: 18px;
      background: rgba(255,255,255,.05);
      border: 1px solid rgba(255,255,255,.08);
    }}
    .dummy-ts-stat-label {{
      font-size: 13px;
      color: var(--muted);
      margin-bottom: 8px;
      text-transform: uppercase;
      letter-spacing: .08em;
    }}
    .dummy-ts-stat-value {{
      font-size: 28px;
      font-weight: 800;
    }}
    .dummy-ts-features {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 18px;
      margin-top: 28px;
    }}
    .dummy-ts-feature {{
      padding: 22px;
    }}
    .dummy-ts-feature-title {{
      margin: 0 0 10px;
      font-size: 18px;
    }}
    .dummy-ts-footer {{
      margin-top: 28px;
      color: var(--muted);
      font-size: 14px;
      text-align: center;
    }}
    .dummy-ts-code {{
      display: inline-block;
      padding: 2px 8px;
      border-radius: 999px;
      background: rgba(255,255,255,.08);
      border: 1px solid rgba(255,255,255,.08);
      color: #fff;
    }}
    @media (max-width: 860px) {{
      .dummy-ts-hero {{ grid-template-columns: 1fr; }}
      .dummy-ts-features {{ grid-template-columns: 1fr; }}
      .dummy-ts-copy {{ padding: 28px; }}
    }}
  `;
  document.head.appendChild(style);
}}

function buildFeatureCard(item: FeatureItem): HTMLElement {{
  const card = createNode('article', 'dummy-ts-panel dummy-ts-feature');
  const heading = createNode('h3', 'dummy-ts-feature-title', item.title);
  const body = createNode('p', 'dummy-ts-text', item.text);
  return append(card, [heading, body]);
}}

function renderApp(): void {{
  if (typeof document === 'undefined' || !document.body) return;

  injectStyles();
  document.title = APP_CONFIG.title + ' - ' + APP_CONFIG.size;

  const wrap = createNode('div', 'dummy-ts-wrap');

  const nav = createNode('div', 'dummy-ts-nav');
  const brand = createNode('div', 'dummy-ts-brand', APP_CONFIG.title);
  const badge = createNode('div', 'dummy-ts-badge', APP_CONFIG.type + ' • ' + APP_CONFIG.size);
  append(nav, [brand, badge]);

  const hero = createNode('section', 'dummy-ts-hero');

  const copy = createNode('div', 'dummy-ts-panel dummy-ts-copy');
  const kicker = createNode('p', 'dummy-ts-kicker', 'Testing File Generator');
  const title = createNode('h1', 'dummy-ts-title', 'Landing page dummy TS untuk ' + APP_CONFIG.size);
  const text1 = createNode('p', 'dummy-ts-text', 'File ini dibuat otomatis sebagai ' + APP_CONFIG.type + ' dan menyebut ' + APP_CONFIG.title + ' seperti generator format lain.');
  const text2 = createNode('p', 'dummy-ts-text', 'Script TypeScript ini aman, statis, dan tidak menjalankan operasi berbahaya. Cocok untuk testing upload, parsing, preview, dan validasi ukuran file TS.');

  const row = createNode('div', 'dummy-ts-row');
  const btn1 = createNode('a', 'dummy-ts-btn dummy-ts-btn-primary', 'Lihat Detail') as HTMLAnchorElement;
  btn1.href = '#detail';

  const btn2 = createNode('a', 'dummy-ts-btn dummy-ts-btn-secondary', 'Buka Contohnya.web.id') as HTMLAnchorElement;
  btn2.href = 'https://contohnya.web.id';
  btn2.target = '_blank';
  btn2.rel = 'noopener noreferrer';

  append(row, [btn1, btn2]);
  append(copy, [kicker, title, text1, text2, row]);

  const side = createNode('div', 'dummy-ts-panel dummy-ts-side');

  const stat1 = createNode('div', 'dummy-ts-stat');
  append(stat1, [
    createNode('div', 'dummy-ts-stat-label', 'Nama Brand'),
    createNode('div', 'dummy-ts-stat-value', APP_CONFIG.title),
  ]);

  const stat2 = createNode('div', 'dummy-ts-stat');
  append(stat2, [
    createNode('div', 'dummy-ts-stat-label', 'Tipe File'),
    createNode('div', 'dummy-ts-stat-value', 'Dummy TS'),
  ]);

  const stat3 = createNode('div', 'dummy-ts-stat');
  append(stat3, [
    createNode('div', 'dummy-ts-stat-label', 'Target Size'),
    createNode('div', 'dummy-ts-stat-value', APP_CONFIG.size),
  ]);

  append(side, [stat1, stat2, stat3]);
  append(hero, [copy, side]);

  const features = createNode('section', 'dummy-ts-features');
  features.id = 'detail';

  FEATURE_CARDS.forEach((item: FeatureItem) => {{
    features.appendChild(buildFeatureCard(item));
  }});

  const footer = createNode('div', 'dummy-ts-footer');
  footer.appendChild(document.createTextNode('Dibuat otomatis oleh generator dummy file untuk '));
  const code1 = createNode('span', 'dummy-ts-code', APP_CONFIG.title);
  const middle = document.createTextNode(' • Label ukuran: ');
  const code2 = createNode('span', 'dummy-ts-code', APP_CONFIG.size);
  append(footer, [code1, middle, code2]);

  append(wrap, [nav, hero, features, footer]);

  while (document.body.firstChild) {{
    document.body.removeChild(document.body.firstChild);
  }}
  document.body.appendChild(wrap);
}}

function boot(): void {{
  if (typeof document === 'undefined') return;

  if (document.readyState === 'loading') {{
    document.addEventListener('DOMContentLoaded', renderApp, {{ once: true }});
  }} else {{
    renderApp();
  }}

  if (typeof console !== 'undefined' && typeof console.log === 'function') {{
    console.log(APP_CONFIG.title + ' | ' + APP_CONFIG.type + ' | ' + APP_CONFIG.size);
    console.log(APP_CONFIG.description);
    console.log('Features: ' + APP_CONFIG.features.join(', '));
  }}
}}

boot();
"""


def pad_ts_to_size(ts_text: str, target_bytes: int) -> bytes:
    base = ts_text.encode("utf-8")
    base_len = len(base)
    if base_len > target_bytes:
        raise ValueError(
            f"Base TS ({base_len} bytes) sudah lebih besar dari target ({target_bytes} bytes). "
            "Kurangi konten template atau naikkan target size."
        )

    comment_open = "\n/* PAD:"
    comment_close = "*/"
    overhead = len((comment_open + comment_close).encode("utf-8"))
    diff = target_bytes - base_len

    if diff == 0:
        return base

    if diff < overhead:
        return base + (" " * diff).encode("utf-8")

    pad_len = diff - overhead
    padding = "X" * pad_len
    padded = ts_text + comment_open + padding + comment_close
    data = padded.encode("utf-8")

    actual = len(data)
    remain = target_bytes - actual
    if remain > 0:
        insert = "X" * remain
        padded = ts_text + comment_open + padding + insert + comment_close
        data = padded.encode("utf-8")
    elif remain < 0:
        padding = padding[:remain]
        padded = ts_text + comment_open + padding + comment_close
        data = padded.encode("utf-8")

    return data[:target_bytes]


def main():
    parser = argparse.ArgumentParser(description="Generate dummy TS ukuran presisi.")
    parser.add_argument(
        "--sizes",
        type=str,
        default=None,
        help="Comma-separated ukuran, misal '10kb,1mb'. Default: 10 varian ukuran umum TS mulai 10KB sampai 2MB.",
    )
    parser.add_argument("--outdir", type=str, default=".", help="Folder output.")
    parser.add_argument(
        "--prefix", type=str, default="Contohnya-TS", help="Prefix nama file output."
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
        ts_text = build_base_ts(format_label(label))
        base_bytes = len(ts_text.encode("utf-8"))
        if base_bytes > size:
            print(f"{label:>8} -> SKIP, base TS ({base_bytes} bytes) > target ({size} bytes)")
            continue
        padded = pad_ts_to_size(ts_text, size)
        out_path = os.path.join(args.outdir, f"{args.prefix}-{format_label(label)}.ts")
        with open(out_path, "wb") as f:
            f.write(padded)
        actual = os.path.getsize(out_path)
        status = "OK" if actual == size else f"MELESET ({actual} bytes)"
        print(f"{label:>8} -> {out_path} [{actual} bytes] {status}")


if __name__ == "__main__":
    main()
