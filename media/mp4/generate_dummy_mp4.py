#!/usr/bin/env python3
"""
generate_dummy_mp4.py

Generate dummy file MP4 (.mp4) buat testing upload, preview, dan size validation.
Video berisi:
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
"""

import argparse
import os
import random
import re
import shutil
import subprocess
import tempfile
from typing import Dict, List, Tuple

DEFAULT_SIZES = [
    "1mb",
    "2mb",
    "3mb",
    "5mb",
    "7mb",
    "10mb",
    "15mb",
    "25mb",
    "35mb",
    "50mb",
]

MAX_DEFAULT_COUNT = 10
DEFAULT_MAX_SIZE_LABEL = "50mb"

TITLE_TEXT = "contohnya.web.id"
SUBTITLE_CHOICES = [
    "dummy file",
    "testing upload",
    "preview validation",
    "sample media file",
    "safe generated video",
    "dummy content for testing",
]

MAX_ATTEMPTS = 8


def parse_size(s: str, binary: bool = False) -> int:
    s = s.strip().lower()
    m = re.match(r"^([\d.]+)\s*(b|kb|mb|gb)?$", s)
    if not m:
        raise ValueError(f"Gak ngerti format ukuran: {s}")
    num, unit = m.groups()
    num = float(num)
    base = 1024 if binary else 1000
    mult = {None: 1, "b": 1, "kb": base, "mb": base**2, "gb": base**3}[unit]
    return int(num * mult)


def format_label(label: str) -> str:
    m = re.match(r"^([\d.]+)\s*(b|kb|mb|gb)$", label.strip().lower())
    if not m:
        return label.strip()
    num, unit = m.groups()
    return f"{num}{unit.upper()}"


def build_default_targets(binary: bool = False) -> Dict[str, int]:
    return {label: parse_size(label, binary=binary) for label in DEFAULT_SIZES}


def filtered_default_labels(max_size_label: str, count: int, binary: bool = False) -> List[str]:
    max_bytes = parse_size(max_size_label, binary=binary)
    labels = [label for label in DEFAULT_SIZES if parse_size(label, binary=binary) <= max_bytes]
    if not labels:
        raise ValueError("Tidak ada default size yang <= --max-size")
    return labels[:count]


def resolve_targets(args) -> List[Tuple[str, int]]:
    if args.sizes:
        labels = [x.strip() for x in args.sizes.split(",") if x.strip()]
        if len(labels) > MAX_DEFAULT_COUNT:
            raise ValueError(f"Maksimal {MAX_DEFAULT_COUNT} ukuran per generate.")
        return sorted(
            [(label.lower(), parse_size(label, binary=args.binary)) for label in labels],
            key=lambda kv: kv[1],
        )

    labels = filtered_default_labels(args.max_size, args.count, binary=args.binary)
    table = build_default_targets(binary=args.binary)
    return [(label, table[label]) for label in labels]


def ensure_ffmpeg():
    if shutil.which("ffmpeg") and shutil.which("ffprobe"):
        return
    msg = (
        "Error: ffmpeg/ffprobe gak ketemu di PATH.\n"
        "Install dulu ffmpeg:\n"
        "- Ubuntu/Debian: sudo apt install ffmpeg\n"
        "- macOS (Homebrew): brew install ffmpeg\n"
        "- Windows: download ffmpeg lalu tambahin ke PATH\n"
    )
    raise SystemExit(msg)


def escape_drawtext(text: str) -> str:
    return text.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")


def choose_profile(target_size: int):
    if target_size <= 120_000:
        return {
            "duration": 2.2,
            "audio_bitrate": 24000,
            "width": 640,
            "height": 360,
            "fps": 24,
            "tolerance": 6000,
            "min_video_bitrate": 18000,
            "container_overhead": 18000,
        }
    if target_size <= 300_000:
        return {
            "duration": 3.5,
            "audio_bitrate": 32000,
            "width": 854,
            "height": 480,
            "fps": 24,
            "tolerance": 12000,
            "min_video_bitrate": 24000,
            "container_overhead": 24000,
        }
    if target_size <= 1_000_000:
        return {
            "duration": 5.0,
            "audio_bitrate": 48000,
            "width": 960,
            "height": 540,
            "fps": 25,
            "tolerance": 20000,
            "min_video_bitrate": 40000,
            "container_overhead": 36000,
        }
    return {
        "duration": 8.0,
        "audio_bitrate": 96000,
        "width": 1280,
        "height": 720,
        "fps": 30,
        "tolerance": 32000,
        "min_video_bitrate": 60000,
        "container_overhead": 64000,
    }


