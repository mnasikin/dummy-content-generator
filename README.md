# Dummy Content Generator

Project buat generate konten berukuran presisi (byte-exact) untuk keperluan testing upload/download, testing batas ukuran file, dan skenario cloud storage lainnya.

**Kalo males generate, bisa download dummy content yang udah jadi di https://contohnya.web.id**

## Quick Start

- **PDF Generator**: Lihat [dokumen/pdf/README.md](dokumen/pdf/README.md)
- **XLSX Generator**: Lihat [dokumen/xlsx/README.md](dokumen/xlsx/README.md)
- **XLS Generator**: Lihat [dokumen/xls/README.md](dokumen/xls/README.md)
- **DOCX Generator**: Lihat [dokumen/docx/README.md](dokumen/docx/README.md)
- **DOC Generator**: Lihat [dokumen/doc/README.md](dokumen/doc/README.md)
- **CSV Generator**: Lihat [data/csv/README.md](data/csv/README.md)
- **JSON Generator**: Lihat [data/json/README.md](data/json/README.md)
- **SQL Generator**: Lihat [data/sql/README.md](data/sql/README.md)
- **XML Generator**: Lihat [data/xml/README.md](data/xml/README.md)
- **HTML Generator**: Lihat [script/html/README.md](script/html/README.md)
- **JS Generator**: Lihat [script/js/README.md](script/js/README.md)
- **PHP Generator**: Lihat [script/php/README.md](script/php/README.md)
- **PY Generator**: Lihat [script/py/README.md](script/py/README.md)
- **SH Generator**: Lihat [script/sh/README.md](script/sh/README.md)
- **TS Generator**: Lihat [script/ts/README.md](script/ts/README.md)
- **GIF Generator**: Lihat [gambar/gif/README.md](gambar/gif/README.md)
- **JPEG Generator**: Lihat [gambar/jpeg/README.md](gambar/jpeg/README.md)
- **JPG Generator**: Lihat [gambar/jpg/README.md](gambar/jpg/README.md)
- **PNG Generator**: Lihat [gambar/png/README.md](gambar/png/README.md)
- **SVG Generator**: Lihat [gambar/svg/README.md](gambar/svg/README.md)
- **WEBP Generator**: Lihat [gambar/webp/README.md](gambar/webp/README.md)
- **ZIP Generator**: Lihat [arsip/zip/README.md](arsip/zip/README.md)
- **R2 Bulk Upload**: Lihat [r2_bulk_upload/README.md](r2_bulk_upload/README.md)
- **TAR Generator**: Lihat [arsip/tar/README.md](arsip/tar/README.md)
- **TAR.GZ Generator**: Lihat [arsip/tar.gz/README.md](arsip/tar.gz/README.md)
- **7Z Generator**: Lihat [arsip/7z/README.md](arsip/7z/README.md)
- **RAR Generator**: Lihat [arsip/rar/README.md](arsip/rar/README.md)

## Project Structure

```
dummy-pdf-generator/
├── README.md                      # File ini
├── r2_upload.sh                   # Script buat upload file ke R2
├── arsip/
│   ├── tar/
│   │   ├── generate_dummy_tar.py  # TAR generator
│   │   └── README.md              # Dokumentasi TAR
│   ├── tar.gz/
│   │   ├── generate_dummy_targz.py  # TAR.GZ generator
│   │   └── README.md              # Dokumentasi TAR.GZ
│   ├── 7z/
│   │   ├── generate_dummy_7z.py  # 7Z generator
│   │   └── README.md              # Dokumentasi 7Z
│   ├── rar/
│   │   ├── generate_dummy_rar.py  # RAR generator
│   │   └── README.md              # Dokumentasi RAR
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
│   ├── php/
│   │   ├── generate_dummy_php.py  # PHP generator
│   │   └── README.md              # Dokumentasi PHP
│   ├── sql/
│   │   ├── generate_dummy_sql.py  # SQL generator
│   │   └── README.md              # Dokumentasi SQL
│   └── xml/
│       ├── generate_dummy_xml.py  # XML generator
│       └── README.md              # Dokumentasi XML
├── script/
│   └── html/
│       ├── generate_dummy_html.py  # HTML generator
│       └── README.md              # Dokumentasi HTML
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
│   ├── xls/
│   │   ├── generate_dummy_xls.py  # XLS generator (legacy binary)
│   │   └── README.md              # Dokumentasi XLS
│   ├── xlsx/
│   │   ├── generate_dummy_xlsx.py # XLSX generator
│   │   └── README.md              # Dokumentasi XLSX
├── gambar/
│   ├── gif/
│   │   ├── generate_dummy_gif.py  # GIF generator
│   │   └── README.md              # Dokumentasi GIF
│   ├── jpeg/
│   │   ├── generate_dummy_jpeg.py  # JPEG generator
│   │   └── README.md              # Dokumentasi JPEG
│   ├── jpg/
│   │   ├── generate_dummy_jpg.py  # JPG generator
│   │   └── README.md              # Dokumentasi JPG
│   ├── png/
│   │   ├── generate_dummy_png.py  # PNG generator
│   │   └── README.md              # Dokumentasi PNG
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
