# generate-dummy-mp4

Script Python buat generate dummy file MP4 (.mp4) untuk testing upload, preview, dan size validation.

Video yang dihasilkan berisi:
- judul animasi: contohnya.web.id
- subjudul/keterangan animasi
- background animasi abstrak dengan gerakan acak ringan

Catatan:
- Butuh ffmpeg + ffprobe terinstall di sistem.
- Output MP4 disimpan di folder yang sama dengan script, kecuali lo set --outdir.
- Ukuran file MP4 gak bisa byte-exact 100% karena dipengaruhi encoder video,
  audio, GOP, frame complexity, dan container overhead.
- Script ini pakai profile adaptif untuk file kecil dan koreksi bitrate supaya
  hasil lebih mendekati target.

## Requirements

- Python 3.8+
- ffmpeg + ffprobe terinstall di sistem

## Install

### Install ffmpeg

**Ubuntu/Debian:**
```bash
sudo apt install ffmpeg
```

**macOS (Homebrew):**
```bash
brew install ffmpeg
```

**Windows:**
Download ffmpeg lalu tambahkan ke PATH

### Python

Tidak perlu install apapun, cuma butuh Python 3.8+ yang terinstall di sistem.

## Usage

```bash
# generate 10 varian ukuran default (1MB s.d 50MB)
python3 generate_dummy_mp4.py

# generate ukuran tertentu aja
python3 generate_dummy_mp4.py --sizes 1mb,2mb,5mb,10mb,25mb

# ukuran custom yang gak ada di default
python3 generate_dummy_mp4.py --sizes 3mb,7mb,15mb,35mb

# ganti folder output
python3 generate_dummy_mp4.py --outdir ./mp4

# ganti jumlah varian default (default: 10)
python3 generate_dummy_mp4.py --count 5

# ganti batas size terbesar (default: 50mb)
python3 generate_dummy_mp4.py --max-size 25mb

# ganti prefix nama file (default: Contohnya-MP4)
python3 generate_dummy_mp4.py --prefix MyVideo

# pakai definisi binary (1 MB = 1024x1024 bytes) instead of decimal (default)
python3 generate_dummy_mp4.py --sizes 10mb --binary
```

### Ukuran default

`1MB, 2MB, 3MB, 5MB, 7MB, 10MB, 15MB, 25MB, 35MB, 50MB`

Nama file output ikut pattern `{prefix}-{label}.mp4`, misal `Contohnya-MP4-1mb.mp4`, `Contohnya-MP4-50mb.mp4`.

### Decimal vs Binary

Default script ini pakai definisi **decimal** (1 MB = 1.000.000 bytes), sesuai gimana kebanyakan file manager/browser/dashboard cloud storage (R2, S3, dll) nampilin ukuran file. Kalau butuh definisi **binary/MiB** (1 MB = 1024x1024 bytes), pakai flag `--binary`.

### Cara kerja (singkat)

1. Pilih profile adaptif berdasarkan target size (durasi, resolusi, fps, bitrate)
2. Generate background animasi abstrak dengan filter_complex (plasma + wave + box)
3. Tambahkan teks animasi (judul, subjudul, footer) dengan drawtext
4. Encode video dengan libx264, audio dengan AAC, pakai preset medium
5. Hitung ukuran MP4 hasil, kalau deviasi > tolerance, adjust bitrate dan ulangi (maks 8 attempts)

### Struktur video

**Profile adaptif:**
- 1-120KB: 640x360, 24fps, 2.2s, 24kbps audio
- 120-300KB: 854x480, 24fps, 3.5s, 32kbps audio
- 300KB-1MB: 960x540, 25fps, 5.0s, 48kbps audio
- 1MB+: 1280x720, 30fps, 8.0s, 96kbps audio

**Teknologi:**
- Video codec: H.264 (libx264)
- Pixel format: yuv420p
- Audio codec: AAC
- Audio sample rate: 48000 Hz
- Audio channels: stereo
- GOP: 2x fps
- Preset: medium
- Fast start: enabled
- Tolerance: 6-32KB tergantung profile

**Visual:**
- Background: Plasma + wave dengan blend mode
- Animasi: Gerakan acak ringan dengan box blur
- Teks: Judul "contohnya.web.id", subjudul, footer
- Font: DejaVuSans/DejaVuSans-Bold

### Presisi ukuran

MP4 gak bisa 100% byte-exact karena:
- Encoding lossy (H.264 compression)
- Audio codec overhead
- GOP structure dan frame complexity
- Container overhead

Tapi script ini mendekati target dengan deviasi maksimal 32KB (tergantung profile), yang cukup presisi untuk kebanyakan testing.

### Keamanan

Script ini sengaja dibuat aman:
- Tidak ada network access (kecuali ffmpeg)
- Tidak ada file I/O yang berbahaya
- Hanya generate video data yang aman
- Cocok untuk testing upload manager, file browser, MIME detection, dan validasi ukuran file

## Uninstall

Tidak perlu uninstall apapun, karena gak ada dependency eksternal selain ffmpeg.

## Disclaimer

Kode di repo ini dibuat dengan bantuan **Claude Sonnet 5** (Anthropic).

## License

MIT