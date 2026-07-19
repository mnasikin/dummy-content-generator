# generate-dummy-rar

Script Python buat generate dummy file RAR (.rar) berukuran mendekati target untuk keperluan testing upload/extract.

Isinya beneran ada data:
- README.txt (nyebutin contohnya.web.id + ukuran target)
- 1 atau lebih file data/dummy-N.bin (random bytes) - buat size gede, otomatis dipecah jadi multi item

## !!! PENTING SOAL LISENSI !!!

RAR itu format PROPRIETARY (bukan open-source). Script ini manggil binary `rar` resmi dari RARLAB/WinRAR via command line, BUKAN library open-source (karena emang gak ada library open-source yang bisa BIKIN file RAR, cuma ada yang bisa baca/extract). Binary `rar` itu shareware: gratis dipakai 40 hari, setelah itu WAJIB beli lisensi buat lanjut pakai secara legal - apalagi untuk pemakaian di situs publik/komersial yang generate banyak file terus-menerus. Ini keputusan bisnis/risiko lo sendiri; script ini cuma alat teknisnya, bukan pengganti keputusan soal lisensi.

## CATATAN soal presisi ukuran

Dipakai mode STORE (-m0, gak dikompres), jadi random bytes gak berubah signifikan ukurannya - overhead RAR-nya kecil dan predictable, mirip ZIP.

## Requirements

- Python 3.8+
- binary `rar` (BUKAN unrar) harus ada di PATH

## Install

### 1. Install Python

Jika belum ada Python 3.8+, install dari https://www.python.org/downloads/

### 2. Install binary `rar`

**Ubuntu/Debian:**
```bash
sudo apt install rar   # dari repo multiverse
```

**macOS:**
```bash
brew install rar
```

**Windows:**
Download dari https://www.rarlab.com/download.htm dan install. Pastikan `rar` ada di PATH.

### 3. (Opsional) Setup virtual environment untuk Python

```bash
python3 -m venv venv
source venv/bin/activate
```

## Cara cek apakah sudah siap semua

```bash
# Cek Python version
python3 --version

# Cek apakah binary rar sudah terinstall
rar --version
```

## Usage

```bash
# generate 10 varian ukuran default (10KB s/d 100MB)
python3 generate_dummy_rar.py

# generate ukuran tertentu aja
python3 generate_dummy_rar.py --sizes 10kb,5mb

# ukuran custom yang gak ada di default
python3 generate_dummy_rar.py --sizes 250kb,2.5mb,777kb

# ganti folder output
python3 generate_dummy_rar.py --outdir ./rar

# ganti prefix nama file (default: Contohnya-RAR)
python3 generate_dummy_rar.py --prefix MyFile

# ganti ukuran maks per file .bin di dalam arsip sebelum dipecah jadi item baru (default: 20mb)
python3 generate_dummy_rar.py --chunk-cap 10mb

# pakai definisi binary (1 MB = 1024x1024 bytes / MiB) instead of decimal (default)
python3 generate_dummy_rar.py --sizes 100mb --binary
```

### Ukuran default

`10KB, 50KB, 100KB, 500KB, 1MB, 5MB, 10MB, 25MB, 50MB, 100MB`

Nama file output ikut pattern `{prefix}-{ukuran}.rar`, misal `Contohnya-RAR-10KB.rar`, `Contohnya-RAR-100MB.rar`.

### Decimal vs Binary

Default script ini pakai definisi **decimal** (1 KB = 1.000 bytes, 1 MB = 1.000.000 bytes), sesuai gimana kebanyakan file manager/browser/dashboard cloud storage (R2, S3, dll) nampilin ukuran file. Kalau butuh definisi **binary/KiB-MiB** (1 KB = 1024 bytes), pakai flag `--binary`.

### Chunk Cap

Parameter `--chunk-cap` mengontrol ukuran maksimum per file .bin di dalam arsip sebelum dipecah jadi item baru. Default: 20MB.

- Untuk file kecil (misal 10KB), hanya akan ada 1 file .bin
- Untuk file besar (misal 100MB dengan chunk-cap 20MB), akan ada 5 file .bin (20MB + 20MB + 20MB + 20MB + 20MB)

Ini berguna untuk menghindari pembuatan file .bin yang terlalu besar di dalam arsip.

### Cara kerja

1. Script Python membuat file README.txt dan beberapa file .bin di temporary directory
2. Script memanggil binary `rar` dengan mode STORE (-m0) untuk mengompres tanpa kompresi
3. Script menghitung overhead RAR dan koreksi iteratif (biasanya hanya 1-2 attempt)
4. Overhead biasanya kecil dan predictable karena mode STORE tidak mengubah ukuran data

### Presisi ukuran

RAR ini bisa mendekati target ukuran dengan error kecil (biasanya < 1%), karena:
- Mode STORE (-m0) tidak mengubah ukuran data
- Random bytes gak berubah signifikan ukurannya
- Overhead RAR kecil dan predictable
- Koreksi biasanya kelar dalam 1-2 attempt

### Struktur isi RAR

```
Contohnya-RAR-1MB/
└── tmp/
    └── tmpxxxxxxxx/
        ├── readme.txt
        └── data/
            └── dummy-1.bin
```

Isi readme.txt:
```
Dummy RAR Archive - contohnya.web.id
Ukuran target: 10KB
File ini dibuat untuk keperluan testing upload, extract, dan kompresi.
```

### Customization

Bisa ubah teks di README.txt dengan mengedit bagian ini di script:

```python
SITE_MENTION = "contohnya.web.id"
README_TEMPLATE = (
    "Dummy RAR Archive - {site}\n"
    "Ukuran target: {label}\n"
    "File ini dibuat untuk keperluan testing upload, extract, dan kompresi.\n"
)
```

## Uninstall

Hapus virtual environment jika digunakan:

```bash
rm -rf venv
```

Hapus binary rar:

```bash
# Ubuntu/Debian
sudo apt remove rar

# macOS
brew uninstall rar

# Windows
Hapus folder instalasi rar dari Program Files
```

## Disclaimer

Kode di repo ini dibuat dengan bantuan **Claude Sonnet 5** (Anthropic).

## License

MIT