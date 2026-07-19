# generate-dummy-ts

Script Python buat generate dummy TypeScript berukuran presisi (byte-exact) untuk keperluan testing upload/download/parsing file.

File yang dihasilkan tetap TypeScript valid (bisa dijalankan di browser tanpa error), dan isinya beneran script TypeScript aman yang nyebut "Contohnya.web.id", label ukuran file, dan keterangan "Dummy File TS".

Output .ts sengaja dibuat aman dan statis:
- tidak pakai eval / new Function
- tidak pakai fetch / XHR / WebSocket
- tidak pakai import / require
- tidak pakai localStorage / sessionStorage
- tidak pakai innerHTML dari string dinamis
- hanya render landing page sederhana dengan textContent
- memakai type annotation yang aman dan jelas

Ukuran file dipaskan memakai block comment supaya tetap valid.

Gak butuh dependency eksternal, cuma Python standard library.

## Requirements

- Python 3.8+
- TypeScript compiler (tsc) untuk compile file .ts yang dihasilkan (opsional, untuk validasi syntax)

## Install

Tidak perlu install apapun, cuma butuh Python 3.8+ yang terinstall di sistem.

## Usage

```bash
# generate 10 varian ukuran default (10KB s/d 2MB)
python3 generate_dummy_ts.py

# generate ukuran tertentu aja
python3 generate_dummy_ts.py --sizes 10kb,100kb

# ukuran custom yang gak ada di default
python3 generate_dummy_ts.py --sizes 250kb,1.5mb,777kb

# ganti folder output
python3 generate_dummy_ts.py --outdir ./ts

# ganti prefix nama file (default: Contohnya-TS)
python3 generate_dummy_ts.py --prefix MyFile

# pakai definisi binary (1 KB = 1024 bytes) instead of decimal (default)
python3 generate_dummy_ts.py --sizes 10mb --binary
```

### Ukuran default

`10KB, 25KB, 50KB, 100KB, 150KB, 250KB, 500KB, 750KB, 1MB, 2MB`

Nama file output ikut pattern `{prefix}-{ukuran}.ts`, misal `Contohnya-TS-50KB.ts`, `Contohnya-TS-2MB.ts`.

### Decimal vs Binary

Default script ini pakai definisi **decimal** (1 KB = 1.000 bytes, 1 MB = 1.000.000 bytes), sesuai gimana kebanyakan file manager/browser/dashboard cloud storage (R2, S3, dll) nampilin ukuran file. Kalau butuh definisi **binary/KiB-MiB** (1 KB = 1024 bytes), pakai flag `--binary`.

### Kustomisasi teks di dalam TypeScript

Edit langsung dua variabel ini di bagian atas file `generate_dummy_ts.py`:

```python
TS_TITLE = "Contohnya.web.id"
TS_CAPTION = "Dummy File TS"
```

### Cara kerja (singkat)

1. Bikin base TypeScript valid berisi script aman yang hanya merender konten statis dengan textContent dan type annotation yang jelas (tidak ada eval, Function, network call, atau storage access).
2. Kalau masih ada sisa gap ke ukuran target, ditambahin byte dummy di dalam block comment supaya ukuran akhir tetap presisi byte-exact.
3. TypeScript itu format teks, jadi padding-nya gak ikut dikompres dan ukuran akhir tetap presisi byte-exact.

### Keamanan

Script ini sengaja dibuat aman:
- Tidak ada `eval()`, `new Function()`, atau dynamic function constructor
- Tidak ada `fetch()`, `XMLHttpRequest()`, `WebSocket`, atau network access
- Tidak ada `import()`, `require()`, atau module loading
- Tidak ada `innerHTML` dari string dinamis
- Tidak ada `localStorage` atau `sessionStorage`
- Hanya merender konten statis dengan `textContent`
- Memakai type annotation yang aman dan jelas
- Cocok untuk testing upload manager, file browser, MIME detection, dan validasi ukuran file

## Uninstall

Tidak perlu uninstall apapun, karena gak ada dependency eksternal.

## Disclaimer

Kode di repo ini dibuat dengan bantuan **Claude Sonnet 5** (Anthropic).

## License

MIT