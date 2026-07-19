# generate-dummy-svg

Script Python buat generate dummy SVG berukuran presisi (byte-exact) untuk keperluan testing upload/download, parsing gambar vector, dan sejenisnya.

File yang dihasilkan tetap SVG valid (bisa dibuka di browser atau SVG viewer mana pun, bukan cuma file random bytes yang dipaksa berekstensi `.svg`), dan isinya beneran multi-element (bukan cuma 1 element + padding tersembunyi) — jumlah element menyesuaikan besar target ukuran.

SVG itu format teks/XML murni (bukan container terkompresi kayak XLSX), jadi bisa di-padding byte-exact kayak PDF — gak perlu estimasi.

Gak butuh dependency eksternal, cuma Python standard library.

## Requirements

- Python 3.8+
- Tidak butuh library eksternal (hanya Python standard library)

## Install

### Opsi 1 — langsung ke sistem

Di distro Linux modern (Debian/Ubuntu terbaru dkk), `pip install` biasa bakal ke-block sama proteksi `externally-managed-environment`. Tapi buat SVG generator ini gak butuh pip, jadi langsung bisa dipakai:

```bash
python3 generate_dummy_svg.py
```

### Opsi 2 — virtual environment (lebih direkomendasikan)

```bash
python3 -m venv venv
source venv/bin/activate
# Tidak perlu install apapun, script ini pakai Python standard library
```

Tiap mau pakai lagi, aktifin dulu venv-nya: `source venv/bin/activate`.

## Usage

```bash
# generate 10 varian ukuran default (1KB s/d 10MB)
python3 generate_dummy_svg.py

# generate ukuran tertentu aja
python3 generate_dummy_svg.py --sizes 1kb,5mb

# ukuran custom yang gak ada di default
python3 generate_dummy_svg.py --sizes 250kb,2.5mb,777kb

# ganti folder output
python3 generate_dummy_svg.py --outdir ./svg

# ganti prefix nama file (default: Contohnya-SVG)
python3 generate_dummy_svg.py --prefix MyFile

# pakai definisi binary (1 MB = 1024x1024 bytes / MiB) instead of decimal (default)
python3 generate_dummy_svg.py --sizes 10mb --binary
```

### Ukuran default

`1KB, 5KB, 10KB, 50KB, 100KB, 500KB, 1MB, 2MB, 5MB, 10MB`

Nama file output ikut pattern `{prefix}-{ukuran}.svg`, misal `Contohnya-SVG-1KB.svg`, `Contohnya-SVG-10MB.svg`.

### Decimal vs Binary

Default script ini pakai definisi **decimal** (1 KB = 1.000 bytes, 1 MB = 1.000.000 bytes), sesuai gimana kebanyakan file manager/browser/dashboard cloud storage (R2, S3, dll) nampilin ukuran file. Kalau butuh definisi **binary/KiB-MiB** (1 KB = 1024 bytes), pakai flag `--binary`.

### Kustomisasi teks di dalam SVG

Edit langsung dua variabel ini di bagian atas file `generate_dummy_svg.py`:

```python
SVG_TITLE = "Contohnya.web.id"
SVG_CAPTION = "Dummy SVG"
```

### Cara kerja (singkat)

1. Bikin base SVG valid berisi konten teks asli (background abstrak dengan gradient + shape acak, judul, ukuran file, keterangan) — jumlah shape menyesuaikan besar target (makin gede target, makin banyak shape, dicap di 14 shape).
2. Kalau masih ada sisa gap ke ukuran target, ditambahin XML comment berisi **string 'x' berulang** sebagai padding.
3. SVG itu format teks/XML murni, jadi padding-nya gak ikut dikompres dan ukuran akhir tetap presisi byte-exact.

## Uninstall

Tidak perlu uninstall apapun karena script ini gak butuh library eksternal. Cukup hapus foldernya kalau mau:

```bash
rm -rf venv
```

## Cara kerja (singkat)

1. Bikin base SVG valid berisi konten teks asli (background abstrak dengan gradient + shape acak, judul, ukuran file, keterangan) — jumlah shape menyesuaikan besar target (makin gede target, makin banyak shape, dicap di 14 shape).
2. Kalau masih ada sisa gap ke ukuran target, ditambahin XML comment berisi **string 'x' berulang** sebagai padding.
3. SVG itu format teks/XML murni, jadi padding-nya gak ikut dikompres dan ukuran akhir tetap presisi byte-exact.

## Disclaimer

Kode di repo ini dibuat dengan bantuan **Claude Sonnet 5** (Anthropic).

## License

MIT