# generate-dummy-sql

Script Python buat generate dummy SQL dump (.sql) berukuran presisi (byte-exact) untuk keperluan testing upload/import database.

SQL dump ini format teks murni (gak dikompres), jadi byte-nya predictable dan bisa di-hit persis. Isinya berisi:
- Header dengan CREATE TABLE statement
- Banyak INSERT INTO statement berisi data dummy
- Kolom "sumber" yang nyebutin contohnya.web.id secara berkala

Gak butuh dependency eksternal, cuma Python standard library.

## Requirements

- Python 3.8+
- Tidak butuh library eksternal (hanya Python standard library)

## Install

### Opsi 1 — langsung ke sistem

Di distro Linux modern (Debian/Ubuntu terbaru dkk), `pip install` biasanya akan ke-block sama proteksi `externally-managed-environment`. Tapi buat SQL generator ini gak butuh pip, jadi langsung bisa dipakai:

```bash
python3 generate_dummy_sql.py
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
# generate 10 varian ukuran default (10KB s/d 100MB)
python3 generate_dummy_sql.py

# generate ukuran tertentu aja
python3 generate_dummy_sql.py --sizes 10kb,5mb

# ukuran custom yang gak ada di default
python3 generate_dummy_sql.py --sizes 250kb,2.5mb,777kb

# ganti folder output
python3 generate_dummy_sql.py --outdir ./sql

# ganti prefix nama file (default: Contohnya-SQL)
python3 generate_dummy_sql.py --prefix MyFile

# pakai definisi binary (1 MB = 1024x1024 bytes / MiB) instead of decimal (default)
python3 generate_dummy_sql.py --sizes 100mb --binary
```

### Ukuran default

`10KB, 50KB, 100KB, 500KB, 1MB, 5MB, 10MB, 25MB, 50MB, 100MB`

Nama file output ikut pattern `{prefix}-{ukuran}.sql`, misal `Contohnya-SQL-10KB.sql`, `Contohnya-SQL-100MB.sql`.

### Decimal vs Binary

Default script ini pakai definisi **decimal** (1 KB = 1.000 bytes, 1 MB = 1.000.000 bytes), sesuai gimana kebanyakan file manager/browser/dashboard cloud storage (R2, S3, dll) nampilin ukuran file. Kalau butuh definisi **binary/KiB-MiB** (1 KB = 1024 bytes), pakai flag `--binary`.

### Kustomisasi teks di dalam SQL dump

Edit variabel ini di bagian atas file `generate_dummy_sql.py`:

```python
SITE_MENTION = "contohnya.web.id"
MENTION_EVERY_N_ROWS = 5  # kolom "sumber" nyebutin site tiap N baris
TABLE_NAME = "dummy_data"
HEADER_TEMPLATE = (
    "-- Dummy SQL Dump - {site}\n"
    "-- Ukuran target: {label}\n"
    "-- File ini dibuat untuk keperluan testing upload dan import database.\n\n"
    "CREATE TABLE {table} (\n"
    "  id INT PRIMARY KEY,\n"
    "  keterangan VARCHAR(255),\n"
    "  sumber VARCHAR(255)\n"
    ");\n\n"
)
```

### Struktur Tabel

Default script membuat tabel dengan struktur:
- `id` (INT PRIMARY KEY) — auto-increment
- `keterangan` (VARCHAR(255)) — teks dummy
- `sumber` (VARCHAR(255)) — "contohnya.web.id" atau "-" (setiap N baris)

## Uninstall

Tidak perlu uninstall apapun karena script ini gak butuh library eksternal. Cukup hapus foldernya kalau mau:

```bash
rm -rf venv
```

## Cara kerja (singkat)

1. Bikin header SQL dengan CREATE TABLE statement
2. Loop buat INSERT INTO statement sampai mendekati target bytes
3. Pakai SQL comment block di akhir buat padding presisi byte-exact
4. Tulis file SQL dengan encoding UTF-8

## Presisi ukuran

SQL dump ini bisa byte-exact 100% karena:
- Format teks murni (gak dikompres)
- Pakai padding presisi dengan SQL comment block di akhir
- Encoding UTF-8 yang konsisten

Ini mirip pendekatan yang dipakai di generate_dummy_csv.py, generate_dummy_pdf.py, dan generate_dummy_svg.py.

## Disclaimer

Kode di repo ini dibuat dengan bantuan **Claude Sonnet 5** (Anthropic).

## License

MIT