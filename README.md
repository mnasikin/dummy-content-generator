# Dummy PDF & XLSX Generator

Project buat generate konten berukuran presisi (byte-exact) untuk keperluan testing upload/download, testing batas ukuran file, dan skenario cloud storage lainnya.

**Kalo males generate, bisa download dummy content yang udah jadi di https://contohnya.web.id**

## Quick Start

- **PDF Generator**: Lihat [dokumen/pdf/README.md](dokumen/pdf/README.md)
- **XLSX Generator**: Lihat [dokumen/xlsx/README.md](dokumen/xlsx/README.md)
- **DOCX Generator**: Lihat [dokumen/docx/README.md](dokumen/docx/README.md)
- **DOC Generator**: Lihat [dokumen/doc/README.md](dokumen/doc/README.md)
- **CSV Generator**: Lihat [data/csv/README.md](data/csv/README.md)
- **JSON Generator**: Lihat [data/json/README.md](data/json/README.md)
- **SQL Generator**: Lihat [data/sql/README.md](data/sql/README.md)
- **SVG Generator**: Lihat [gambar/svg/README.md](gambar/svg/README.md)
- **ZIP Generator**: Lihat [arsip/zip/README.md](arsip/zip/README.md)
- **WEBP Generator**: Lihat [gambar/webp/README.md](gambar/webp/README.md)
- **R2 Bulk Upload**: Lihat [r2_bulk_upload/README.md](r2_bulk_upload/README.md)
- **TAR Generator**: Lihat [arsip/tar/README.md](arsip/tar/README.md)

## Project Structure

```
dummy-pdf-generator/
├── README.md                      # File ini
├── r2_upload.sh                   # Script buat upload file ke R2
├── arsip/
│   ├── tar/
│   │   ├── generate_dummy_tar.py  # TAR generator
│   │   └── README.md              # Dokumentasi TAR
│   └── zip/
│       ├── generate_dummy_zip.py  # ZIP generator
│       └── README.md              # Dokumentasi ZIP
├── data/
│   ├── csv/
│   │   ├── generate_dummy_csv.py  # CSV generator
│   │   └── README.md              # Dokumentasi CSV
│   ├── json/
│   │   ├── generate_dummy_json.py # JSON generator
│   │   └── README.md              # Dokumentasi JSON
│   └── sql/
│       ├── generate_dummy_sql.py  # SQL generator
│       └── README.md              # Dokumentasi SQL
├── dokumen/
│   ├── doc/
│   │   ├── generate_dummy_doc.py  # DOC generator (legacy binary)
│   │   ├── build_docx.js          # Node.js script untuk build DOCX
│   │   └── README.md              # Dokumentasi DOC
│   ├── docx/
│   │   ├── generate_dummy_docx.py # DOCX generator
│   │   ├── build_docx.js          # Node.js script untuk build DOCX
│   │   └── README.md              # Dokumentasi DOCX
│   ├── pdf/
│   │   ├── generate_dummy_pdf.py  # PDF generator
│   │   └── README.md              # Dokumentasi PDF
│   └── xlsx/
│       ├── generate_dummy_xlsx.py # XLSX generator
│       └── README.md              # Dokumentasi XLSX
├── gambar/
│   ├── svg/
│   │   ├── generate_dummy_svg.py  # SVG generator
│   │   └── README.md              # Dokumentasi SVG
│   └── webp/
│       ├── generate_dummy_webp.py # WEBP generator
│       └── README.md              # Dokumentasi WEBP
└── r2_bulk_upload/
    ├── r2_upload.sh               # Script upload bulk ke R2
    └── README.md                  # Dokumentasi R2 Upload
```

## License

MIT