# JSON Generator

Generate dummy file JSON berukuran presisi (byte-exact) untuk testing upload/parsing data JSON.

## Features

- Generate JSON dengan ukuran byte presisi untuk testing upload/download
- Format teks murni (tidak dikompres), jadi byte-nya predictable dan bisa di-hit persis
- Tidak butuh dependency eksternal, hanya Python standard library
- Kolom: id, title, description, category, source (nyebutin contohnya.web.id secara berkala)

## Usage

```bash
# Generate 10 varian ukuran default
python3 generate_dummy_json.py

# Generate ukuran tertentu
python3 generate_dummy_json.py --sizes 1kb,5mb,100mb

# Ganti folder output
python3 generate_dummy_json.py --outdir ./json

# Ganti prefix nama file
python3 generate_dummy_json.py --prefix Contohnya-JSON

# Pakai definisi binary (1 MB = 1024x1024 bytes)
python3 generate_dummy_json.py --binary
```

## Command Line Options

- `--sizes`: Comma-separated ukuran (misal: `1kb,50kb,10mb`). Default: 10 varian standar
- `--outdir`: Folder output (default: `.`)
- `--prefix`: Prefix nama file output (default: `Contohnya-JSON`)
- `--binary`: Pakai definisi binary (1 MB = 1024x1024 bytes) instead of decimal (default)

## Default Sizes

- 1kb, 10kb, 50kb, 100kb, 500kb, 1mb, 5mb, 10mb, 50mb, 100mb

## Configuration

Edit variabel ini di script untuk kustomisasi:

```python
SITE_MENTION = "contohnya.web.id"  # Teks yang ditulis di kolom source
MENTION_EVERY_N_ITEMS = 5           # Kolom source nyebutin site tiap N item
HEADER = '{"metadata":{"generator":"Dummy JSON Generator","website":"' + SITE_MENTION + '"},"data":['  # Header JSON
```

## Example Output

```
    1kb -> ./Contohnya-JSON-1KB.json  [1000 bytes, 1 object]  OK
   10kb -> ./Contohnya-JSON-10KB.json  [10000 bytes, 10 objects]  OK
   50kb -> ./Contohnya-JSON-50KB.json  [50000 bytes, 50 objects]  OK
```

## Notes

- JSON itu format teks murni (gak dikompres), jadi byte-nya predictable dan bisa di-hit persis
- Mirip pendekatan di generate_dummy_csv.py / generate_dummy_svg.py
- Bukan kayak generate_dummy_xlsx.py yang butuh estimasi iteratif karena XLSX itu container ZIP
- Tidak perlu dependency eksternal, cuma Python standard library

## Requirements

- Python 3.8+
- Standard library only (no external dependencies needed)

## License

MIT