# generate-dummy-docx

Script Python buat generate dummy Word document (.docx) berukuran mendekati target untuk keperluan testing upload/parsing dokumen.

DOCX itu container ZIP terkompresi (mirip XLSX), jadi ukurannya gak linear sempurna terhadap jumlah paragraf - gak bisa byte-exact kayak PDF/CSV/SQL. Strateginya: estimasi jumlah paragraf dari bytes-per-paragraf hasil sample, generate, ukur, koreksi kalau masih jauh.

Generate file DOCX dilakukan lewat docx-js (npm), dipanggil dari script Node kecil (build_docx.js) yang harus ada satu folder sama script ini.

## Requirements

- Python 3.8+
- Node.js (untuk build_docx.js)
- npm package `docx` (harus install dulu)

## Install

### 1. Install Node.js dan npm

Jika belum ada Node.js, install dari https://nodejs.org/

### 2. Install docx package

Di folder dokumen/docx, jalankan:

```bash
npm install docx
```

### 3. Pastikan build_docx.js ada

Script ini membutuhkan file `build_docx.js` yang ada di folder yang sama. File ini sudah disertakan di repo ini.

### 4. (Opsional) Setup virtual environment untuk Python

```bash
python3 -m venv venv
source venv/bin/activate
```

## Usage

```bash
# generate 10 varian ukuran default (10KB s/d 50MB)
python3 generate_dummy_docx.py

# generate ukuran tertentu aja
python3 generate_dummy_docx.py --sizes 10kb,5mb

# ukuran custom yang gak ada di default
python3 generate_dummy_docx.py --sizes 250kb,2.5mb,777kb

# ganti folder output
python3 generate_dummy_docx.py --outdir ./docx

# ganti prefix nama file (default: Contohnya-DOCX)
python3 generate_dummy_docx.py --prefix MyFile

# pakai definisi binary (1 MB = 1024x1024 bytes / MiB) instead of decimal (default)
python3 generate_dummy_docx.py --sizes 100mb --binary
```

### Ukuran default

`10KB, 50KB, 100KB, 500KB, 1MB, 5MB, 10MB, 20MB, 35MB, 50MB`

Nama file output ikut pattern `{prefix}-{ukuran}.docx`, misal `Contohnya-DOCX-10KB.docx`, `Contohnya-DOCX-50MB.docx`.

### Decimal vs Binary

Default script ini pakai definisi **decimal** (1 KB = 1.000 bytes, 1 MB = 1.000.000 bytes), sesuai gimana kebanyakan file manager/browser/dashboard cloud storage (R2, S3, dll) nampilin ukuran file. Kalau butuh definisi **binary/KiB-MiB** (1 KB = 1024 bytes), pakai flag `--binary`.

### Cara kerja

1. Script Python memanggil Node.js script (build_docx.js) untuk generate DOCX
2. Node.js script menggunakan library `docx` untuk membuat document
3. Jika ukuran hasil generate masih jauh dari target, script melakukan koreksi iteratif
4. Untuk target besar, teks per paragraf dibuat lebih panjang (bukan nambah jumlah paragraf tanpa batas) untuk menghindari OOM (Out of Memory) di Node.js

### Presisi ukuran

DOCX ini bisa mendekati target ukuran dengan error kecil (biasanya <2%), tapi gak bisa byte-exact 100% karena:
- DOCX adalah ZIP terkompresi
- Struktur internal DOCX kompleks dengan banyak overhead
- Kompresi ZIP tidak deterministik untuk teks yang sama

## Uninstall

Hapus package docx jika tidak butuh lagi:

```bash
npm uninstall docx
```

Hapus virtual environment jika digunakan:

```bash
rm -rf venv
```

## Disclaimer

Kode di repo ini dibuat dengan bantuan **Claude Sonnet 5** (Anthropic).

## License

MIT