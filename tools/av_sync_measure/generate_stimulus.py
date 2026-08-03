#!/usr/bin/env python3
"""Generate a flash+beep A/V sync stimulus video via ffmpeg + numpy."""

from __future__ import annotations

import argparse
import math
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np


def _write_wav_pcm16(path: Path, samples: np.ndarray, sample_rate: int) -> None:
    import wave

    clipped = np.clip(samples, -1.0, 1.0)
    pcm = (clipped * 32767.0).astype(np.int16)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm.tobytes())


def build_audio(
    duration_s: float,
    sample_rate: int,
    period_s: float,
    beep_s: float,
    beep_hz: float,
    first_marker_s: float,
) -> np.ndarray:
    n = int(round(duration_s * sample_rate))
    audio = np.zeros(n, dtype=np.float64)
    t = 0.0
    marker_t = first_marker_s
    while marker_t + beep_s <= duration_s + 1e-9:
        start = int(round(marker_t * sample_rate))
        length = int(round(beep_s * sample_rate))
        end = min(n, start + length)
        if start >= n:
            break
        idx = np.arange(end - start)
        tone = 0.9 * np.sin(2 * math.pi * beep_hz * (idx / sample_rate))
        # short cosine fade to avoid clicks
        fade = min(32, (end - start) // 4)
        if fade > 0:
            ramp = np.linspace(0.0, 1.0, fade)
            tone[:fade] *= ramp
            tone[-fade:] *= ramp[::-1]
        audio[start:end] += tone
        marker_t += period_s
        t = marker_t
    _ = t
    return audio


def build_gray_frames(
    duration_s: float,
    fps: int,
    width: int,
    height: int,
    period_s: float,
    flash_frames: int,
    first_marker_s: float,
) -> np.ndarray:
    n_frames = int(round(duration_s * fps))
    frames = np.full((n_frames, height, width), 16, dtype=np.uint8)
    marker_t = first_marker_s
    while marker_t < duration_s:
        start_f = int(round(marker_t * fps))
        for i in range(flash_frames):
            f = start_f + i
            if 0 <= f < n_frames:
                frames[f].fill(255)
        marker_t += period_s
    return frames


def encode_stimulus(
    output: Path,
    frames: np.ndarray,
    audio_wav: Path,
    fps: int,
    width: int,
    height: int,
) -> None:
    raw = frames.reshape(-1).tobytes()
    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "rawvideo",
        "-pix_fmt",
        "gray",
        "-s",
        f"{width}x{height}",
        "-r",
        str(fps),
        "-i",
        "pipe:0",
        "-i",
        str(audio_wav),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-shortest",
        str(output),
    ]
    proc = subprocess.run(cmd, input=raw, capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError(
            "ffmpeg failed to encode stimulus:\n"
            + proc.stderr.decode("utf-8", errors="replace")
        )


def delay_audio_copy(src: Path, dst: Path, delay_ms: float) -> None:
    """Create a receiver-like file where audio is delayed vs video."""
    # adelay expects ms for each channel
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(src),
        "-filter_complex",
        f"[0:a]adelay={delay_ms}|{delay_ms}[a]",
        "-map",
        "0:v",
        "-map",
        "[a]",
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        str(dst),
    ]
    proc = subprocess.run(cmd, capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError(
            "ffmpeg adelay failed:\n" + proc.stderr.decode("utf-8", errors="replace")
        )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, default=Path("stimulus_flash_beep.mp4"))
    p.add_argument("--duration", type=float, default=60.0, help="seconds")
    p.add_argument("--fps", type=int, default=30)
    p.add_argument("--width", type=int, default=640)
    p.add_argument("--height", type=int, default=360)
    p.add_argument("--period", type=float, default=4.0, help="marker period, seconds")
    p.add_argument("--first-marker", type=float, default=1.0, help="first marker time, s")
    p.add_argument("--beep-ms", type=float, default=60.0)
    p.add_argument("--beep-hz", type=float, default=1000.0)
    p.add_argument("--flash-frames", type=int, default=2)
    p.add_argument("--sample-rate", type=int, default=48000)
    p.add_argument(
        "--also-delayed",
        type=float,
        default=None,
        metavar="MS",
        help="also write a copy with audio delayed by MS (simulates slower voice path, e.g. VoLTE)",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    audio = build_audio(
        duration_s=args.duration,
        sample_rate=args.sample_rate,
        period_s=args.period,
        beep_s=args.beep_ms / 1000.0,
        beep_hz=args.beep_hz,
        first_marker_s=args.first_marker,
    )
    frames = build_gray_frames(
        duration_s=args.duration,
        fps=args.fps,
        width=args.width,
        height=args.height,
        period_s=args.period,
        flash_frames=args.flash_frames,
        first_marker_s=args.first_marker,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / "stimulus.wav"
        _write_wav_pcm16(wav, audio, args.sample_rate)
        encode_stimulus(args.output, frames, wav, args.fps, args.width, args.height)
    print(f"wrote {args.output}")
    if args.also_delayed is not None:
        delayed = args.output.with_name(
            args.output.stem + f"_audio_delay_{int(args.also_delayed)}ms" + args.output.suffix
        )
        delay_audio_copy(args.output, delayed, args.also_delayed)
        print(f"wrote {delayed} (audio delayed by {args.also_delayed} ms)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
