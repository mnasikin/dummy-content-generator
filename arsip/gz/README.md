# generate-dummy-gz

Script Python buat generate dummy .gz berukuran presisi (byte-exact) untuk keperluan testing upload/extract/kompresi.

File yang dihasilkan tetap .gz valid (bisa di-extract di tool mana pun, bukan cuma file random bytes yang dipaksa berekstensi `.gz`), dan isinya beneran ada data:
- README.txt (nyebutin contohnya.web.id + ukuran target)
- 1 atau lebih file data/dummy-N.bin (random bytes) — buat size gede, otomatis dipecah jadi multi item (bukan 1 file .bin raksasa doang)

.gz dibuat pakai gzip-compressed tar stream, jadi ukurannya predictable dan bisa di-hit byte-exact lewat estimasi + koreksi iteratif.

Gak butuh dependency eksternal, cuma Python standard library.

## Requirements

- Python 3.8+
- Tidak butuh library eksternal (hanya Python standard library)

## Install

### Opsi 1 — langsung ke sistem

Di distro Linux modern (Debian/Ubuntu terbaru dkk), `pip install` biasanya akan ke-block sama proteksi `externally-managed-environment`. Tapi buat .gz generator ini gak butuh pip, jadi langsung bisa dipakai:

```bash
python3 generate_dummy_gz.py
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
# generate 10 varian ukuran default (32KB s/d 50MB)
python3 generate_dummy_gz.py

# generate ukuran tertentu aja
python3 generate_dummy_gz.py --sizes 64kb,256kb,1mb,7mb

# generate N varian default dengan ukuran maks tertentu
python3 generate_dummy_gz.py --count 6
python3 generate_dummy_gz.py --count 5 --max-size 25mb

# ganti folder output
python3 generate_dummy_gz.py --outdir ./gz

# ganti prefix nama file (default: Contohnya-GZ)
python3 generate_dummy_gz.py --prefix MyFile

# ganti ukuran maks per file data/dummy-*.bin di dalam .gz (default: 20MB)
python3 generate_dummy_gz.py --chunk-cap 10mb

# pakai definisi binary (1 MB = 1024x1024 bytes / MiB) instead of decimal (default)
python3 generate_dummy_gz.py --sizes 50mb --binary
```

### Ukuran default

`32KB, 64KB, 128KB, 256KB, 512KB, 1MB, 2MB, 5MB, 10MB, 50MB`

Nama file output ikut pattern `{prefix}-{ukuran}.gz`, misal `Contohnya-GZ-32KB.gz`, `Contohnya-GZ-50MB.gz`.

### Decimal vs Binary

Default script ini pakai definisi **decimal** (1 KB = 1.000 bytes, 1 MB = 1.000.000 bytes), sesuai gimana kebanyakan file manager/browser/dashboard cloud storage (R2, S3, dll) nampilin ukuran file. Kalau butuh definisi **binary/KiB-MiB** (1 KB = 1024 bytes), pakai flag `--binary`.

### Kustomisasi teks di dalam .gz

Edit variabel ini di bagian atas file `generate_dummy_gz.py`:

```python
SITE_MENTION = "contohnya.web.id"
README_TEMPLATE = (
    "Dummy GZ Archive - {site}\n"
    "Ukuran target: {label}\n"
    "File ini dibuat untuk testing upload, extract, dan validasi ukuran.\n"
    "Isi arsip: README.txt + file data/dummy-N.bin.\n"
)
```

### Chunk Cap

Parameter `--chunk-cap` mengatur ukuran maksimum per file data/dummy-*.bin di dalam .gz sebelum dipecah jadi item baru. Default: 20MB. Ini berguna untuk menghindari file .bin yang terlalu besar.

### Count & Max Size

Parameter `--count` mengatur jumlah varian default yang digenerate (maks 10). Parameter `--max-size` mengatur batas size terbesar untuk varian default. Default: count=10, max-size=50mb.

## Uninstall

Tidak perlu uninstall apapun karena script ini gak butuh library eksternal. Cukup hapus foldernya kalau mau:

```bash
rm -rf venv
```

## Cara kerja (singkat)

1. Bikin base .gz berisi README.txt + N file data/dummy-*.bin (random bytes) — jumlah item menyesuaikan besar target.
2. Hitung estimasi ukuran dan koreksi iteratif sampai ukuran file persis target_bytes.
3. .gz dibuat dengan gzip-compressed tar stream supaya ukuran akhir tetap presisi byte-exact.

## Presisi ukuran

.gz ini bisa byte-exact 100% karena:
- Format .gz yang dikompres (bukan uncompressed)
- Pakai estimasi + koreksi iteratif untuk mendekati target
- Isi arsip beneran ada data (bukan cuma padding kosong)

## Struktur isi .gz

Setelah di-extract, isi .gz akan berupa:
- README.txt — teks dengan info tentang file dan ukuran target
- data/dummy-1.bin, data/dummy-2.bin, dst — file random bytes

## Disclaimer

Kode di repo ini dibuat dengan bantuan **Claude Sonnet 5** (Anthropic).

## License

MIT