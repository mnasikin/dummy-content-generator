# generate-dummy-wav

Script Python buat generate dummy WAV audio berukuran presisi (byte-exact) untuk keperluan testing upload/download/parsing audio.

File yang dihasilkan tetap WAV valid (bisa dibuka di player audio mana pun), dan isinya beneran audio PCM 16-bit dengan melodi yang berbeda-beda (arpeggio pentatonic scale).

WAV = raw PCM + 44-byte header, jadi size-nya byte-exact ke target (pakai basis desimal 1 kB = 1000 byte, 1 MB = 1.000.000 byte, biar match sama angka yang ditunjukin file explorer/OS pada umumnya).

Gak butuh dependency eksternal, cuma Python standard library.

## Requirements

- Python 3.8+

## Install

Tidak perlu install apapun, cuma butuh Python 3.8+ yang terinstall di sistem.

## Usage

```bash
# generate 10 varian ukuran default (10KB s/d 10MB)
python3 generate_dummy_wav.py

# generate ukuran tertentu aja
python3 generate_dummy_wav.py --sizes 10kb,50kb,100kb,500kb

# ukuran custom yang gak ada di default
python3 generate_dummy_wav.py --sizes 1mb,2mb,3mb,5mb,7mb,10mb

# ganti folder output
python3 generate_dummy_wav.py --outdir ./wav

# ganti prefix nama file (default: dummy)
python3 generate_dummy_wav.py --prefix MyAudio

# pakai definisi binary (1 MB = 1024x1024 bytes) instead of decimal (default)
python3 generate_dummy_wav.py --sizes 10mb --binary
```

### Ukuran default

`10KB, 50KB, 100KB, 500KB, 1MB, 2MB, 3MB, 5MB, 7MB, 10MB`

Nama file output ikut pattern `{prefix}-{label}.wav`, misal `dummy_10kb.wav`, `dummy_10mb.wav`.

### Decimal vs Binary

Default script ini pakai definisi **decimal** (1 KB = 1.000 bytes, 1 MB = 1.000.000 bytes), sesuai gimana kebanyakan file manager/browser/dashboard cloud storage (R2, S3, dll) nampilin ukuran file. Kalau butuh definisi **binary/KiB-MiB** (1 KB = 1024 bytes), pakai flag `--binary`.

### Cara kerja (singkat)

1. Hitung jumlah sample yang dibutuhkan berdasarkan target size (data bytes = target - 44 byte header)
2. Generate melodi arpeggio pentatonic scale (naik-turun) dengan fade in/out tiap segmen
3. Setiap file mulai dari nada awal yang berbeda, jadi antar file kedengeran beda
4. WAV itu format raw PCM, jadi ukuran akhir tetap presisi byte-exact

### Struktur audio

- Sample rate: 44100 Hz
- Channels: 1 (mono)
- Sample width: 16-bit PCM
- Amplitude: 16000 (headroom di bawah 32767 biar ga clipping)
- Segment duration: 0.4 detik per nada
- Fade in/out: 8ms per segmen
- Scale: C4 pentatonic (261.63, 293.66, 329.63, 392.00, 440.00, 523.25, 587.33, 659.25 Hz)

### Keamanan

Script ini sengaja dibuat aman:
- Tidak ada network access
- Tidak ada file I/O yang berbahaya
- Hanya generate audio data yang aman
- Cocok untuk testing upload manager, file browser, MIME detection, dan validasi ukuran file

## Uninstall

Tidak perlu uninstall apapun, karena gak ada dependency eksternal.

## Disclaimer

Kode di repo ini dibuat dengan bantuan **Claude Sonnet 5** (Anthropic).

## License

MIT