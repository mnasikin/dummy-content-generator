# generate-dummy-php

Script Python buat generate dummy PHP berukuran presisi (byte-exact) untuk keperluan testing upload/download/parsing file.

File yang dihasilkan tetap PHP valid (bisa dijalankan di server PHP tanpa error), dan isinya beneran landing page sederhana yang nyebut "Contohnya.web.id", label ukuran file, dan keterangan "Dummy File PHP".

PHP itu format teks, tapi script ini sengaja dibuat aman dan statis, jadi gampang di-padding byte-exact pakai comment block supaya ukuran file pas sesuai target.

Gak butuh dependency eksternal, cuma Python standard library.

## Requirements

- Python 3.8+
- PHP 7.4+ (untuk menjalankan file PHP yang dihasilkan)

## Install

Tidak perlu install apapun, cuma butuh Python 3.8+ yang terinstall di sistem.

## Usage

```bash
# generate 10 varian ukuran default (10KB s/d 2MB)
python3 generate_dummy_php.py

# generate ukuran tertentu aja
python3 generate_dummy_php.py --sizes 10kb,100kb

# ukuran custom yang gak ada di default
python3 generate_dummy_php.py --sizes 250kb,1.5mb,777kb

# ganti folder output
python3 generate_dummy_php.py --outdir ./php

# ganti prefix nama file (default: Contohnya-PHP)
python3 generate_dummy_php.py --prefix MyFile

# pakai definisi binary (1 KB = 1024 bytes) instead of decimal (default)
python3 generate_dummy_php.py --sizes 10mb --binary
```

### Ukuran default

`10KB, 25KB, 50KB, 100KB, 150KB, 250KB, 500KB, 750KB, 1MB, 2MB`

Nama file output ikut pattern `{prefix}-{ukuran}.php`, misal `Contohnya-PHP-50KB.php`, `Contohnya-PHP-2MB.php`.

### Decimal vs Binary

Default script ini pakai definisi **decimal** (1 KB = 1.000 bytes, 1 MB = 1.000.000 bytes), sesuai gimana kebanyakan file manager/browser/dashboard cloud storage (R2, S3, dll) nampilin ukuran file. Kalau butuh definisi **binary/KiB-MiB** (1 KB = 1024 bytes), pakai flag `--binary`.

### Kustomisasi teks di dalam PHP

Edit langsung dua variabel ini di bagian atas file `generate_dummy_php.py`:

```python
PHP_TITLE = "Contohnya.web.id"
PHP_CAPTION = "Dummy File PHP"
```

### Cara kerja (singkat)

1. Bikin base PHP valid berisi header content-type dan HTML statis yang aman (tidak ada exec, eval, include, require, curl, database, atau system call).
2. Kalau masih ada sisa gap ke ukuran target, ditambahin byte dummy di dalam comment block PHP supaya ukuran akhir tetap presisi byte-exact.
3. PHP itu format teks, jadi padding-nya gak ikut dikompres dan ukuran akhir tetap presisi byte-exact.

### Keamanan

Script ini sengaja dibuat aman:
- Tidak ada `exec()`, `eval()`, `include()`, `require()`, `curl_exec()`, atau system call lainnya
- Hanya berisi `header('Content-Type: text/html; charset=utf-8')` dan HTML statis
- Tidak ada koneksi database atau API eksternal
- Cocok untuk testing upload manager, file browser, MIME detection, dan validasi ukuran file

## Uninstall

Tidak perlu uninstall apapun, karena gak ada dependency eksternal.

## Disclaimer

Kode di repo ini dibuat dengan bantuan **Claude Sonnet 5** (Anthropic).

## License

MIT