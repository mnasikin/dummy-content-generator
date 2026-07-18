#!/bin/bash
# upload-folder.sh
# Upload semua file di folder lokal ke R2, dengan Content-Disposition: attachment
# biar browser langsung download (bukan preview) pas diklik.

set -e

BUCKET="bucketku"          # nama bucket R2 lo
LOCAL_DIR="."                # folder lokal isi file PDF nya (ganti kalo perlu)
REMOTE_PREFIX="dokumen/xlsx"  # path tujuan di R2

for filepath in "$LOCAL_DIR"/*.xlsx; do
  filename=$(basename "$filepath")
  echo "Uploading: $filename"
  npx wrangler r2 object put "$BUCKET/$REMOTE_PREFIX/$filename" \
    --file="$filepath" \
    --content-disposition="attachment; filename=\"$filename\"" \
    --remote
done

echo "Selesai. Total file: $(ls "$LOCAL_DIR"/*.xlsx | wc -l)"
