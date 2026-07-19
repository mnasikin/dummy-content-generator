# generate-dummy-tar

Script Python buat generate dummy TAR (.tar, uncompressed) berukuran presisi (byte-exact) untuk keperluan testing upload/extract/arsip.

File yang dihasilkan tetap TAR valid (bisa di-extract di tool mana pun, bukan cuma file random bytes yang dipaksa berekstensi `.tar`), dan isinya beneran ada data:
- README.txt (nyebutin contohnya.web.id + ukuran target)
- 1 atau lebih file data/dummy-N.bin (random bytes) — buat size gede, otomatis dipecah jadi multi item

CATATAN PENTING soal presisi ukuran:
TAR itu format berbasis block 512-byte, dan library tarfile Python SELALU membulatkan ukuran akhir file ke kelipatan 10.240 bytes (20 block, standar "tar record size" POSIX/GNU tar), berapa pun persis isi datanya. Ini batasan format, bukan bug script. Jadi hasil akhirnya "sedekat mungkin ke target, dibulatkan ke atas ke kelipatan 10.240 bytes terdekat" - BEDA dari generate_dummy_zip.py yang bisa byte-exact 100% (ZIP gak punya batasan ini).

Gak butuh dependency eksternal, cuma Python standard library.

## Requirements

- Python 3.8+
- Tidak butuh library eksternal (hanya Python standard library)

## Install

### Opsi 1 — langsung ke sistem

Di distro Linux modern (Debian/Ubuntu terbaru dkk), `pip install` biasanya akan ke-block sama proteksi `externally-managed-environment`. Tapi buat TAR generator ini gak butuh pip, jadi langsung bisa dipakai:

```bash
python3 generate_dummy_tar.py
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
# generate 10 varian ukuran default (10KB s/d 100MB)
python3 generate_dummy_tar.py

# generate ukuran tertentu aja
python3 generate_dummy_tar.py --sizes 10kb,5mb

# ukuran custom yang gak ada di default
python3 generate_dummy_tar.py --sizes 250kb,2.5mb,777kb

# ganti folder output
python3 generate_dummy_tar.py --outdir ./tar

# ganti prefix nama file (default: Contohnya-TAR)
python3 generate_dummy_tar.py --prefix MyFile

# ganti ukuran maks per file .bin di dalam TAR (default: 20MB)
python3 generate_dummy_tar.py --chunk-cap 10mb

# pakai definisi binary (1 MB = 1024x1024 bytes / MiB) instead of decimal (default)
python3 generate_dummy_tar.py --sizes 100mb --binary
```

### Ukuran default

`10KB, 50KB, 100KB, 500KB, 1MB, 5MB, 10MB, 25MB, 50MB, 100MB`

Nama file output ikut pattern `{prefix}-{ukuran}.tar`, misal `Contohnya-TAR-10KB.tar`, `Contohnya-TAR-100MB.tar`.

### Decimal vs Binary

Default script ini pakai definisi **decimal** (1 KB = 1.000 bytes, 1 MB = 1.000.000 bytes), sesuai gimana kebanyakan file manager/browser/dashboard cloud storage (R2, S3, dll) nampilin ukuran file. Kalau butuh definisi **binary/KiB-MiB** (1 KB = 1024 bytes), pakai flag `--binary`.

### Kustomisasi teks di dalam TAR

Edit variabel ini di bagian atas file `generate_dummy_tar.py`:

```python
SITE_MENTION = "contohnya.web.id"
README_TEMPLATE = (
    "Dummy TAR Archive - {site}\n"
    "Ukuran target: {label}\n"
    "File ini dibuat untuk keperluan testing upload, extract, dan arsip.\n"
)
```

### Chunk Cap

Parameter `--chunk-cap` mengatur ukuran maksimum per file .bin di dalam TAR sebelum dipecah jadi item baru. Default: 20MB. Ini berguna untuk menghindari file .bin yang terlalu besar.

## Uninstall

Tidak perlu uninstall apapun karena script ini gak butuh library eksternal. Cukup hapus foldernya kalau mau:

```bash
rm -rf venv
```

## Cara kerja (singkat)

1. Bikin base TAR berisi README.txt + N file data/dummy-*.bin (random bytes) — jumlah item menyesuaikan besar target.
2. Hitung estimasi ukuran dan koreksi iteratif sampai ukuran file sedekat mungkin ke target (dibulatkan ke kelipatan 10.240 bytes terdekat).
3. TAR dibuat dengan format uncompressed (gak dikompres) supaya ukuran akhir tetap predictable.

## Presisi ukuran

TAR format punya batasan inherent: ukuran akhir file SELALU dibulatkan ke kelipatan 10.240 bytes (20 block tar). Ini berarti:
- Untuk target kecil (misal 10KB), ukuran akhir bisa jadi 20.480 bytes
- Untuk target besar (misal 100MB), ukuran akhir bisa jadi 100.000.640 bytes
- Script mencoba mendekati target sebisa mungkin dengan koreksi overhead header TAR

Ini berbeda dari ZIP yang bisa byte-exact 100% karena ZIP gak punya batasan block-based seperti TAR.

## Disclaimer

Kode di repo ini dibuat dengan bantuan **Claude Sonnet 5** (Anthropic).

## License

MIT