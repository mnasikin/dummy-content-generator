# generate-dummy-pdf

Script Python buat generate dummy PDF berukuran presisi (byte-exact) untuk keperluan testing upload/download, testing batas ukuran file, dan sejenisnya.

File yang dihasilkan tetap PDF valid (bisa dibuka di reader mana pun, bukan cuma file random bytes yang dipaksa berekstensi `.pdf`), dan isinya beneran multi-halaman (bukan cuma 1 halaman + padding tersembunyi) — jumlah halaman menyesuaikan besar target ukuran.

## Requirements

- Python 3.8+
- [pikepdf](https://pypi.org/project/pikepdf/)
- [reportlab](https://pypi.org/project/reportlab/)

## Install

### Opsi 1 — langsung ke sistem

Di distro Linux modern (Debian/Ubuntu terbaru dkk), `pip install` biasa bakal ke-block sama proteksi `externally-managed-environment`. Tambahin flag `--break-system-packages`:

```bash
pip install pikepdf reportlab --break-system-packages
```

### Opsi 2 — virtual environment (lebih direkomendasikan)

```bash
python3 -m venv venv
source venv/bin/activate
pip install pikepdf reportlab
```

Tiap mau pakai lagi, aktifin dulu venv-nya: `source venv/bin/activate`.

## Usage

```bash
# generate semua ukuran default (1KB s/d 100MB)
python3 generate_dummy_pdf.py

# generate ukuran tertentu aja
python3 generate_dummy_pdf.py --sizes 1kb,50kb,10mb

# ukuran custom yang gak ada di default
python3 generate_dummy_pdf.py --sizes 250kb,2.5mb,777kb

# ganti folder output
python3 generate_dummy_pdf.py --outdir ./pdf

# ganti prefix nama file (default: Contohnya-PDF)
python3 generate_dummy_pdf.py --prefix MyFile

# pakai definisi binary (1 MB = 1024x1024 bytes / MiB) instead of decimal (default)
python3 generate_dummy_pdf.py --sizes 100mb --binary
```

### Ukuran default

`1KB, 50KB, 100KB, 500KB, 1MB, 5MB, 10MB, 50MB, 100MB`

Nama file output ikut pattern `{prefix}-{ukuran}.pdf`, misal `Contohnya-PDF-1KB.pdf`, `Contohnya-PDF-10MB.pdf`.

### Decimal vs Binary

Default script ini pakai definisi **decimal** (1 KB = 1.000 bytes, 1 MB = 1.000.000 bytes), sesuai gimana kebanyakan file manager/browser/dashboard cloud storage (R2, S3, dll) nampilin ukuran file. Kalau butuh definisi **binary/KiB-MiB** (1 KB = 1024 bytes), pakai flag `--binary`.

### Kustomisasi teks di dalam PDF

Edit langsung dua variabel ini di bagian atas file `generate_dummy_pdf.py`:

```python
PDF_TITLE = "Contoh File PDF - Contohnya.web.id"
PDF_SUBTITLE = "Dummy file untuk testing"
```

## Uninstall

```bash
pip uninstall pikepdf reportlab --break-system-packages
```

Kalau pakai virtual environment, cukup hapus foldernya:

```bash
rm -rf venv
```

## Cara kerja (singkat)

1. Bikin base PDF valid berisi konten teks asli (judul, subjudul, nomor halaman, baris dummy) — jumlah halaman menyesuaikan besar target (makin gede target, makin banyak halaman, dicap di 500 halaman).
2. Kalau masih ada sisa gap ke ukuran target, ditambahin extra stream object berisi **random bytes** (bukan byte berulang, karena byte berulang gampang kekompres) sebagai padding.
3. Disimpan dengan `compress_streams=False` supaya padding-nya gak ikut dikompres ulang dan ukuran akhir tetap presisi byte-exact.

## Disclaimer

Kode di repo ini dibuat dengan bantuan **Claude Sonnet 5** (Anthropic).

## License

MIT
