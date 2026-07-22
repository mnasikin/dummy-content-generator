# generate-dummy-rtf

Script Python buat generate dummy file RTF (.rtf) untuk testing upload, preview, dan size validation.

Karakter:
- Output valid Rich Text Format (.rtf), bukan file rename extension
- Isinya aman, statis, dan harmless
- Ukuran file diusahakan mendekati target dengan filler text RTF yang valid
- Support custom variant size lewat parameter CLI

Catatan:
- Karena RTF itu text-based, script ini bisa bikin ukuran sangat presisi
- Tidak butuh dependency eksternal

## Requirements

- Python 3.8+

## Install

### Python

Tidak perlu install apapun, cuma butuh Python 3.8+ yang terinstall di sistem.

## Usage

```bash
# generate 10 varian ukuran default (10KB s.d 10MB)
python3 generate_dummy_rtf.py

# generate ukuran tertentu aja
python3 generate_dummy_rtf.py --sizes 10kb,25kb,50kb,100kb,250kb

# ukuran custom yang gak ada di default
python3 generate_dummy_rtf.py --sizes 1mb,2mb,5mb,10mb

# ganti folder output
python3 generate_dummy_rtf.py --outdir ./rtf

# ganti prefix nama file (default: Contohnya-RTF)
python3 generate_dummy_rtf.py --prefix MyDocument

# ganti judul dokumen di dalam file RTF (default: contohnya.web.id)
python3 generate_dummy_rtf.py --title "My Document Title"

# ganti keterangan/subjudul di dalam file RTF (default: dummy file for testing)
python3 generate_dummy_rtf.py --note "Testing upload validation"

# ganti jumlah varian default (default: 10)
python3 generate_dummy_rtf.py --count 5

# ganti batas size terbesar (default: 10mb)
python3 generate_dummy_rtf.py --max-size 5mb

# pakai definisi binary (1 MB = 1024x1024 bytes) instead of decimal (default)
python3 generate_dummy_rtf.py --sizes 10mb --binary
```

### Ukuran default

`10KB, 25KB, 50KB, 100KB, 250KB, 500KB, 1MB, 2MB, 5MB, 10MB`

Nama file output ikut pattern `{prefix}-{label}.rtf`, misal `Contohnya-RTF-10kb.rtf`, `Contohnya-RTF-10mb.rtf`.

### Decimal vs Binary

Default script ini pakai definisi **decimal** (1 KB = 1.000 bytes, 1 MB = 1.000.000 bytes), sesuai gimana kebanyakan file manager/browser/dashboard cloud storage (R2, S3, dll) nampilin ukuran file. Kalau butuh definisi **binary/KiB-MiB** (1 KB = 1024 bytes), pakai flag `--binary`.

### Cara kerja (singkat)

1. Build header RTF dengan font, color table, dan teks judul/keterangan
2. Generate filler block dengan paragraf berulang yang berisi dummy content
3. Tambahkan padding content untuk tuning ukuran
4. Tambahkan footer RTF
5. Hitung ukuran file RTF hasil, kalau deviasi > 256 bytes, adjust padding

### Struktur RTF

**Header:**
- Font table: Arial dan Courier New
- Color table: 4 warna (gray, blue, dark gray)
- Font size: 32pt untuk judul, 22pt untuk teks, 20pt untuk field
- Margins: 180 twips (sa), 120 twips (li)

**Content:**
- Judul dokumen dengan bold
- Keterangan/subjudul dengan italic
- Footer dengan teks keterangan
- Filler block dengan paragraf berulang
- Field sample: name, type, status, mode, purpose

**Formatting:**
- Bold: \\b
- Italic: \\i
- Underline: \\ul
- Paragraph: \\par
- Line spacing: 240 twips (sl)
- Paragraph spacing: 120 twips (sa)

### Presisi ukuran

RTF bisa sangat presisi karena:
- Text-based format
- Tidak ada kompresi
- Tidak ada overhead kompleks
- Bisa adjust dengan padding content

Toleransi: 256 bytes (sekitar 1-2 paragraf)

### Keamanan

Script ini sengaja dibuat aman:
- Tidak ada network access
- Tidak ada file I/O yang berbahaya
- Hanya generate text data yang aman
- Cocok untuk testing upload manager, file browser, MIME detection, dan validasi ukuran file

## Uninstall

Tidak perlu uninstall apapun, karena gak ada dependency eksternal.

## Disclaimer

Kode di repo ini dibuat dengan bantuan **Claude Sonnet 5** (Anthropic).

## License

MIT