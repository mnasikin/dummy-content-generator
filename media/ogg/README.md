# generate-dummy-ogg

Script Python buat generate dummy file OGG (.ogg) untuk testing upload, preview, dan size validation.

File yang dihasilkan tetap OGG valid (bisa dibuka di player audio mana pun), dan isinya beneran audio dengan melodi yang berbeda-beda (arpeggio pentatonic scale).

OGG/Vorbis gak bisa byte-exact 100% kayak WAV karena hasil akhirnya dipengaruhi encoding lossy, bitrate/quality behavior encoder, dan overhead container. Script ini pakai pendekatan ukur-dan-koreksi durasi WAV sumber lalu encode ulang pakai ffmpeg supaya hasil OGG mendekati target size.

## Requirements

- Python 3.8+
- ffmpeg terinstall di sistem

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
# generate 10 varian ukuran default (10KB s/d 10MB)
python3 generate_dummy_ogg.py

# generate ukuran tertentu aja
python3 generate_dummy_ogg.py --sizes 10kb,50kb,100kb,500kb

# ukuran custom yang gak ada di default
python3 generate_dummy_ogg.py --sizes 1mb,2mb,3mb,5mb,7mb,10mb

# ganti folder output
python3 generate_dummy_ogg.py --outdir ./ogg

# ganti prefix nama file (default: Contohnya-OGG)
python3 generate_dummy_ogg.py --prefix MyAudio

# ganti jumlah varian default (default: 10)
python3 generate_dummy_ogg.py --count 5

# ganti batas size terbesar (default: 10mb)
python3 generate_dummy_ogg.py --max-size 5mb

# ganti bitrate (default: 192k)
python3 generate_dummy_ogg.py --bitrate 256k

# pakai definisi binary (1 MB = 1024x1024 bytes) instead of decimal (default)
python3 generate_dummy_ogg.py --sizes 10mb --binary
```

### Ukuran default

`10KB, 50KB, 100KB, 500KB, 1MB, 2MB, 3MB, 5MB, 7MB, 10MB`

Nama file output ikut pattern `{prefix}-{label}.ogg`, misal `Contohnya-OGG-10kb.ogg`, `Contohnya-OGG-10mb.ogg`.

### Decimal vs Binary

Default script ini pakai definisi **decimal** (1 KB = 1.000 bytes, 1 MB = 1.000.000 bytes), sesuai gimana kebanyakan file manager/browser/dashboard cloud storage (R2, S3, dll) nampilin ukuran file. Kalau butuh definisi **binary/KiB-MiB** (1 KB = 1024 bytes), pakai flag `--binary`.

### Cara kerja (singkat)

1. Hitung durasi estimasi berdasarkan target size dan bitrate
2. Generate WAV sumber dengan melodi arpeggio pentatonic scale
3. Encode WAV ke OGG pakai ffmpeg dengan libvorbis encoder
4. Hitung ukuran OGG hasil, kalau deviasi > 4096 bytes, adjust durasi dan ulangi (maks 10 attempts)
5. File WAV sementara otomatis dihapus setelah proses convert selesai

### Struktur audio

- Sample rate: 44100 Hz
- Channels: 1 (mono)
- Sample width: 16-bit PCM
- Amplitude: 16000 (headroom di bawah 32767 biar ga clipping)
- Segment duration: 0.4 detik per nada
- Fade in/out: 8ms per segmen
- Scale: C4 pentatonic (261.63, 293.66, 329.63, 392.00, 440.00, 523.25, 587.33, 659.25 Hz)
- Bitrate: 192k (CBR)
- Max attempts: 10
- Deviasi toleransi: 4096 bytes

### Presisi ukuran

OGG gak bisa 100% byte-exact karena:
- Encoding lossy (Vorbis compression)
- Container/stream overhead
- Frame structure dan metadata

Tapi script ini mendekati target dengan deviasi maksimal 4096 bytes (sekitar 4KB), yang cukup presisi untuk kebanyakan testing.

### Keamanan

Script ini sengaja dibuat aman:
- Tidak ada network access (kecuali ffmpeg)
- Tidak ada file I/O yang berbahaya
- Hanya generate audio data yang aman
- Cocok untuk testing upload manager, file browser, MIME detection, dan validasi ukuran file

## Uninstall

Tidak perlu uninstall apapun, karena gak ada dependency eksternal selain ffmpeg.

## Disclaimer

Kode di repo ini dibuat dengan bantuan **Claude Sonnet 5** (Anthropic).

## License

MIT