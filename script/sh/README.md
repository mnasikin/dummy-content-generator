# generate-dummy-sh

Script Python buat generate dummy shell script berukuran presisi (byte-exact) untuk keperluan testing upload/download/parsing file.

File yang dihasilkan tetap shell script valid (bisa dijalankan di terminal tanpa error), dan isinya beneran shell script aman yang nyebut "Contohnya.web.id", label ukuran file, dan keterangan "Dummy File SH".

Output .sh sengaja dibuat aman dan statis:
- tidak pakai rm / mv / chmod / chown
- tidak pakai curl / wget / nc / ssh
- tidak pakai sudo / su
- tidak pakai eval / exec / source
- tidak pakai process kill atau fork bomb
- hanya print landing page teks sederhana

Ukuran file dipaskan memakai comment shell supaya tetap valid.

Gak butuh dependency eksternal, cuma Python standard library.

## Requirements

- Python 3.8+
- Shell (bash, sh, atau terminal lainnya) untuk menjalankan file .sh yang dihasilkan

## Install

Tidak perlu install apapun, cuma butuh Python 3.8+ yang terinstall di sistem.

## Usage

```bash
# generate 10 varian ukuran default (10KB s/d 2MB)
python3 generate_dummy_sh.py

# generate ukuran tertentu aja
python3 generate_dummy_sh.py --sizes 10kb,100kb

# ukuran custom yang gak ada di default
python3 generate_dummy_sh.py --sizes 250kb,1.5mb,777kb

# ganti folder output
python3 generate_dummy_sh.py --outdir ./sh

# ganti prefix nama file (default: Contohnya-SH)
python3 generate_dummy_sh.py --prefix MyFile

# pakai definisi binary (1 KB = 1024 bytes) instead of decimal (default)
python3 generate_dummy_sh.py --sizes 10mb --binary
```

### Ukuran default

`10KB, 25KB, 50KB, 100KB, 150KB, 250KB, 500KB, 750KB, 1MB, 2MB`

Nama file output ikut pattern `{prefix}-{ukuran}.sh`, misal `Contohnya-SH-50KB.sh`, `Contohnya-SH-2MB.sh`.

### Decimal vs Binary

Default script ini pakai definisi **decimal** (1 KB = 1.000 bytes, 1 MB = 1.000.000 bytes), sesuai gimana kebanyakan file manager/browser/dashboard cloud storage (R2, S3, dll) nampilin ukuran file. Kalau butuh definisi **binary/KiB-MiB** (1 KB = 1024 bytes), pakai flag `--binary`.

### Kustomisasi teks di dalam Shell Script

Edit langsung dua variabel ini di bagian atas file `generate_dummy_sh.py`:

```python
SH_TITLE = "Contohnya.web.id"
SH_CAPTION = "Dummy File SH"
```

### Cara kerja (singkat)

1. Bikin base shell script valid berisi script aman yang hanya print landing page teks sederhana (tidak ada rm, mv, chmod, chown, curl, wget, nc, ssh, sudo, su, eval, exec, source, atau process kill).
2. Kalau masih ada sisa gap ke ukuran target, ditambahin byte dummy di dalam comment shell supaya ukuran akhir tetap presisi byte-exact.
3. Shell script itu format teks, jadi padding-nya gak ikut dikompres dan ukuran akhir tetap presisi byte-exact.

### Keamanan

Script ini sengaja dibuat aman:
- Tidak ada `rm`, `mv`, `chmod`, `chown`, atau file manipulation
- Tidak ada `curl`, `wget`, `nc`, `ssh`, atau network access
- Tidak ada `sudo`, `su`, atau privilege escalation
- Tidak ada `eval`, `exec`, `source`, atau dynamic code execution
- Tidak ada process kill atau fork bomb
- Hanya print teks ke stdout
- Cocok untuk testing upload manager, file browser, MIME detection, dan validasi ukuran file

## Uninstall

Tidak perlu uninstall apapun, karena gak ada dependency eksternal.

## Disclaimer

Kode di repo ini dibuat dengan bantuan **Claude Sonnet 5** (Anthropic).

## License

MIT