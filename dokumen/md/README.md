# generate-dummy-md

Script Python buat generate dummy Markdown (.md) yang aman dan statis buat testing upload, preview, parsing, dan validasi ukuran file.

File yang dihasilkan tetap Markdown valid (bisa dibuka di editor teks atau markdown viewer mana pun, bukan cuma file random bytes yang dipaksa berekstensi `.md`), dan isinya beneran multi-element (bukan cuma 1 element + padding tersembunyi) — jumlah element menyesuaikan besar target ukuran.

Markdown itu format teks sederhana, jadi bisa di-padding byte-exact lewat estimasi + koreksi iteratif.

Gak butuh dependency eksternal, cuma Python standard library.

## Requirements

- Python 3.8+

## Install

Tidak butuh install apapun, cuma Python 3.8+ yang terinstall di sistem.

## Usage

```bash
# generate 10 varian ukuran default (10KB s/d 10MB)
python3 generate_dummy_md.py

# generate ukuran tertentu aja
python3 generate_dummy_md.py --sizes 10kb,25kb,100kb,1mb,10mb

# ukuran custom yang gak ada di default
python3 generate_dummy_md.py --sizes 250kb,2.5mb,777kb

# ganti folder output
python3 generate_dummy_md.py --outdir ./md

# ganti prefix nama file (default: Contohnya-MD)
python3 generate_dummy_md.py --prefix MyFile
```

### Ukuran default

`10KB, 25KB, 50KB, 100KB, 250KB, 500KB, 1MB, 2MB, 5MB, 10MB`

Nama file output ikut pattern `{prefix}-{ukuran}.md`, misal `Contohnya-MD-10KB.md`, `Contohnya-MD-10MB.md`.

### Decimal vs Binary

Default script ini pakai definisi **decimal** (1 KB = 1.000 bytes, 1 MB = 1.000.000 bytes), sesuai gimana kebanyakan file manager/browser/dashboard cloud storage (R2, S3, dll) nampilin ukuran file. Kalau butuh definisi **binary/KiB-MiB** (1 KB = 1024 bytes), pakai flag `--binary`.

### Kustomisasi teks di dalam Markdown

Edit langsung dua variabel ini di bagian atas file `generate_dummy_md.py`:

```python
TITLE = "Contohnya.web.id"
SUBTITLE = "Dummy Markdown File"
```

### Cara kerja (singkat)

1. Bikin base Markdown valid berisi konten teks asli (judul, subjudul, poin, tabel, kutipan) — jumlah element menyesuaikan besar target.
2. Kalau masih ada sisa gap ke ukuran target, ditambahin byte dummy lewat Lorem ipsum dan padding.
3. Markdown itu format teks sederhana, jadi padding-nya gak ikut dikompres dan ukuran akhir tetap presisi byte-exact.

## Uninstall

Tidak butuh uninstall apapun, karena gak ada dependency eksternal.

## Disclaimer

Kode di repo ini dibuat dengan bantuan **Claude Sonnet 5** (Anthropic).

## License

MIT