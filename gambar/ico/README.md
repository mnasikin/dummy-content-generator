# generate-dummy-ico

Script Python buat generate dummy ICO berukuran presisi (byte-exact-ish target with filler) buat testing upload/download/parsing file. Tiap file berisi ikon .ico valid dengan visual sederhana bertema "Contohnya.web.id" dan label "Dummy File ICO".

File yang dihasilkan tetap ICO valid (bisa dibuka di browser atau ICO viewer mana pun, bukan cuma file random bytes yang dipaksa berekstensi `.ico`), dan isinya beneran multi-element (bukan cuma 1 element + padding tersembunyi) — jumlah element menyesuaikan besar target ukuran.

ICO itu format container terkompresi, jadi bisa di-padding byte-exact lewat estimasi + koreksi iteratif.

Gak butuh dependency eksternal, cuma Python standard library.

## Requirements

- Python 3.8+

## Install

Tidak butuh install apapun, cuma Python 3.8+ yang terinstall di sistem.

## Usage

```bash
# generate 10 varian ukuran default (10KB s/d 2MB)
python3 generate_dummy_ico.py

# generate ukuran tertentu aja
python3 generate_dummy_ico.py --sizes 10kb,1mb

# ukuran custom yang gak ada di default
python3 generate_dummy_ico.py --sizes 250kb,2.5mb,777kb

# ganti folder output
python3 generate_dummy_ico.py --outdir ./ico

# ganti prefix nama file (default: Contohnya-ICO)
python3 generate_dummy_ico.py --prefix MyFile

# pakai definisi binary (1 MB = 1024x1024 bytes / MiB) instead of decimal (default)
python3 generate_dummy_ico.py --sizes 10mb --binary
```

### Ukuran default

`10KB, 25KB, 50KB, 100KB, 150KB, 250KB, 500KB, 750KB, 1MB, 1.5MB, 2MB`

Nama file output ikut pattern `{prefix}-{ukuran}.ico`, misal `Contohnya-ICO-10KB.ico`, `Contohnya-ICO-2MB.ico`.

### Decimal vs Binary

Default script ini pakai definisi **decimal** (1 KB = 1.000 bytes, 1 MB = 1.000.000 bytes), sesuai gimana kebanyakan file manager/browser/dashboard cloud storage (R2, S3, dll) nampilin ukuran file. Kalau butuh definisi **binary/KiB-MiB** (1 KB = 1024 bytes), pakai flag `--binary`.

### Kustomisasi teks di dalam ICO

Edit langsung dua variabel ini di bagian atas file `generate_dummy_ico.py`:

```python
ICO_TITLE = "Contohnya.web.id"
ICO_CAPTION = "Dummy File ICO"
```

### Cara kerja (singkat)

1. Bikin base PNG valid berisi konten gambar asli (background abstrak dengan gradient + shape acak, judul, ukuran file, keterangan) — jumlah shape menyesuaikan besar target.
2. Convert PNG ke format ICO dengan 4 resolusi berbeda (16x16, 32x32, 48x48, 64x64).
3. Kalau masih ada sisa gap ke ukuran target, ditambahin byte dummy di akhir file sebagai padding.
4. ICO itu format container terkompresi, jadi padding-nya gak ikut dikompres dan ukuran akhir tetap presisi byte-exact.

## Uninstall

Tidak butuh uninstall apapun, karena gak ada dependency eksternal.

## Disclaimer

Kode di repo ini dibuat dengan bantuan **Claude Sonnet 5** (Anthropic).

## License

MIT