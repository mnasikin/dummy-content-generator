# generate-dummy-webp

Script Python buat generate dummy WebP berukuran presisi (byte-exact) untuk keperluan testing upload/download/parsing gambar.

File yang dihasilkan tetap WebP valid (bisa dibuka di browser atau WebP viewer mana pun, bukan cuma file random bytes yang dipaksa berekstensi `.webp`), dan isinya beneran multi-element (bukan cuma 1 element + padding tersembunyi) — jumlah element menyesuaikan besar target ukuran.

WebP itu format teks/container terkompresi kayak PNG, jadi bisa di-padding byte-exact lewat estimasi + koreksi iteratif.

Gak butuh dependency eksternal, cuma Python standard library + Pillow (optional).

## Requirements

- Python 3.8+
- Pillow (recommended) atau Python standard library (fallback)

## Install

### Opsi 1 — langsung ke sistem

Di distro Linux modern (Debian/Ubuntu terbaru dkk), `pip install` biasa bakal ke-block sama proteksi `externally-managed-environment`. Install Pillow dulu:

```bash
pip install Pillow --break-system-packages
```

### Opsi 2 — virtual environment (lebih direkomendasikan)

```bash
python3 -m venv venv
source venv/bin/activate
pip install Pillow
```

Tiap mau pakai lagi, aktifin dulu venv-nya: `source venv/bin/activate`.

## Usage

```bash
# generate 10 varian ukuran default (1KB s/d 10MB)
python3 generate_dummy_webp.py

# generate ukuran tertentu aja
python3 generate_dummy_webp.py --sizes 1kb,5mb

# ukuran custom yang gak ada di default
python3 generate_dummy_webp.py --sizes 250kb,2.5mb,777kb

# ganti folder output
python3 generate_dummy_webp.py --outdir ./webp

# ganti prefix nama file (default: Contohnya-WebP)
python3 generate_dummy_webp.py --prefix MyFile

# pakai definisi binary (1 MB = 1024x1024 bytes / MiB) instead of decimal (default)
python3 generate_dummy_webp.py --sizes 10mb --binary
```

### Ukuran default

`1KB, 5KB, 10KB, 50KB, 100KB, 500KB, 1MB, 2MB, 5MB, 10MB`

Nama file output ikut pattern `{prefix}-{ukuran}.webp`, misal `Contohnya-WebP-1KB.webp`, `Contohnya-WebP-10MB.webp`.

### Decimal vs Binary

Default script ini pakai definisi **decimal** (1 KB = 1.000 bytes, 1 MB = 1.000.000 bytes), sesuai gimana kebanyakan file manager/browser/dashboard cloud storage (R2, S3, dll) nampilin ukuran file. Kalau butuh definisi **binary/KiB-MiB** (1 KB = 1024 bytes), pakai flag `--binary`.

### Kustomisasi teks di dalam WebP

Edit langsung dua variabel ini di bagian atas file `generate_dummy_webp.py`:

```python
WEBP_TITLE = "Contohnya.web.id"
WEBP_CAPTION = "Dummy WebP"
```

### Cara kerja (singkat)

1. Bikin base WebP valid berisi konten gambar asli (background abstrak dengan gradient + shape acak, judul, ukuran file, keterangan) — jumlah shape menyesuaikan besar target.
2. Kalau masih ada sisa gap ke ukuran target, ditambahin byte dummy di akhir file sebagai padding.
3. WebP itu format container terkompresi, jadi padding-nya gak ikut dikompres dan ukuran akhir tetap presisi byte-exact.

## Uninstall

```bash
pip uninstall Pillow --break-system-packages
```

Kalau pakai virtual environment, cukup hapus foldernya:

```bash
rm -rf venv
```

## Cara kerja (singkat)

1. Bikin base WebP valid berisi konten gambar asli (background abstrak dengan gradient + shape acak, judul, ukuran file, keterangan) — jumlah shape menyesuaikan besar target.
2. Kalau masih ada sisa gap ke ukuran target, ditambahin byte dummy di akhir file sebagai padding.
3. WebP itu format container terkompresi, jadi padding-nya gak ikut dikompres dan ukuran akhir tetap presisi byte-exact.

## Disclaimer

Kode di repo ini dibuat dengan bantuan **Claude Sonnet 5** (Anthropic).

## License

MIT