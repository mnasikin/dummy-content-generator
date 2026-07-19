# generate-dummy-xml

Script Python buat generate dummy file XML berukuran presisi (byte-exact) untuk keperluan testing upload/parsing data terstruktur.

XML itu format teks murni (gak dikompres), jadi byte-nya predictable dan bisa di-hit persis - sama pendekatan kayak generate_dummy_csv.py / generate_dummy_sql.py / generate_dummy_pdf.py.

Max size default 10MB (bukan 100MB) - XML pada praktiknya (config file, API response, feed, dsb) jarang butuh ukuran gede banget, beda dari PDF/ZIP/dokumen yang wajar sampai puluhan-ratusan MB.

Gak butuh dependency eksternal, cuma Python standard library.

## Requirements

- Python 3.8+

## Install

### 1. Install Python

Jika belum ada Python 3.8+, install dari https://www.python.org/downloads/

### 2. (Opsional) Setup virtual environment untuk Python

```bash
python3 -m venv venv
source venv/bin/activate
```

## Cara cek apakah sudah siap semua

```bash
# Cek Python version
python3 --version
```

## Usage

```bash
# generate 10 varian ukuran default (1KB s/d 10MB)
python3 generate_dummy_xml.py

# generate ukuran tertentu aja
python3 generate_dummy_xml.py --sizes 1kb,5mb

# ukuran custom yang gak ada di default
python3 generate_dummy_xml.py --sizes 250kb,2.5mb,777kb

# ganti folder output
python3 generate_dummy_xml.py --outdir ./xml

# ganti prefix nama file (default: Contohnya-XML)
python3 generate_dummy_xml.py --prefix MyFile

# pakai definisi binary (1 MB = 1024x1024 bytes / MiB) instead of decimal (default)
python3 generate_dummy_xml.py --sizes 10mb --binary
```

### Ukuran default

`1KB, 5KB, 10KB, 50KB, 100KB, 500KB, 1MB, 2MB, 5MB, 10MB`

Nama file output ikut pattern `{prefix}-{ukuran}.xml`, misal `Contohnya-XML-1KB.xml`, `Contohnya-XML-10MB.xml`.

### Decimal vs Binary

Default script ini pakai definisi **decimal** (1 KB = 1.000 bytes, 1 MB = 1.000.000 bytes), sesuai gimana kebanyakan file manager/browser/dashboard cloud storage (R2, S3, dll) nampilin ukuran file. Kalau butuh definisi **binary/KiB-MiB** (1 KB = 1024 bytes), pakai flag `--binary`.

### Cara kerja

1. Script Python generate XML dengan elemen <item> berulang
2. Setiap elemen <item> berisi teks dummy dan referensi ke contohnya.web.id
3. Script menghitung overhead root element dan padding presisi
4. Padding menggunakan XML comment sebelum </data> untuk mencapai byte-exact target
5. Jika sisa terlalu kecil untuk comment valid, isi dengan whitespace

### Presisi ukuran

XML ini bisa mencapai **byte-exact** 100% presisi karena:
- XML adalah format teks murni (gak dikompres)
- Byte-nya predictable dan bisa di-hit persis
- Padding menggunakan XML comment untuk presisi

### Struktur XML

```xml
<?xml version="1.0" encoding="UTF-8"?>
<data>
  <item id="1">
    <keterangan>Dummy data testing - abcdefghijklmnopqrstuvwxyz</keterangan>
    <sumber>contohnya.web.id</sumber>
  </item>
  <item id="2">
    <keterangan>Dummy data testing - bcdefghijklmnopqrstuvwxyza</keterangan>
    <sumber>-</sumber>
  </item>
  ...
  <!-- padding untuk presisi byte-exact -->
</data>
```

### Customization

Bisa ubah teks di dalam XML dengan mengedit bagian ini di script:

```python
SITE_MENTION = "contohnya.web.id"
MENTION_EVERY_N_ROWS = 5
ROOT_OPEN = '<?xml version="1.0" encoding="UTF-8"?>\n<data>\n'
ROOT_CLOSE = "</data>\n"
```

## Uninstall

Hapus virtual environment jika digunakan:

```bash
rm -rf venv
```

## Disclaimer

Kode di repo ini dibuat dengan bantuan **Claude Sonnet 5** (Anthropic).

## License

MIT