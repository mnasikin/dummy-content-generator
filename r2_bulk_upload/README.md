# R2 Bulk Upload Script

Script bash untuk upload file dummy (PDF, XLSX, CSV, JSON, dll) ke Cloudflare R2 storage dengan Content-Disposition: attachment agar browser langsung download file (bukan preview).

## Features

- Upload bulk file dari folder lokal ke R2
- Content-Disposition: attachment header untuk force download
- Support multiple file types (xlsx, pdf, csv, json, dll)
- Simple configuration via environment variables
- Progress tracking per file

## Usage

```bash
# Bikin script executable (kalau belum)
chmod +x r2_upload.sh

# Upload file XLSX saja
./r2_upload.sh

# Upload file PDF saja
FILE_TYPE="pdf" ./r2_upload.sh

# Upload semua file type
FILE_TYPE="all" ./r2_upload.sh
```

## Configuration

Edit variabel ini di script:

```bash
BUCKET="bucketku"          # nama bucket R2
LOCAL_DIR="."                # folder lokal berisi file
REMOTE_PREFIX="dokumen/xlsx"  # path tujuan di R2
```

### Configuration Options

- **BUCKET**: Ganti nama bucket R2 yang ingin diupload
- **LOCAL_DIR**: Tentukan folder lokal yang berisi file dummy (default: current directory)
- **REMOTE_PREFIX**: Set path tujuan di R2 (default: dokumen/xlsx)
- **FILE_TYPE**: Filter file type untuk diupload (xlsx, pdf, csv, json, dll, atau "all" untuk semua)

## Editing the Script

Untuk kustomisasi perilaku upload, edit variabel di `r2_upload.sh`:

```bash
# Contoh kustomisasi
BUCKET="my-production-bucket"
LOCAL_DIR="./output"
REMOTE_PREFIX="uploads/dummy-files"
```

## Example Output

```
Uploading: Contohnya-XLSX-1MB.xlsx
Uploading: Contohnya-XLSX-10MB.xlsx
Uploading: Contohnya-PDF-1MB.pdf
Selesai. Total file: 3
```

## Prerequisites

- [Wrangler CLI](https://developers.cloudflare.com/workers/wrangler/) installed
- Bucket R2 sudah dikonfigurasi
- Cloudflare API credentials sudah di-setup
- File dummy sudah dibuat di folder lokal

### Install Wrangler

```bash
npm install -g wrangler
```

### Setup Cloudflare Credentials

```bash
wrangler login
```

## Notes

- Script ini upload file ke R2 dengan header `Content-Disposition: attachment`, memaksa browser untuk download file bukan preview
- Script hanya upload file yang cocok dengan pattern (misal: *.xlsx untuk file XLSX)
- Total file yang diupload ditampilkan di akhir
- Gunakan `set -e` untuk stop script jika ada error

## Integration with Generator Scripts

1. Generate dummy file:
   ```bash
   # Generate XLSX
   cd xlsx && python3 generate_dummy_xlsx.py
   
   # Generate PDF
   cd pdf && python3 generate_dummy_pdf.py
   
   # Generate CSV
   cd csv && python3 generate_dummy_csv.py
   
   # Generate JSON
   cd json && python3 generate_dummy_json.py
   ```

2. Upload ke R2:
   ```bash
   cd r2_bulk_upload
   ./r2_upload.sh
   ```

## License

MIT