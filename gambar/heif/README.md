# generate-dummy-heif

Script Python buat generate dummy HEIF berukuran presisi (byte-exact-ish target with filler) buat testing upload/download/parsing gambar. Tiap file berisi gambar HEIF asli (bukan cuma file acak ber-ekstensi `.heif`), lalu dipad dengan trailing filler agar ukurannya pas target.

File yang dihasilkan tetap HEIF valid (bisa dibuka di browser atau HEIF viewer mana pun, bukan cuma file random bytes yang dipaksa berekstensi `.heif`), dan isinya beneran multi-element (bukan cuma 1 element + padding tersembunyi) — jumlah element menyesuaikan besar target ukuran.

HEIF itu format container terkompresi, jadi bisa di-padding byte-exact lewat estimasi + koreksi iteratif.

Butuh dependency eksternal: Pillow dan pillow-heif.

## Requirements

- Python 3.8+
- Pillow
- pillow-heif

## Install

### Opsi 1 — langsung ke sistem

Di distro Linux modern (Debian/Ubuntu terbaru dkk), `pip install` biasakan ke-block sama proteksi `externally-managed-environment`. Install Pillow dan pillow-heif dulu:

```bash
pip install Pillow pillow-heif --break-system-packages
```

### Opsi 2 — virtual environment (lebih direkomendasikan)

```bash
python3 -m venv venv
source venv/bin/activate
pip install Pillow pillow-heif
```

Tiap mau pakai lagi, aktifin dulu venv-nya: `source venv/bin/activate`.

## Usage

```bash
# generate 10 varian ukuran default (25KB s/d 15MB)
python3 generate_dummy_heif.py

# generate ukuran tertentu aja
python3 generate_dummy_heif.py --sizes 25kb,1mb,15mb

# ukuran custom yang gak ada di default
python3 generate_dummy_heif.py --sizes 250kb,2.5mb,777kb

# ganti folder output
python3 generate_dummy_heif.py --outdir ./heif

# ganti prefix nama file (default: Contohnya-HEIF)
python3 generate_dummy_heif.py --prefix MyFile
```

### Ukuran default

`25KB, 50KB, 100KB, 250KB, 500KB, 1MB, 2MB, 3MB, 5MB, 15MB`

Nama file output ikut pattern `{prefix}-{ukuran}.heif`, misal `Contohnya-HEIF-25KB.heif`, `Contohnya-HEIF-15MB.heif`.

### Kustomisasi teks di dalam HEIF

Edit langsung dua variabel ini di bagian atas file `generate_dummy_heif.py`:

```python
HEIF_TITLE = "Contohnya.web.id"
HEIF_CAPTION = "Dummy File HEIF"
```

### Cara kerja (singkat)

1. Bikin base HEIF valid berisi konten gambar asli (background abstrak dengan gradient + shape acak, judul, ukuran file, keterangan) — jumlah shape menyesuaikan besar target.
2. Kalau masih ada sisa gap ke ukuran target, ditambahin byte dummy di akhir file sebagai padding.
3. HEIF itu format container terkompresi, jadi padding-nya gak ikut dikompres dan ukuran akhir tetap presisi byte-exact.

## Uninstall

```bash
pip uninstall Pillow pillow-heif --break-system-packages
```

Kalau pakai virtual environment, cukup hapus foldernya:

```bash
rm -rf venv
```

## Disclaimer

Kode di repo ini dibuat dengan bantuan **Claude Sonnet 5** (Anthropic).

## License

MIT