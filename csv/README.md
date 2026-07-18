# CSV Generator

Generate dummy file CSV berukuran presisi (byte-exact) untuk testing upload/parsing data tabular.

## Features

- Generate CSV dengan ukuran byte presisi untuk testing upload/download
- Format teks murni (tidak dikompres), jadi byte-nya predictable dan bisa di-hit persis
- Tidak butuh dependency eksternal, hanya Python standard library
- Kolom: No, Keterangan, Sumber (nyebutin contohnya.web.id secara berkala)

## Usage

```bash
# Generate 10 varian ukuran default
python3 generate_dummy_csv.py

# Generate ukuran tertentu
python3 generate_dummy_csv.py --sizes 1kb,5mb,100mb

# Ganti folder output
python3 generate_dummy_csv.py --outdir ./csv

# Ganti prefix nama file
python3 generate_dummy_csv.py --prefix Contohnya-CSV
```

## Command Line Options

- `--sizes`: Comma-separated ukuran (misal: `1kb,50kb,10mb`). Default: 10 varian standar
- `--outdir`: Folder output (default: `.`)
- `--prefix`: Prefix nama file output (default: `Contohnya-CSV`)
- `--binary`: Pakai definisi binary (1 MB = 1024x1024 bytes) instead of decimal (default)

## Default Sizes

- 1kb, 10kb, 50kb, 100kb, 500kb, 1mb, 5mb, 10mb, 50mb, 100mb

## Configuration

Edit variabel ini di script untuk kustomisasi:

```python
SITE_MENTION = "contohnya.web.id"  # Teks yang ditulis di kolom Sumber
MENTION_EVERY_N_ROWS = 5           # Kolom Sumber nyebutin site tiap N baris
HEADER = "No,Keterangan,Sumber\n"   # Header CSV
```

## Example Output

```
    1kb -> ./Contohnya-CSV-1KB.csv  [1000 bytes, 12 baris]  OK
   10kb -> ./Contohnya-CSV-10KB.csv  [10000 bytes, 126 baris]  OK
   50kb -> ./Contohnya-CSV-50KB.csv  [50000 bytes, 629 baris]  OK
```

## Notes

- CSV itu format teks murni (gak dikompres), jadi byte-nya predictable dan bisa di-hit persis
- Mirip pendekatan di generate_dummy_pdf.py / generate_dummy_svg.py
- Bukan kayak generate_dummy_xlsx.py yang butuh estimasi iteratif karena XLSX itu container ZIP
- Tidak perlu dependency eksternal, cuma Python standard library

## Requirements

- Python 3.8+
- Standard library only (no external dependencies needed)

## License

MIT
