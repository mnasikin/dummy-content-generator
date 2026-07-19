# generate-dummy-xls

Script Python buat generate dummy Excel spreadsheet (.xls, format binary Excel 97-2003) berukuran mendekati target untuk keperluan testing upload/parsing spreadsheet legacy.

.xls itu format binary (BIFF/OLE Compound File), BEDA TOTAL dari .xlsx (yang XML+ZIP) - gak bisa di-hand-craft/padding manual. Strateginya: generate .xlsx dulu (pakai openpyxl, mesin yang sama kayak generate_dummy_xlsx.py), terus CONVERT ke .xls pakai LibreOffice headless (`soffice --convert-to xls`).

## KETERBATASAN PENTING

- Ukuran akhir .xls BISA JAUH LEBIH GEDE dari .xlsx sumbernya (rasio ~2-3x dari observasi, tapi GAK konsisten antar ukuran), karena format binary lama gak punya kompresi kayak ZIP. Jadi ini approximate, bukan presisi - script ini ukur rasio spesifik per target dan koreksi sekali.
- Proses convert lewat LibreOffice itu lumayan lambat, apalagi buat file gede. Sabar aja pas nunggu, dan timeout udah dinaikkan ke 600 detik biar aman buat file besar.

## Requirements

- Python 3.8+
- Python package `openpyxl` (pip install openpyxl --break-system-packages)
- LibreOffice (`soffice` harus ada di PATH)

## Install

### 1. Install Python package openpyxl

```bash
pip install openpyxl --break-system-packages
```

### 2. Install LibreOffice

**Ubuntu/Debian:**
```bash
sudo apt install libreoffice
```

**Kalo mau lebih ringan, cukup komponen calc-nya doang:**
```bash
sudo apt install libreoffice-calc
```

**macOS:**
```bash
brew install --cask libreoffice
```

**Windows:**
Download dari https://www.libreoffice.org/download/download/

### 3. (Opsional) Setup virtual environment untuk Python

```bash
python3 -m venv venv
source venv/bin/activate
```

## Cara cek apakah sudah siap semua

```bash
# Cek Python package openpyxl
python3 -c "import openpyxl; print(openpyxl.__version__)"

# Cek LibreOffice
which soffice                # harus nunjukkin path, bukan kosong
```

Kalo `which soffice` kosong (gak ketemu), berarti LibreOffice belom keinstall atau belom masuk PATH. Kalo `python3 -c "import openpyxl"` error, berarti package openpyxl belom keinstall.

## Usage

```bash
# generate 10 varian ukuran default (10KB s/d 50MB)
python3 generate_dummy_xls.py

# generate ukuran tertentu aja
python3 generate_dummy_xls.py --sizes 10kb,5mb

# ukuran custom yang gak ada di default
python3 generate_dummy_xls.py --sizes 250kb,2.5mb,777kb

# ganti folder output
python3 generate_dummy_xls.py --outdir ./xls

# ganti prefix nama file (default: Contohnya-XLS-Legacy)
python3 generate_dummy_xls.py --prefix MyFile

# pakai definisi binary (1 MB = 1024x1024 bytes / MiB) instead of decimal (default)
python3 generate_dummy_xls.py --sizes 100mb --binary
```

### Ukuran default

`10KB, 50KB, 100KB, 500KB, 1MB, 5MB, 10MB, 20MB, 35MB, 50MB`

Nama file output ikut pattern `{prefix}-{ukuran}.xls`, misal `Contohnya-XLS-Legacy-10KB.xls`, `Contohnya-XLS-Legacy-50MB.xls`.

### Decimal vs Binary

Default script ini pakai definisi **decimal** (1 KB = 1.000 bytes, 1 MB = 1.000.000 bytes), sesuai gimana kebanyakan file manager/browser/dashboard cloud storage (R2, S3, dll) nampilin ukuran file. Kalau butuh definisi **binary/KiB-MiB** (1 KB = 1024 bytes), pakai flag `--binary`.

### Cara kerja

1. Script Python generate XLSX pakai openpyxl
2. Script Python convert XLSX ke XLS menggunakan LibreOffice headless
3. Jika ukuran hasil convert masih jauh dari target, script melakukan koreksi iteratif
4. Timeout untuk convert sudah dinaikkan ke 600 detik untuk file besar

### Presisi ukuran

XLS ini bisa mendekati target ukuran dengan error kecil (biasanya <10%), tapi gak bisa byte-exact 100% karena:
- Format binary .xls punya struktur encoding beda dari ZIP+XML
- Rasio konversi xlsx->xls itu GAK konsisten antar ukuran (kadang 2x, kadang 3x)
- LibreOffice convert juga punya overhead dan optimasi sendiri

## Perbedaan dengan .xlsx Generator

Generator ini lebih "berat" dari generate_dummy_xlsx.py karena butuh 2 tools sekaligus:
1. Python (untuk orchestration)
2. LibreOffice (untuk convert xlsx → xls)

**Kenapa butuh LibreOffice?**
- .xlsx generator (`generate_dummy_xlsx.py`) sudah cukup jika cuma butuh file .xlsx
- .xls generator ini butuh LibreOffice untuk convert xlsx → xls (format binary legacy)

**Jika cuma butuh .xlsx:**
- Pakai `generate_dummy_xlsx.py` yang lebih ringan dependency-nya
- Tidak perlu install LibreOffice

## Uninstall

Hapus package openpyxl jika tidak butuh lagi:

```bash
pip uninstall openpyxl
```

Hapus LibreOffice jika tidak butuh lagi:

```bash
# Ubuntu/Debian
sudo apt remove --purge libreoffice

# macOS
brew uninstall --cask libreoffice
```

Hapus virtual environment jika digunakan:

```bash
rm -rf venv
```

## Disclaimer

Kode di repo ini dibuat dengan bantuan **Claude Sonnet 5** (Anthropic).

## License

MIT