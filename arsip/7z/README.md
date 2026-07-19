# generate-dummy-7z

Script Python buat generate dummy file 7Z (.7z) berukuran mendekati target untuk keperluan testing upload/extract.

Isinya beneran ada data:
- README.txt (nyebutin contohnya.web.id + ukuran target)
- 1 atau lebih file data/dummy-N.bin (random bytes) - buat size gede, otomatis dipecah jadi multi item

## CATATAN soal presisi ukuran

Sama kayak TAR.GZ, random bytes GAK signifikan kekompres, jadi overhead 7Z-nya kecil dan predictable (biasanya < 1% dari target) - gak perlu iterasi berat.

## Requirements

- Python 3.8+
- py7zr package

## Install

### 1. Install Python

Jika belum ada Python 3.8+, install dari https://www.python.org/downloads/

### 2. Install py7zr package

```bash
pip install py7zr --break-system-packages
```

### 3. (Opsional) Setup virtual environment untuk Python

```bash
python3 -m venv venv
source venv/bin/activate
pip install py7zr --break-system-packages
```

## Cara cek apakah sudah siap semua

```bash
# Cek Python version
python3 --version

# Cek apakah py7zr sudah terinstall
python3 -c "import py7zr; print('py7zr version:', py7zr.__version__)"
```

## Usage

```bash
# generate 10 varian ukuran default (10KB s/d 100MB)
python3 generate_dummy_7z.py

# generate ukuran tertentu aja
python3 generate_dummy_7z.py --sizes 10kb,5mb

# ukuran custom yang gak ada di default
python3 generate_dummy_7z.py --sizes 250kb,2.5mb,777kb

# ganti folder output
python3 generate_dummy_7z.py --outdir ./7z

# ganti prefix nama file (default: Contohnya-7Z)
python3 generate_dummy_7z.py --prefix MyFile

# ganti ukuran maks per file .bin di dalam arsip sebelum dipecah jadi item baru (default: 20mb)
python3 generate_dummy_7z.py --chunk-cap 10mb

# pakai definisi binary (1 MB = 1024x1024 bytes / MiB) instead of decimal (default)
python3 generate_dummy_7z.py --sizes 100mb --binary
```

### Ukuran default

`10KB, 50KB, 100KB, 500KB, 1MB, 5MB, 10MB, 25MB, 50MB, 100MB`

Nama file output ikut pattern `{prefix}-{ukuran}.7z`, misal `Contohnya-7Z-10KB.7z`, `Contohnya-7Z-100MB.7z`.

### Decimal vs Binary

Default script ini pakai definisi **decimal** (1 KB = 1.000 bytes, 1 MB = 1.000.000 bytes), sesuai gimana kebanyakan file manager/browser/dashboard cloud storage (R2, S3, dll) nampilin ukuran file. Kalau butuh definisi **binary/KiB-MiB** (1 KB = 1024 bytes), pakai flag `--binary`.

### Chunk Cap

Parameter `--chunk-cap` mengontrol ukuran maksimum per file .bin di dalam arsip sebelum dipecah jadi item baru. Default: 20MB.

- Untuk file kecil (misal 10KB), hanya akan ada 1 file .bin
- Untuk file besar (misal 100MB dengan chunk-cap 20MB), akan ada 5 file .bin (20MB + 20MB + 20MB + 20MB + 20MB)

Ini berguna untuk menghindari pembuatan file .bin yang terlalu besar di dalam arsip.

### Cara kerja

1. Script Python membuat 7Z dengan file README.txt dan beberapa file .bin
2. File .bin berisi random bytes (data incompressible)
3. Script menghitung overhead 7Z dan koreksi iteratif (biasanya hanya 1-2 attempt)
4. Overhead biasanya < 1% dari target karena random data gak signifikan kekompres

### Presisi ukuran

7Z ini bisa mendekati target ukuran dengan error kecil (biasanya < 1%), karena:
- Random bytes gak signifikan kekompres (data incompressible)
- Overhead 7Z kecil dan predictable
- Koreksi biasanya kelar dalam 1-2 attempt

### Struktur isi 7Z

```
dummy-10KB.7z
├── README.txt
└── data/
    ├── dummy-1.bin
    └── dummy-2.bin
```

Isi README.txt:
```
Dummy 7Z Archive - contohnya.web.id
Ukuran target: 10KB
File ini dibuat untuk keperluan testing upload, extract, dan kompresi.
```

### Customization

Bisa ubah teks di README.txt dengan mengedit bagian ini di script:

```python
SITE_MENTION = "contohnya.web.id"
README_TEMPLATE = (
    "Dummy 7Z Archive - {site}\n"
    "Ukuran target: {label}\n"
    "File ini dibuat untuk keperluan testing upload, extract, dan kompresi.\n"
)
```

## Uninstall

Hapus virtual environment jika digunakan:

```bash
rm -rf venv
```

Hapus py7zr package:

```bash
pip uninstall py7zr
```

## Disclaimer

Kode di repo ini dibuat dengan bantuan **Claude Sonnet 5** (Anthropic).

## License

MIT