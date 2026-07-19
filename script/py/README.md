# generate-dummy-py

Script Python buat generate dummy Python berukuran presisi (byte-exact) untuk keperluan testing upload/download/parsing file.

File yang dihasilkan tetap Python valid (bisa dijalankan di terminal tanpa error), dan isinya beneran script Python aman yang nyebut "Contohnya.web.id", label ukuran file, dan keterangan "Dummy File PY".

Output .py sengaja dibuat aman dan statis:
- tidak pakai eval / exec
- tidak pakai os.system / subprocess
- tidak pakai network access
- tidak pakai file delete / rename
- tidak pakai import modul berbahaya
- hanya print landing page teks sederhana

Ukuran file dipaskan memakai comment Python supaya tetap valid.

Gak butuh dependency eksternal, cuma Python standard library. Generator ini juga cuma pakai argparse, os, dan re.

## Requirements

- Python 3.8+

## Install

Tidak perlu install apapun, cuma butuh Python 3.8+ yang terinstall di sistem.

## Usage

```bash
# generate 10 varian ukuran default (10KB s/d 2MB)
python3 generate_dummy_py.py

# generate ukuran tertentu aja
python3 generate_dummy_py.py --sizes 10kb,100kb

# ukuran custom yang gak ada di default
python3 generate_dummy_py.py --sizes 250kb,1.5mb,777kb

# ganti folder output
python3 generate_dummy_py.py --outdir ./py

# ganti prefix nama file (default: Contohnya-PY)
python3 generate_dummy_py.py --prefix MyFile

# pakai definisi binary (1 KB = 1024 bytes) instead of decimal (default)
python3 generate_dummy_py.py --sizes 10mb --binary
```

### Ukuran default

`10KB, 25KB, 50KB, 100KB, 150KB, 250KB, 500KB, 750KB, 1MB, 2MB`

Nama file output ikut pattern `{prefix}-{ukuran}.py`, misal `Contohnya-PY-50KB.py`, `Contohnya-PY-2MB.py`.

### Decimal vs Binary

Default script ini pakai definisi **decimal** (1 KB = 1.000 bytes, 1 MB = 1.000.000 bytes), sesuai gimana kebanyakan file manager/browser/dashboard cloud storage (R2, S3, dll) nampilin ukuran file. Kalau butuh definisi **binary/KiB-MiB** (1 KB = 1024 bytes), pakai flag `--binary`.

### Kustomisasi teks di dalam Python

Edit langsung dua variabel ini di bagian atas file `generate_dummy_py.py`:

```python
PY_TITLE = "Contohnya.web.id"
PY_CAPTION = "Dummy File PY"
```

### Cara kerja (singkat)

1. Bikin base Python valid berisi script aman yang hanya print landing page teks sederhana (tidak ada eval, exec, os.system, subprocess, network access, atau file manipulation).
2. Kalau masih ada sisa gap ke ukuran target, ditambahin byte dummy di dalam comment Python supaya ukuran akhir tetap presisi byte-exact.
3. Python itu format teks, jadi padding-nya gak ikut dikompres dan ukuran akhir tetap presisi byte-exact.

### Keamanan

Script ini sengaja dibuat aman:
- Tidak ada `eval()`, `exec()`, atau dynamic code execution
- Tidak ada `os.system()`, `subprocess.call()`, atau shell command execution
- Tidak ada network access atau HTTP requests
- Tidak ada file deletion, rename, atau I/O operations
- Tidak ada import modul berbahaya (hanya argparse, os, re)
- Hanya print teks ke stdout
- Cocok untuk testing upload manager, file browser, MIME detection, dan validasi ukuran file

## Uninstall

Tidak perlu uninstall apapun, karena gak ada dependency eksternal.

## Disclaimer

Kode di repo ini dibuat dengan bantuan **Claude Sonnet 5** (Anthropic).

## License

MIT