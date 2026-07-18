# Dummy PDF & XLSX Generator

Project buat generate dummy PDF dan XLSX berukuran presisi (byte-exact) untuk keperluan testing upload/download, testing batas ukuran file, dan skenario cloud storage lainnya.

## Quick Start

- **PDF Generator**: Lihat [pdf/README.md](pdf/README.md)
- **XLSX Generator**: Lihat [xlsx/README.md](xlsx/README.md)
- **CSV Generator**: Lihat [csv/README.md](csv/README.md)
- **JSON Generator**: Lihat [json/README.md](json/README.md)
- **SVG Generator**: Lihat [svg/README.md](svg/README.md)
- **ZIP Generator**: Lihat [zip/README.md](zip/README.md)
- **WEBP Generator**: Lihat [webp/README.md](webp/README.md)
- **R2 Bulk Upload**: Lihat [r2_bulk_upload/README.md](r2_bulk_upload/README.md)

## Project Structure

```
dummy-pdf-generator/
├── README.md                      # File ini
├── r2_upload.sh                   # Script buat upload file ke R2
├── pdf/
│   ├── generate_dummy_pdf.py      # PDF generator
│   └── README.md                  # Dokumentasi PDF
├── xlsx/
│   └── generate_dummy_xlsx.py     # XLSX generator
├── csv/
│   └── generate_dummy_csv.py      # CSV generator
├── json/
│   ├── generate_dummy_json.py     # JSON generator
│   └── README.md                  # Dokumentasi JSON
├── svg/
│   ├── generate_dummy_svg.py      # SVG generator
│   └── README.md                  # Dokumentasi SVG
├── zip/
│   ├── generate_dummy_zip.py      # ZIP generator
│   └── README.md                  # Dokumentasi ZIP
├── webp/
│   ├── generate_dummy_webp.py     # WEBP generator
│   └── README.md                  # Dokumentasi WEBP
└── r2_bulk_upload/
    ├── r2_upload.sh               # Script upload bulk ke R2
    └── README.md                  # Dokumentasi R2 Upload
```

## Fitur

- Generate file PDF, XLSX, CSV, JSON, SVG, ZIP, dan WEBP valid dengan ukuran byte presisi
- Test upload/download dengan ukuran file yang tepat
- Test batas ukuran file
- Kompatibel dengan cloud storage (R2, S3, dll)
- Semua file valid dan bisa dibuka di reader standar

## Requirements

- Python 3.8+
- pikepdf, reportlab (untuk PDF)
- openpyxl (untuk XLSX)
- Standard library (untuk CSV, JSON, SVG, ZIP, WEBP)

## Installation

Lihat dokumentasi generator spesifik untuk instruksi instalasi detail.

### CSV Generator
Tidak butuh dependency eksternal, hanya Python standard library.

### PDF Generator
```
pip install pikepdf reportlab
```

### XLSX Generator
```
pip install openpyxl
```

## License

MIT