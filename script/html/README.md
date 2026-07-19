# generate-dummy-html

Script Python buat generate dummy HTML berukuran presisi (byte-exact) untuk keperluan testing upload/download/parsing file.

File yang dihasilkan tetap HTML valid (bisa dibuka di browser atau HTML viewer mana pun), dan isinya beneran landing page sederhana yang nyebut "Contohnya.web.id", label ukuran file, dan keterangan "Dummy File HTML".

HTML itu format teks, jadi gampang di-padding byte-exact pakai comment HTML supaya ukuran file pas sesuai target.

Gak butuh dependency eksternal, cuma Python standard library.

## Requirements

- Python 3.8+

## Install

Tidak perlu install apapun, cuma butuh Python 3.8+ yang terinstall di sistem.

## Usage

```bash
# generate 10 varian ukuran default (10KB s/d 2MB)
python3 generate_dummy_html.py

# generate ukuran tertentu aja
python3 generate_dummy_html.py --sizes 10kb,100kb

# ukuran custom yang gak ada di default
python3 generate_dummy_html.py --sizes 250kb,1.5mb,777kb

# ganti folder output
python3 generate_dummy_html.py --outdir ./html

# ganti prefix nama file (default: Contohnya-HTML)
python3 generate_dummy_html.py --prefix MyFile

# pakai definisi binary (1 KB = 1024 bytes) instead of decimal (default)
python3 generate_dummy_html.py --sizes 10mb --binary
```

### Ukuran default

`10KB, 25KB, 50KB, 100KB, 150KB, 250KB, 500KB, 750KB, 1MB, 2MB`

Nama file output ikut pattern `{prefix}-{ukuran}.html`, misal `Contohnya-HTML-50KB.html`, `Contohnya-HTML-2MB.html`.

### Decimal vs Binary

Default script ini pakai definisi **decimal** (1 KB = 1.000 bytes, 1 MB = 1.000.000 bytes), sesuai gimana kebanyakan file manager/browser/dashboard cloud storage (R2, S3, dll) nampilin ukuran file. Kalau butuh definisi **binary/KiB-MiB** (1 KB = 1024 bytes), pakai flag `--binary`.

### Kustomisasi teks di dalam HTML

Edit langsung dua variabel ini di bagian atas file `generate_dummy_html.py`:

```python
HTML_TITLE = "Contohnya.web.id"
HTML_CAPTION = "Dummy File HTML"
```

### Cara kerja (singkat)

1. Bikin base HTML valid berisi landing page sederhana yang nyebut "Contohnya.web.id", label ukuran file, dan keterangan "Dummy File HTML".
2. Kalau masih ada sisa gap ke ukuran target, ditambahin byte dummy di dalam comment HTML supaya ukuran akhir tetap presisi byte-exact.
3. HTML itu format teks, jadi padding-nya gak ikut dikompres dan ukuran akhir tetap presisi byte-exact.

## Uninstall

Tidak perlu uninstall apapun, karena gak ada dependency eksternal.

## Disclaimer

Kode di repo ini dibuat dengan bantuan **Claude Sonnet 5** (Anthropic).

## License

MIT