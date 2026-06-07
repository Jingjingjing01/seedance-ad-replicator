#!/usr/bin/env python3
"""Split a video into requested time ranges using ffmpeg."""

import argparse
import subprocess
from pathlib import Path


def parse_time(value: str) -> float:
    value = value.strip()
    if ":" not in value:
        return float(value)

    parts = [float(part) for part in value.split(":")]
    if len(parts) == 2:
        minutes, seconds = parts
        return minutes * 60 + seconds
    if len(parts) == 3:
        hours, minutes, seconds = parts
        return hours * 3600 + minutes * 60 + seconds
    raise ValueError(f"Invalid timestamp: {value}")


def parse_segments(raw: str) -> list[tuple[float, float]]:
    segments = []
    for item in raw.split(","):
        if not item.strip():
            continue
        if "-" not in item:
            raise ValueError(f"Segment must be start-end: {item}")
        start_raw, end_raw = item.split("-", 1)
        start = parse_time(start_raw)
        end = parse_time(end_raw)
        if end <= start:
            raise ValueError(f"Segment end must be after start: {item}")
        if end - start >= 15:
            raise ValueError(f"Segment must be under 15 seconds: {item}")
        segments.append((start, end))
    if not segments:
        raise ValueError("No segments provided")
    return segments


def main() -> None:
    parser = argparse.ArgumentParser(description="Split video into sub-15s clips with ffmpeg.")
    parser.add_argument("video", help="Source video path")
    parser.add_argument("--segments", required=True, help="Comma-separated ranges, e.g. '0-8.5,8.5-14.8'")
    parser.add_argument("--out-dir", default="segments", help="Output directory")
    parser.add_argument("--reencode", action="store_true", help="Re-encode for more accurate cuts")
    args = parser.parse_args()

    video = Path(args.video).expanduser().resolve()
    if not video.exists():
        raise FileNotFoundError(f"Video not found: {video}")

    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    segments = parse_segments(args.segments)

    for index, (start, end) in enumerate(segments, start=1):
        duration = end - start
        output = out_dir / f"segment_{index:02d}_{start:.1f}-{end:.1f}{video.suffix}"
        cmd = ["ffmpeg", "-y", "-ss", f"{start:.3f}", "-i", str(video), "-t", f"{duration:.3f}"]
        if args.reencode:
            cmd += ["-c:v", "libx264", "-c:a", "aac"]
        else:
            cmd += ["-c", "copy"]
        cmd.append(str(output))
        subprocess.run(cmd, check=True)
        print(output)


if __name__ == "__main__":
    main()