def build_filter_complex(seed: int, subtitle: str, width: int, height: int, fps: int, duration: float) -> str:
    random.seed(seed)
    c1 = f"0x{random.randint(0x223344, 0x88ccff):06x}"
    c2 = f"0x{random.randint(0x331122, 0xff6699):06x}"
    c3 = f"0x{random.randint(0x112233, 0x66ff99):06x}"
    title = escape_drawtext(TITLE_TEXT)
    subtitle = escape_drawtext(subtitle)

    title_fontsize = max(28, int(width * 0.044))
    subtitle_fontsize = max(16, int(width * 0.022))
    footer_fontsize = max(12, int(width * 0.015))

    title_fade_out = max(0.8, duration - 0.8)
    subtitle_fade_out = max(0.7, duration - 0.7)
    footer_fade_out = max(0.8, duration - 0.9)

    return (
        f"color=c={c1}:s={width}x{height}:d={duration}:r={fps}[base];"
        f"nullsrc=s={width}x{height}:d={duration}:r={fps},"
        f"geq=r='128+90*sin((X+T*120)/70)':g='128+90*sin((Y+T*95)/80)':b='128+90*sin((X+Y+T*110)/90)',"
        f"boxblur=8:2[plasma];"
        f"nullsrc=s={width}x{height}:d={duration}:r={fps},"
        f"geq=r='100+80*sin(hypot(X-W/2,Y-H/2)/18-T*2)':g='80+70*sin(X/35+T*1.7)':b='140+90*sin(Y/28+T*1.2)',"
        f"boxblur=12:2[wave];"
        f"[base][plasma]blend=all_mode=screen:all_opacity=0.45[tmp1];"
        f"[tmp1][wave]blend=all_mode=addition:all_opacity=0.35[tmp2];"
        f"[tmp2]eq=saturation=1.25:contrast=1.08,format=yuv420p[bg];"
        f"[bg]"
        f"drawbox=x='mod(t*90,{width})-180':y={int(height*0.11)}:w={max(120, int(width*0.14))}:h={max(120, int(height*0.75))}:color={c2}@0.18:t=fill,"
        f"drawbox=x='{width}-mod(t*120,{width+220})':y={int(height*0.17)}:w={max(140, int(width*0.17))}:h={max(120, int(height*0.66))}:color={c3}@0.15:t=fill,"
        f"drawtext=text='{title}':fontcolor=white:fontsize={title_fontsize}:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
        f"x='(w-text_w)/2+sin(t*2.2)*18':y='h*0.34+sin(t*3.0)*10':"
        f"alpha='if(lt(t,0.4),t/0.4,if(lt(t,{title_fade_out}),1,({duration}-t)/0.8))',"
        f"drawtext=text='{subtitle}':fontcolor=white:fontsize={subtitle_fontsize}:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:"
        f"x='(w-text_w)/2':y='h*0.52+cos(t*2.6)*8':"
        f"alpha='if(lt(t,0.7),0,if(lt(t,1.2),(t-0.7)/0.5,if(lt(t,{subtitle_fade_out}),1,({duration}-t)/0.7)))',"
        f"drawtext=text='generated safe dummy file':fontcolor=white@0.85:fontsize={footer_fontsize}:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:"
        f"x='(w-text_w)/2':y='h*0.62+sin(t*1.8)*6':"
        f"alpha='if(lt(t,1.1),0,if(lt(t,1.7),(t-1.1)/0.6,if(lt(t,{footer_fade_out}),1,({duration}-t)/0.9)))'[v]"
    )


