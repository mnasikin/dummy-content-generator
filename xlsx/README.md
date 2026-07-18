# generate-dummy-xlsx

Script Python buat generate dummy XLSX berukuran presisi (byte-exact) untuk keperluan testing upload/download, testing batas ukuran file, dan sejenisnya.

File yang dihasilkan tetap XLSX valid (bisa dibuka di Excel mana pun, bukan cuma file random bytes yang dipaksa berekstensi `.xlsx`), dan isinya beneran multi-sheet (bukan cuma 1 sheet + padding tersembunyi) — jumlah sheet menyesuaikan besar target ukuran.

## Requirements

- Python 3.8+
- [openpyxl](https://pypi.org/project/openpyxl/)

## Install

### Opsi 1 — langsung ke sistem

Di distro Linux modern (Debian/Ubuntu terbaru dkk), `pip install` biasa bakal ke-block sama proteksi `externally-managed-environment`. Tambahin flag `--break-system-packages`:

```bash
pip install openpyxl --break-system-packages
```

### Opsi 2 — virtual environment (lebih direkomendasikan)

```bash
python3 -m venv venv
source venv/bin/activate
pip install openpyxl
```

Tiap mau pakai lagi, aktifin dulu venv-nya: `source venv/bin/activate`.

## Usage

```bash
# generate semua ukuran default (1KB s/d 100MB)
python3 generate_dummy_xlsx.py

# generate ukuran tertentu aja
python3 generate_dummy_xlsx.py --sizes 1kb,50kb,10mb

# ukuran custom yang gak ada di default
python3 generate_dummy_xlsx.py --sizes 250kb,2.5mb,777kb

# ganti folder output
python3 generate_dummy_xlsx.py --outdir ./xlsx

# ganti prefix nama file (default: Contohnya-XLSX)
python3 generate_dummy_xlsx.py --prefix MyFile

# pakai definisi binary (1 MB = 1024x1024 bytes / MiB) instead of decimal (default)
python3 generate_dummy_xlsx.py --sizes 100mb --binary
```

### Ukuran default

`1KB, 50KB, 100KB, 500KB, 1MB, 5MB, 10MB, 50MB, 100MB`

Nama file output ikut pattern `{prefix}-{ukuran}.xlsx`, misal `Contohnya-XLSX-1KB.xlsx`, `Contohnya-XLSX-10MB.xlsx`.

### Decimal vs Binary

Default script ini pakai definisi **decimal** (1 KB = 1.000 bytes, 1 MB = 1.000.000 bytes), sesuai gimana kebanyakan file manager/browser/dashboard cloud storage (R2, S3, dll) nampilin ukuran file. Kalau butuh definisi **binary/KiB-MiB** (1 KB = 1024 bytes), pakai flag `--binary`.

### Kustomisasi teks di dalam XLSX

Edit langsung dua variabel ini di bagian atas file `generate_dummy_xlsx.py`:

```python
XLSX_TITLE = "Contoh File XLSX - Contohnya.web.id"
XLSX_SUBTITLE = "Dummy file untuk testing"
```

## Uninstall

```bash
pip uninstall openpyxl --break-system-packages
```

Kalau pakai virtual environment, cukup hapus foldernya:

```bash
rm -rf venv
```

## Cara kerja (singkat)

1. Bikin base XLSX valid berisi konten teks asli (judul, subjudul, nomor sheet, baris dummy) — jumlah sheet menyesuaikan besar target (makin gede target, makin banyak sheet, dicap di 500 sheet).
2. Kalau masih ada sisa gap ke ukuran target, ditambahin extra data berisi **random bytes** (bukan byte berulang, karena byte berulang gampang kekompres) sebagai padding.
3. Disimpan dengan compression disabled supaya padding-nya gak ikut dikompres ulang dan ukuran akhir tetap presisi byte-exact.

## Disclaimer

Kode di repo ini dibuat dengan bantuan **Claude Sonnet 5** (Anthropic).

## License

MIT