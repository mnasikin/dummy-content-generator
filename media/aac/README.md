# generate-dummy-aac

Script Python buat generate dummy AAC audio dengan ukuran mendekati target (tidak 100% byte-exact karena encoding lossy).

File yang dihasilkan tetap AAC valid (bisa dibuka di player audio mana pun), dan isinya beneran audio dengan melodi yang berbeda-beda (arpeggio pentatonic scale).

AAC juga gak bisa byte-exact 100% kayak WAV karena ada proses encoding lossy, bitrate, dan container/stream overhead. Script ini pakai pendekatan ukur-dan-koreksi durasi WAV sumber lalu encode ulang pakai ffmpeg (CBR-ish) supaya hasil AAC mendekati target size.

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
python3 generate_dummy_aac.py

# generate ukuran tertentu aja
python3 generate_dummy_aac.py --sizes 10kb,50kb,100kb,500kb

# ukuran custom yang gak ada di default
python3 generate_dummy_aac.py --sizes 1mb,2mb,3mb,5mb,7mb,10mb

# ganti folder output
python3 generate_dummy_aac.py --outdir ./aac

# ganti bitrate (default: 128k)
python3 generate_dummy_aac.py --bitrate 192k

# ganti prefix nama file (default: Contohnya-AAC)
python3 generate_dummy_aac.py --prefix MyAudio
```

### Ukuran default

`10KB, 50KB, 100KB, 500KB, 1MB, 2MB, 3MB, 5MB, 7MB, 10MB`

Nama file output ikut pattern `{prefix}-{label}.aac`, misal `Contohnya-AAC-10kb.aac`, `Contohnya-AAC-10mb.aac`.

### Decimal vs Binary

Default script ini pakai definisi **decimal** (1 KB = 1.000 bytes, 1 MB = 1.000.000 bytes), sesuai gimana kebanyakan file manager/browser/dashboard cloud storage (R2, S3, dll) nampilin ukuran file. Kalau butuh definisi **binary/KiB-MiB** (1 KB = 1024 bytes), pakai flag `--binary`.

### Cara kerja (singkat)

1. Hitung durasi estimasi berdasarkan target size dan bitrate
2. Generate WAV sumber dengan melodi arpeggio pentatonic scale
3. Encode WAV ke AAC pakai ffmpeg dengan bitrate CBR-ish
4. Hitung ukuran AAC hasil, kalau deviasi > 2048 bytes, adjust durasi dan ulangi (maks 8 attempts)
5. File WAV sementara otomatis dihapus setelah proses convert selesai

### Struktur audio

- Sample rate: 44100 Hz
- Channels: 1 (mono)
- Sample width: 16-bit PCM
- Amplitude: 16000 (headroom di bawah 32767 biar ga clipping)
- Segment duration: 0.4 detik per nada
- Fade in/out: 8ms per segmen
- Scale: C4 pentatonic (261.63, 293.66, 329.63, 392.00, 440.00, 523.25, 587.33, 659.25 Hz)
- Bitrate: 128k (CBR-ish)
- Max attempts: 8
- Deviasi toleransi: 2048 bytes

### Presisi ukuran

AAC gak bisa 100% byte-exact karena:
- Encoding lossy (AAC compression)
- Container/stream overhead
- Frame structure dan metadata

Tapi script ini mendekati target dengan deviasi maksimal 2048 bytes (sekitar 2KB), yang cukup presisi untuk kebanyakan testing.

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