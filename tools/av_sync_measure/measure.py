#!/usr/bin/env python3
"""Measure A/V playout offset from a receiver capture with flash+beep markers."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import wave
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from .thresholds import PROFILES, verdict


@dataclass
class MeasureResult:
    input: str
    bias_ms: float
    threshold_profile: str
    flash_times_ms: list[float]
    beep_times_ms: list[float]
    offsets_ms: list[float]
    matched_pairs: int
    match_rate: float
    mean_offset_ms: float | None
    median_offset_ms: float | None
    p95_offset_ms: float | None
    std_offset_ms: float | None
    min_offset_ms: float | None
    max_offset_ms: float | None
    drift_ms_per_min: float | None
    verdict: str


def run_ffmpeg(cmd: list[str]) -> None:
    proc = subprocess.run(cmd, capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError(
            "ffmpeg failed:\n" + proc.stderr.decode("utf-8", errors="replace")
        )


def extract_audio_wav(input_path: Path, wav_path: Path, sample_rate: int = 48000) -> None:
    run_ffmpeg(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(input_path),
            "-vn",
            "-ac",
            "1",
            "-ar",
            str(sample_rate),
            "-c:a",
            "pcm_s16le",
            str(wav_path),
        ]
    )


def read_wav_mono(path: Path) -> tuple[np.ndarray, int]:
    with wave.open(str(path), "rb") as wf:
        channels = wf.getnchannels()
        sample_rate = wf.getframerate()
        width = wf.getsampwidth()
        n = wf.getnframes()
        raw = wf.readframes(n)
    if width != 2:
        raise ValueError(f"expected 16-bit PCM, got sampwidth={width}")
    data = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
    if channels > 1:
        data = data.reshape(-1, channels).mean(axis=1)
    return data, sample_rate


def detect_beeps(
    audio: np.ndarray,
    sample_rate: int,
    min_period_s: float = 2.0,
    threshold_ratio: float = 0.35,
) -> list[float]:
    """Return beep onset times in milliseconds."""
    win = max(1, int(sample_rate * 0.005))  # 5 ms RMS
    # pad to full windows
    n_win = len(audio) // win
    if n_win == 0:
        return []
    shaped = audio[: n_win * win].reshape(n_win, win)
    rms = np.sqrt(np.mean(shaped * shaped, axis=1))
    if rms.max() <= 1e-8:
        return []
    thr = max(rms.max() * threshold_ratio, np.median(rms) * 8.0)
    above = rms > thr
    times_ms: list[float] = []
    refractory = int(round(min_period_s / (win / sample_rate)))
    i = 0
    while i < len(above):
        if above[i]:
            # onset = first bin of this peak
            t_ms = (i * win) * 1000.0 / sample_rate
            times_ms.append(t_ms)
            i += max(refractory, 1)
        else:
            i += 1
    return times_ms


def probe_fps(input_path: Path) -> float:
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=avg_frame_rate,r_frame_rate",
        "-of",
        "json",
        str(input_path),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError("ffprobe failed:\n" + proc.stderr)
    info = json.loads(proc.stdout)
    streams = info.get("streams") or []
    if not streams:
        raise RuntimeError("no video stream found")
    rate = streams[0].get("avg_frame_rate") or streams[0].get("r_frame_rate") or "0/1"
    num, den = rate.split("/")
    num_f, den_f = float(num), float(den)
    if den_f == 0:
        return 30.0
    fps = num_f / den_f
    return fps if fps > 0 else 30.0


def extract_frame_luma_means(input_path: Path, width: int = 64, height: int = 36) -> np.ndarray:
    cmd = [
        "ffmpeg",
        "-v",
        "error",
        "-i",
        str(input_path),
        "-vf",
        f"scale={width}:{height},format=gray",
        "-f",
        "rawvideo",
        "-pix_fmt",
        "gray",
        "pipe:1",
    ]
    proc = subprocess.run(cmd, capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError(
            "ffmpeg frame extract failed:\n"
            + proc.stderr.decode("utf-8", errors="replace")
        )
    frame_size = width * height
    raw = proc.stdout
    n_frames = len(raw) // frame_size
    if n_frames == 0:
        return np.zeros(0, dtype=np.float64)
    frames = np.frombuffer(raw[: n_frames * frame_size], dtype=np.uint8)
    frames = frames.reshape(n_frames, frame_size)
    return frames.mean(axis=1).astype(np.float64)


def detect_flashes(
    luma: np.ndarray,
    fps: float,
    min_period_s: float = 2.0,
    threshold_ratio: float = 0.55,
) -> list[float]:
    if luma.size == 0:
        return []
    baseline = np.median(luma)
    peak = luma.max()
    if peak - baseline < 20:
        # weak contrast; fall back to relative peaks
        thr = baseline + (peak - baseline) * 0.7
    else:
        thr = max(baseline + 40.0, baseline + (peak - baseline) * threshold_ratio)
    above = luma >= thr
    times_ms: list[float] = []
    refractory = max(1, int(round(min_period_s * fps)))
    i = 0
    while i < len(above):
        if above[i]:
            times_ms.append(i * 1000.0 / fps)
            i += refractory
        else:
            i += 1
    return times_ms


def match_pairs(
    flash_ms: list[float],
    beep_ms: list[float],
    search_window_ms: float = 2000.0,
) -> list[tuple[float, float, float]]:
    """Greedy nearest-neighbor matching. Returns (flash, beep, offset) tuples."""
    used_beeps: set[int] = set()
    pairs: list[tuple[float, float, float]] = []
    for f in flash_ms:
        best_j = None
        best_abs = None
        for j, b in enumerate(beep_ms):
            if j in used_beeps:
                continue
            d = b - f
            if abs(d) > search_window_ms:
                continue
            ad = abs(d)
            if best_abs is None or ad < best_abs:
                best_abs = ad
                best_j = j
        if best_j is not None:
            b = beep_ms[best_j]
            used_beeps.add(best_j)
            pairs.append((f, b, b - f))
    return pairs


def percentile(values: np.ndarray, p: float) -> float:
    if values.size == 0:
        raise ValueError("empty")
    return float(np.percentile(values, p))


def estimate_drift_ms_per_min(pair_flash_ms: list[float], offsets_ms: list[float]) -> float | None:
    if len(offsets_ms) < 3:
        return None
    x = np.asarray(pair_flash_ms, dtype=np.float64) / 60000.0  # minutes
    y = np.asarray(offsets_ms, dtype=np.float64)
    # simple linear regression slope
    x_mean = x.mean()
    y_mean = y.mean()
    denom = np.sum((x - x_mean) ** 2)
    if denom <= 1e-12:
        return 0.0
    slope = float(np.sum((x - x_mean) * (y - y_mean)) / denom)
    return slope


def measure_file(
    input_path: Path,
    bias_ms: float = 0.0,
    threshold_profile: str = "baseline",
    search_window_ms: float = 2000.0,
    min_period_s: float = 2.0,
) -> MeasureResult:
    if threshold_profile not in PROFILES:
        raise ValueError(f"unknown profile {threshold_profile}; choose from {list(PROFILES)}")

    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / "audio.wav"
        extract_audio_wav(input_path, wav)
        audio, sr = read_wav_mono(wav)

    fps = probe_fps(input_path)
    luma = extract_frame_luma_means(input_path)
    flashes = detect_flashes(luma, fps=fps, min_period_s=min_period_s)
    beeps = detect_beeps(audio, sample_rate=sr, min_period_s=min_period_s)
    pairs = match_pairs(flashes, beeps, search_window_ms=search_window_ms)

    raw_offsets = [o for _, _, o in pairs]
    corrected = [o - bias_ms for o in raw_offsets]
    arr = np.asarray(corrected, dtype=np.float64) if corrected else np.asarray([], dtype=np.float64)

    mean = float(arr.mean()) if arr.size else None
    median = float(np.median(arr)) if arr.size else None
    p95 = percentile(arr, 95) if arr.size else None
    std = float(arr.std(ddof=0)) if arr.size else None
    vmin = float(arr.min()) if arr.size else None
    vmax = float(arr.max()) if arr.size else None
    drift = estimate_drift_ms_per_min([p[0] for p in pairs], corrected) if arr.size else None
    match_rate = (len(pairs) / len(flashes)) if flashes else 0.0

    if median is None or std is None:
        v = "FAIL"
    else:
        v = verdict(median, std, threshold_profile)

    return MeasureResult(
        input=str(input_path),
        bias_ms=bias_ms,
        threshold_profile=threshold_profile,
        flash_times_ms=[round(x, 3) for x in flashes],
        beep_times_ms=[round(x, 3) for x in beeps],
        offsets_ms=[round(x, 3) for x in corrected],
        matched_pairs=len(pairs),
        match_rate=round(match_rate, 4),
        mean_offset_ms=None if mean is None else round(mean, 3),
        median_offset_ms=None if median is None else round(median, 3),
        p95_offset_ms=None if p95 is None else round(p95, 3),
        std_offset_ms=None if std is None else round(std, 3),
        min_offset_ms=None if vmin is None else round(vmin, 3),
        max_offset_ms=None if vmax is None else round(vmax, 3),
        drift_ms_per_min=None if drift is None else round(drift, 3),
        verdict=v,
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", type=Path, required=True, help="receiver capture with A/V")
    p.add_argument("--bias-ms", type=float, default=0.0, help="subtract recorder bias")
    p.add_argument(
        "--threshold-profile",
        choices=sorted(PROFILES.keys()),
        default="baseline",
    )
    p.add_argument("--search-window-ms", type=float, default=2000.0)
    p.add_argument("--min-period-s", type=float, default=2.0)
    p.add_argument("--report", type=Path, default=None, help="write JSON report")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    result = measure_file(
        input_path=args.input,
        bias_ms=args.bias_ms,
        threshold_profile=args.threshold_profile,
        search_window_ms=args.search_window_ms,
        min_period_s=args.min_period_s,
    )
    payload = asdict(result)
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    print(text)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text + "\n", encoding="utf-8")
    return 0 if result.verdict != "FAIL" or args.threshold_profile == "baseline" else 2


if __name__ == "__main__":
    sys.exit(main())
