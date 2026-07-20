# generate-dummy-sqlite

Script Python buat generate dummy SQLite database (.sqlite) buat testing upload/import database.

Isinya tabel + banyak row dummy, dengan mention contohnya.web.id secara berkala.

**PENTING:**
- SQLite database asli TIDAK bisa byte-exact bebas seperti file teks.
- Ukuran file SQLite selalu kelipatan page_size.
- Jadi script ini akan membuat file SQLite VALID dengan ukuran "target atau lebih besar sedikit", bukan presisi 1 byte.

Kalau butuh byte-exact, pakai .sql dump, bukan .sqlite.

Gak butuh dependency eksternal, cuma Python standard library.

## Requirements

- Python 3.8+
- Tidak butuh library eksternal (hanya Python standard library)

## Install

### Opsi 1 — langsung ke sistem

Di distro Linux modern (Debian/Ubuntu terbaru dkk), `pip install` biasanya akan ke-block sama proteksi `externally-managed-environment`. Tapi buat SQLite generator ini gak butuh pip, jadi langsung bisa dipakai:

```bash
python3 generate_dummy_sqlite.py
```

### Opsi 2 — virtual environment (lebih direkomendasikan)

```bash
python3 -m venv venv
source venv/bin/activate
# Tidak perlu install apapun, script ini pakai Python standard library
```

Tiap mau pakai lagi, aktifin dulu venv-nya: `source venv/bin/activate`.

## Usage

```bash
# generate 10 varian ukuran default (10KB s/d 25MB)
python3 generate_dummy_sqlite.py

# generate ukuran tertentu aja
python3 generate_dummy_sqlite.py --sizes 10kb,5mb,25mb

# ukuran custom yang gak ada di default
python3 generate_dummy_sqlite.py --sizes 250kb,2.5mb,777kb

# ganti folder output
python3 generate_dummy_sqlite.py --outdir ./sqlite

# ganti prefix nama file (default: Contohnya-SQLITE)
python3 generate_dummy_sqlite.py --prefix MyFile

# pakai definisi binary (1 MB = 1024x1024 bytes) instead of decimal (default)
python3 generate_dummy_sqlite.py --sizes 25mb --binary
```

### Ukuran default

`10KB, 25KB, 50KB, 100KB, 250KB, 500KB, 1MB, 5MB, 10MB, 25MB`

Nama file output ikut pattern `{prefix}-{ukuran}.sqlite`, misal `Contohnya-SQLITE-10KB.sqlite`, `Contohnya-SQLITE-25MB.sqlite`.

### Decimal vs Binary

Default script ini pakai definisi **decimal** (1 KB = 1.000 bytes, 1 MB = 1.000.000 bytes), sesuai gimana kebanyakan file manager/browser/dashboard cloud storage (R2, S3, dll) nampilin ukuran file. Kalau butuh definisi **binary/KiB-MiB** (1 KB = 1024 bytes), pakai flag `--binary`.

### Kustomisasi teks di dalam database

Edit variabel ini di bagian atas file `generate_dummy_sqlite.py`:

```python
SITE_MENTION = "contohnya.web.id"
MENTION_EVERY_N_ROWS = 5  # kolom "sumber" nyebutin site tiap N baris
TABLE_NAME = "dummy_data"
```

### Struktur Tabel

Default script membuat tabel dengan struktur:
- `id` (INTEGER PRIMARY KEY) — auto-increment
- `keterangan` (TEXT NOT NULL) — teks dummy
- `sumber` (TEXT NOT NULL) — "contohnya.web.id" atau "-" (setiap N baris)

### Filler Table

Script juga membuat tabel `filler_data` untuk menambahkan BLOB data dummy untuk mengisi sisa space sampai mendekati target ukuran.

## Uninstall

Tidak perlu uninstall apapun karena script ini gak butuh library eksternal. Cukup hapus foldernya kalau mau:

```bash
rm -rf venv
```

## Cara kerja (singkat)

1. Bikin database SQLite dengan page_size=512
2. Buat tabel dummy_data dan filler_data
3. Loop buat INSERT INTO statement sampai mendekati target bytes
4. Pakai BLOB data di filler_data untuk mengisi sisa space
5. Ukuran file selalu kelipatan page_size (512 bytes)

## Presisi ukuran

SQLite database ini **tidak bisa byte-exact 100%** karena:
- Format database biner (bukan teks)
- Ukuran file selalu kelipatan page_size (default 512 bytes)
- Script akan membuat file dengan ukuran "target atau lebih besar sedikit"

Status output akan menunjukkan:
- `EXACT` — ukuran pas target (jarang terjadi karena page_size)
- `VALID (rounded to page size X)` — ukuran dibulatkan ke kelipatan page_size
- `VALID (overshoot X bytes)` — ukuran sedikit lebih besar dari target
- `KURANG (X bytes)` — ukuran kurang dari target (jarang terjadi)

## Presisi vs SQL Dump

Kalau butuh byte-exact 100%, gunakan generate_dummy_sql.py (SQL dump) bukan generate_dummy_sqlite.py (SQLite database). SQL dump bisa byte-exact karena format teks murni, sedangkan SQLite database tidak bisa karena format biner dan page_size constraints.

## Disclaimer

Kode di repo ini dibuat dengan bantuan **Claude Sonnet 5** (Anthropic).

## License

MIT