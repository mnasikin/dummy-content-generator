# generate-dummy-js

Script Python buat generate dummy JavaScript berukuran presisi (byte-exact) untuk keperluan testing upload/download/parsing file.

File yang dihasilkan tetap JS valid (bisa dijalankan di browser tanpa error), dan isinya beneran script JavaScript aman yang nyebut "Contohnya.web.id", label ukuran file, dan keterangan "Dummy File JS".

Output .js sengaja dibuat aman dan statis:
- tidak pakai eval / new Function
- tidak pakai fetch / XHR / WebSocket
- tidak pakai import / require
- tidak pakai localStorage / sessionStorage
- tidak pakai innerHTML dari string dinamis
- hanya render landing page sederhana dengan textContent

Ukuran file dipaskan memakai block comment JS supaya tetap valid.

Gak butuh dependency eksternal, cuma Python standard library.

## Requirements

- Python 3.8+
- Browser modern (untuk menjalankan file JS yang dihasilkan)

## Install

Tidak perlu install apapun, cuma butuh Python 3.8+ yang terinstall di sistem.

## Usage

```bash
# generate 10 varian ukuran default (10KB s/d 2MB)
python3 generate_dummy_js.py

# generate ukuran tertentu aja
python3 generate_dummy_js.py --sizes 10kb,100kb

# ukuran custom yang gak ada di default
python3 generate_dummy_js.py --sizes 250kb,1.5mb,777kb

# ganti folder output
python3 generate_dummy_js.py --outdir ./js

# ganti prefix nama file (default: Contohnya-JS)
python3 generate_dummy_js.py --prefix MyFile

# pakai definisi binary (1 KB = 1024 bytes) instead of decimal (default)
python3 generate_dummy_js.py --sizes 10mb --binary
```

### Ukuran default

`10KB, 25KB, 50KB, 100KB, 150KB, 250KB, 500KB, 750KB, 1MB, 2MB`

Nama file output ikut pattern `{prefix}-{ukuran}.js`, misal `Contohnya-JS-50KB.js`, `Contohnya-JS-2MB.js`.

### Decimal vs Binary

Default script ini pakai definisi **decimal** (1 KB = 1.000 bytes, 1 MB = 1.000.000 bytes), sesuai gimana kebanyakan file manager/browser/dashboard cloud storage (R2, S3, dll) nampilin ukuran file. Kalau butuh definisi **binary/KiB-MiB** (1 KB = 1024 bytes), pakai flag `--binary`.

### Kustomisasi teks di dalam JS

Edit langsung dua variabel ini di bagian atas file `generate_dummy_js.py`:

```python
JS_TITLE = "Contohnya.web.id"
JS_CAPTION = "Dummy File JS"
```

### Cara kerja (singkat)

1. Bikin base JS valid berisi script aman yang hanya merender konten statis dengan textContent (tidak ada eval, Function, network call, atau storage access).
2. Kalau masih ada sisa gap ke ukuran target, ditambahin byte dummy di dalam block comment JS supaya ukuran akhir tetap presisi byte-exact.
3. JS itu format teks, jadi padding-nya gak ikut dikompres dan ukuran akhir tetap presisi byte-exact.

### Keamanan

Script ini sengaja dibuat aman:
- Tidak ada `eval()`, `new Function()`, atau dynamic function constructor
- Tidak ada `fetch()`, `XMLHttpRequest()`, `WebSocket`, atau network access
- Tidak ada `import()`, `require()`, atau module loading
- Tidak ada `innerHTML` dari string dinamis
- Tidak ada `localStorage` atau `sessionStorage`
- Hanya merender konten statis dengan `textContent`
- Cocok untuk testing upload manager, file browser, MIME detection, dan validasi ukuran file

## Uninstall

Tidak perlu uninstall apapun, karena gak ada dependency eksternal.

## Disclaimer

Kode di repo ini dibuat dengan bantuan **Claude Sonnet 5** (Anthropic).

## License

MIT