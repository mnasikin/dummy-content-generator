# generate-dummy-avif

Script Python buat generate dummy AVIF berukuran presisi (byte-exact-ish target with filler) buat testing upload/download/parsing gambar. Tiap file berisi gambar AVIF asli (bukan cuma file acak ber-ekstensi `.avif`), lalu dipad dengan trailing filler agar ukurannya pas target.

File yang dihasilkan tetap AVIF valid (bisa dibuka di browser atau AVIF viewer mana pun, bukan cuma file random bytes yang dipaksa berekstensi `.avif`), dan isinya beneran multi-element (bukan cuma 1 element + padding tersembunyi) — jumlah element menyesuaikan besar target ukuran.

AVIF itu format container terkompresi, jadi bisa di-padding byte-exact lewat estimasi + koreksi iteratif.

Butuh dependency eksternal: Pillow (dan pillow-heif atau pillow-avif-plugin).

## Requirements

- Python 3.8+
- Pillow
- pillow-heif atau pillow-avif-plugin

## Install

### Opsi 1 — pakai pillow-heif

```bash
pip install Pillow pillow-heif --break-system-packages
```

### Opsi 2 — pakai pillow-avif-plugin

```bash
pip install Pillow pillow-avif-plugin --break-system-packages
```

### Opsi 3 — virtual environment (lebih direkomendasikan)

```bash
python3 -m venv venv
source venv/bin/activate
pip install Pillow pillow-heif
```

Tiap mau pakai lagi, aktifin dulu venv-nya: `source venv/bin/activate`.

## Usage

```bash
# generate 10 varian ukuran default (25KB s/d 15MB)
python3 generate_dummy_avif.py

# generate ukuran tertentu aja
python3 generate_dummy_avif.py --sizes 25kb,1mb,15mb

# ukuran custom yang gak ada di default
python3 generate_dummy_avif.py --sizes 250kb,2.5mb,777kb

# ganti folder output
python3 generate_dummy_avif.py --outdir ./avif

# ganti prefix nama file (default: Contohnya-AVIF)
python3 generate_dummy_avif.py --prefix MyFile
```

### Ukuran default

`25KB, 50KB, 100KB, 250KB, 500KB, 1MB, 2MB, 3MB, 5MB, 15MB`

Nama file output ikut pattern `{prefix}-{ukuran}.avif`, misal `Contohnya-AVIF-25KB.avif`, `Contohnya-AVIF-15MB.avif`.

### Kustomisasi teks di dalam AVIF

Edit langsung dua variabel ini di bagian atas file `generate_dummy_avif.py`:

```python
AVIF_TITLE = "Contohnya.web.id"
AVIF_CAPTION = "Dummy File AVIF"
```

### Cara kerja (singkat)

1. Script otomatis mendeteksi dan memilih support AVIF yang tersedia (pillow-heif, pillow-avif-plugin, atau native Pillow).
2. Bikin base AVIF valid berisi konten gambar asli (background abstrak dengan gradient + shape acak, judul, ukuran file, keterangan) — jumlah shape menyesuaikan besar target.
3. Kalau masih ada sisa gap ke ukuran target, ditambahin byte dummy di akhir file sebagai padding.
4. AVIF itu format container terkompresi, jadi padding-nya gak ikut dikompres dan ukuran akhir tetap presisi byte-exact.

## Uninstall

```bash
pip uninstall Pillow pillow-heif pillow-avif-plugin --break-system-packages
```

Kalau pakai virtual environment, cukup hapus foldernya:

```bash
rm -rf venv
```

## Disclaimer

Kode di repo ini dibuat dengan bantuan **Claude Sonnet 5** (Anthropic).

## License

MIT