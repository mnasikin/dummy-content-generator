# generate-dummy-css

Script Python buat generate dummy CSS berukuran presisi (byte-exact) untuk keperluan testing upload, preview, dan size validation.

File yang dihasilkan tetap CSS valid (bisa di-compile di browser atau tool CSS apa pun), dan isinya beneran CSS statis dengan ukuran byte-exact atau sedekat mungkin ke target.

Output .css sengaja dibuat aman dan statis:
- tidak pakai @import atau @media yang kompleks
- tidak pakai @keyframes yang berlebihan
- tidak pakai pseudo-element yang berlebihan
- hanya berisi deklarasi CSS statis yang valid

Ukuran file dipaskan memakai block comment CSS supaya tetap valid.

Gak butuh dependency eksternal, cuma Python standard library.

## Requirements

- Python 3.8+
- Browser modern (untuk preview file CSS yang dihasilkan)

## Install

Tidak perlu install apapun, cuma butuh Python 3.8+ yang terinstall di sistem.

## Usage

```bash
# generate 10 varian ukuran default (4KB s/d 10MB)
python3 generate_dummy_css.py

# generate ukuran tertentu aja
python3 generate_dummy_css.py --sizes 4kb,8kb,16kb,32kb

# ukuran custom yang gak ada di default
python3 generate_dummy_css.py --sizes 64kb,256kb,1mb,7mb

# ganti folder output
python3 generate_dummy_css.py --outdir ./css

# ganti prefix nama file (default: Contohnya-CSS)
python3 generate_dummy_css.py --prefix MyFile

# pakai definisi binary (1 MB = 1024x1024 bytes) instead of decimal (default)
python3 generate_dummy_css.py --sizes 10mb --binary
```

### Ukuran default

`4KB, 8KB, 16KB, 32KB, 64KB, 128KB, 256KB, 512KB, 1MB, 10MB`

Nama file output ikut pattern `{prefix}-{ukuran}.css`, misal `Contohnya-CSS-4KB.css`, `Contohnya-CSS-10MB.css`.

### Decimal vs Binary

Default script ini pakai definisi **decimal** (1 KB = 1.000 bytes, 1 MB = 1.000.000 bytes), sesuai gimana kebanyakan file manager/browser/dashboard cloud storage (R2, S3, dll) nampilin ukuran file. Kalau butuh definisi **binary/KiB-MiB** (1 KB = 1024 bytes), pakai flag `--binary`.

### Kustomisasi teks di dalam CSS

Edit variabel ini di bagian atas file `generate_dummy_css.py`:

```python
SITE_MENTION = "contohnya.web.id"
```

### Cara kerja (singkat)

1. Bikin base CSS valid berisi custom properties, utility classes, dan dummy rules
2. Loop buat CSS chunk sampai mendekati target bytes
3. Kalau masih ada sisa gap ke ukuran target, ditambahin byte dummy di dalam block comment CSS supaya ukuran akhir tetap presisi byte-exact
4. CSS itu format teks, jadi padding-nya gak ikut dikompres dan ukuran akhir tetap presisi byte-exact

### Struktur isi CSS

Default script membuat CSS dengan struktur:
- Header block dengan komentar dan custom properties (:root)
- Banyak component classes dengan deklarasi CSS statis
- Grid classes
- Text utility classes
- Media queries untuk responsive design

### Keamanan

Script ini sengaja dibuat aman:
- Tidak ada @import atau @media yang berlebihan
- Tidak ada @keyframes yang berlebihan
- Tidak ada pseudo-element yang berlebihan
- Hanya berisi deklarasi CSS statis yang valid
- Cocok untuk testing upload manager, file browser, MIME detection, dan validasi ukuran file

## Uninstall

Tidak perlu uninstall apapun, karena gak ada dependency eksternal.

## Disclaimer

Kode di repo ini dibuat dengan bantuan **Claude Sonnet 5** (Anthropic).

## License

MIT