def generate_mp4_near_target(out_path: str, target_size: int, seed: int) -> int:
    profile = choose_profile(target_size)
    duration = profile["duration"]
    audio_bitrate = profile["audio_bitrate"]
    width = profile["width"]
    height = profile["height"]
    fps = profile["fps"]
    tolerance = profile["tolerance"]
    min_video_bitrate = profile["min_video_bitrate"]
    container_overhead = profile["container_overhead"]

    subtitle = SUBTITLE_CHOICES[seed % len(SUBTITLE_CHOICES)]
    usable = max(40_000, target_size - container_overhead)
    video_bitrate = max(min_video_bitrate, int((usable * 8 / duration) - audio_bitrate))

    best_actual = None
    best_blob = None
    best_diff = None

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_mp4 = os.path.join(tmpdir, "temp.mp4")

        for _ in range(MAX_ATTEMPTS):
            filter_complex = build_filter_complex(seed, subtitle, width, height, fps, duration)
            cmd = [
                "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                "-f", "lavfi", "-i", f"anullsrc=r=48000:cl=stereo:d={duration}",
                "-filter_complex", filter_complex,
                "-map", "[v]",
                "-map", "0:a",
                "-t", str(duration),
                "-r", str(fps),
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-preset", "medium",
                "-b:v", str(video_bitrate),
                "-maxrate", str(max(int(video_bitrate * 1.10), min_video_bitrate)),
                "-bufsize", str(max(video_bitrate * 2, 120000)),
                "-g", str(fps * 2),
                "-c:a", "aac",
                "-b:a", str(audio_bitrate),
                "-movflags", "+faststart",
                tmp_mp4,
            ]
            subprocess.run(cmd, check=True)
            actual = os.path.getsize(tmp_mp4)
            diff = actual - target_size

            if best_diff is None or abs(diff) < abs(best_diff):
                best_actual = actual
                best_diff = diff
                with open(tmp_mp4, "rb") as f:
                    best_blob = f.read()

            if abs(diff) <= tolerance:
                break

            ratio = target_size / max(actual, 1)
            if actual < target_size:
                video_bitrate = max(min_video_bitrate, int(video_bitrate * max(1.05, ratio)))
            else:
                video_bitrate = max(min_video_bitrate, int(video_bitrate * min(0.95, ratio)))

        with open(out_path, "wb") as f:
            f.write(best_blob)

    return best_actual


def main():
    parser = argparse.ArgumentParser(description="Generate dummy MP4 ukuran mendekati target.")
    parser.add_argument(
        "--sizes",
        type=str,
        default=None,
        help="Comma-separated ukuran custom, misal '500kb,1mb,5mb'. Maks 10 ukuran.",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=MAX_DEFAULT_COUNT,
        help="Jumlah varian default yang digenerate. Maks 10. Default 10.",
    )
    parser.add_argument(
        "--max-size",
        type=str,
        default=DEFAULT_MAX_SIZE_LABEL,
        help="Batas size terbesar untuk varian default. Default 50mb.",
    )
    parser.add_argument("--outdir", type=str, default=".", help="Folder output.")
    parser.add_argument("--prefix", type=str, default="Contohnya-MP4", help="Prefix nama file output.")
    parser.add_argument(
        "--binary",
        action="store_true",
        help="Pakai definisi binary (1 MB = 1024x1024 bytes) instead of decimal.",
    )
    args = parser.parse_args()

    if args.count < 1:
        raise ValueError("--count minimal 1")
    if args.count > MAX_DEFAULT_COUNT:
        raise ValueError(f"--count maksimal {MAX_DEFAULT_COUNT}")

    ensure_ffmpeg()
    os.makedirs(args.outdir, exist_ok=True)
    targets = resolve_targets(args)

    print(f"Generating {len(targets)} dummy MP4 files...\n")

    for idx, (raw_label, target_size) in enumerate(targets):
        pretty = format_label(raw_label)
        filename = f"{args.prefix}-{pretty}.mp4"
        filepath = os.path.join(args.outdir, filename)
        actual_size = generate_mp4_near_target(filepath, target_size, seed=idx + 1)
        diff = actual_size - target_size

        profile = choose_profile(target_size)
        tolerance = profile["tolerance"]
        status = "OK-ish" if abs(diff) <= tolerance else f"diff {diff:+d} bytes"

        print(
            f"{filename:20s} target={target_size:>10,} B "
            f"actual={actual_size:>10,} B ({status})"
        )

    print(f"\nDone. Files saved to {args.outdir}/")


if __name__ == "__main__":
    main()
