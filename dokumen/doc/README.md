# generate-dummy-doc

Script Python buat generate dummy Word document (.doc, format binary Word 97-2003) berukuran mendekati target untuk keperluan testing upload/parsing dokumen legacy.

.doc itu format binary (OLE Compound File), BEDA TOTAL dari .docx (yang XML+ZIP) - gak bisa di-hand-craft/padding manual kayak PDF/CSV/DOCX. Strateginya: generate .docx dulu (pakai mesin yang sama kayak generate_dummy_docx.py), terus CONVERT ke .doc pakai LibreOffice headless (`soffice --convert-to doc`).

## KETERBATASAN PENTING

- Ukuran akhir .doc BISA BEDA dari .docx sumbernya (kadang lebih kecil, kadang lebih besar), karena format binary punya karakteristik encoding beda dari ZIP+XML. Jadi ini approximate, bukan presisi.
- Proses convert lewat LibreOffice itu lumayan lambat (bukan operasi instant kayak nulis file biasa), apalagi kalau dipanggil berkali-kali buat banyak ukuran. Sabar aja pas nunggu.

## Requirements

- Python 3.8+
- Node.js + npm package `docx` (npm install docx) - buat generate .docx dulu
- LibreOffice (`soffice` harus ada di PATH) - buat convert ke .doc

## Install

### 1. Install Node.js dan npm

Jika belum ada Node.js, install dari https://nodejs.org/

### 2. Install docx package

Di folder dokumen/doc, jalankan:

```bash
npm install docx
```

### 3. Install LibreOffice

**Ubuntu/Debian:**
```bash
sudo apt install libreoffice
```

**Kalo mau lebih ringan, cukup komponen writer-nya doang:**
```bash
sudo apt install libreoffice-writer
```

**macOS:**
```bash
brew install --cask libreoffice
```

**Windows:**
Download dari https://www.libreoffice.org/download/download/

### 4. Pastikan build_docx.js ada

Script ini membutuhkan file `build_docx.js` yang ada di folder yang sama. File ini sudah disertakan di repo ini.

### 5. (Opsional) Setup virtual environment untuk Python

```bash
python3 -m venv venv
source venv/bin/activate
```

## Cara cek apakah sudah siap semua

```bash
# Cek Node.js dan docx package
node -e "require('docx')"   # gak boleh error

# Cek LibreOffice
which soffice                # harus nunjukkin path, bukan kosong
```

Kalo `which soffice` kosong (gak ketemu), berarti LibreOffice belom keinstall atau belom masuk PATH. Kalo `node -e "require('docx')"` error, berarti `npm install docx` belom jalan di folder itu.

## Usage

```bash
# generate 10 varian ukuran default (10KB s/d 50MB)
python3 generate_dummy_doc.py

# generate ukuran tertentu aja
python3 generate_dummy_doc.py --sizes 10kb,5mb

# ukuran custom yang gak ada di default
python3 generate_dummy_doc.py --sizes 250kb,2.5mb,777kb

# ganti folder output
python3 generate_dummy_doc.py --outdir ./doc

# ganti prefix nama file (default: Contohnya-DOC)
python3 generate_dummy_doc.py --prefix MyFile

# pakai definisi binary (1 MB = 1024x1024 bytes / MiB) instead of decimal (default)
python3 generate_dummy_doc.py --sizes 100mb --binary
```

### Ukuran default

`10KB, 50KB, 100KB, 500KB, 1MB, 5MB, 10MB, 20MB, 35MB, 50MB`

Nama file output ikut pattern `{prefix}-{ukuran}.doc`, misal `Contohnya-DOC-10KB.doc`, `Contohnya-DOC-50MB.doc`.

### Decimal vs Binary

Default script ini pakai definisi **decimal** (1 KB = 1.000 bytes, 1 MB = 1.000.000 bytes), sesuai gimana kebanyakan file manager/browser/dashboard cloud storage (R2, S3, dll) nampilin ukuran file. Kalau butuh definisi **binary/KiB-MiB** (1 KB = 1024 bytes), pakai flag `--binary`.

### Cara kerja

1. Script Python memanggil Node.js script (build_docx.js) untuk generate DOCX
2. Node.js script menggunakan library `docx` untuk membuat document
3. Script Python convert DOCX ke DOC menggunakan LibreOffice headless
4. Jika ukuran hasil convert masih jauh dari target, script melakukan koreksi iteratif
5. Untuk target besar, teks per paragraf dibuat lebih panjang (bukan nambah jumlah paragraf tanpa batas) untuk menghindari OOM (Out of Memory) di Node.js

### Presisi ukuran

DOC ini bisa mendekati target ukuran dengan error kecil (biasanya <10%), tapi gak bisa byte-exact 100% karena:
- Format binary .doc punya struktur encoding beda dari ZIP+XML
- Rasio konversi docx->doc itu GAK konsisten antar ukuran (kadang 1.6x, kadang 3.3x)
- LibreOffice convert juga punya overhead dan optimasi sendiri

## Perbedaan dengan .docx Generator

Generator ini lebih "berat" dari generate_dummy_docx.py karena butuh 3 tools sekaligus:
1. Python (untuk orchestration)
2. Node.js + docx package (untuk generate .docx)
3. LibreOffice (untuk convert ke .doc)

**Kenapa butuh LibreOffice?**
- .docx generator (`generate_dummy_docx.py`) sudah cukup jika cuma butuh file .docx
- .doc generator ini butuh LibreOffice untuk convert .docx → .doc (format binary legacy)

**Jika cuma butuh .docx:**
- Pakai `generate_dummy_docx.py` yang lebih ringan dependency-nya
- Tidak perlu install LibreOffice

## Uninstall

Hapus package docx jika tidak butuh lagi:

```bash
npm uninstall docx
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