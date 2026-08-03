"""Tests for A/V sync measurement helpers and end-to-end ffmpeg path."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.av_sync_measure.generate_stimulus import (  # noqa: E402
    build_audio,
    build_gray_frames,
    delay_audio_copy,
    encode_stimulus,
)
from tools.av_sync_measure.measure import (  # noqa: E402
    detect_beeps,
    detect_flashes,
    match_pairs,
    measure_file,
)
from tools.av_sync_measure.thresholds import verdict  # noqa: E402


def _ffmpeg_available() -> bool:
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        subprocess.run(["ffprobe", "-version"], capture_output=True, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


class ThresholdTests(unittest.TestCase):
    def test_baseline_always_measured(self):
        self.assertEqual(verdict(999, 999, "baseline"), "MEASURED_ONLY")

    def test_itu_pass_fail(self):
        self.assertEqual(verdict(80, 10, "itu_like"), "PASS")
        self.assertEqual(verdict(200, 10, "itu_like"), "FAIL")
        self.assertEqual(verdict(-60, 10, "itu_like"), "FAIL")
        self.assertEqual(verdict(20, 50, "itu_like"), "FAIL")

    def test_sat_compensated(self):
        self.assertEqual(verdict(90, 20, "sat_compensated"), "PASS")
        self.assertEqual(verdict(140, 20, "sat_compensated"), "FAIL")


class DetectorTests(unittest.TestCase):
    def test_detect_beeps_and_flashes_and_match(self):
        sr = 48000
        fps = 30
        period = 4.0
        first = 1.0
        duration = 20.0
        audio = build_audio(duration, sr, period, 0.06, 1000.0, first)
        # delay audio by 500 ms relative to video timeline concept
        delay = int(0.5 * sr)
        delayed = np.concatenate([np.zeros(delay), audio])[: int(duration * sr)]
        beeps = detect_beeps(delayed, sr, min_period_s=2.0)
        frames = build_gray_frames(duration, fps, 64, 36, period, 2, first)
        luma = frames.reshape(frames.shape[0], -1).mean(axis=1)
        flashes = detect_flashes(luma, fps=fps, min_period_s=2.0)
        pairs = match_pairs(flashes, beeps, search_window_ms=2000)
        self.assertGreaterEqual(len(pairs), 3)
        offsets = [o for _, _, o in pairs]
        median = float(np.median(offsets))
        self.assertTrue(450 <= median <= 550, msg=f"median={median}, offsets={offsets}")


@unittest.skipUnless(_ffmpeg_available(), "ffmpeg/ffprobe required")
class EndToEndTests(unittest.TestCase):
    def test_measure_known_audio_delay(self):
        import wave

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            stim = tmp_path / "stim.mp4"
            delayed = tmp_path / "delayed.mp4"
            duration = 24.0
            fps = 30
            sr = 48000
            period = 4.0
            first = 1.0
            audio = build_audio(duration, sr, period, 0.06, 1000.0, first)
            frames = build_gray_frames(duration, fps, 320, 180, period, 2, first)
            wav = tmp_path / "a.wav"
            pcm = (np.clip(audio, -1, 1) * 32767).astype(np.int16)
            with wave.open(str(wav), "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sr)
                wf.writeframes(pcm.tobytes())
            encode_stimulus(stim, frames, wav, fps, 320, 180)
            delay_audio_copy(stim, delayed, 500)
            result = measure_file(
                delayed,
                bias_ms=0.0,
                threshold_profile="baseline",
                search_window_ms=2000,
                min_period_s=2.0,
            )
            self.assertGreaterEqual(result.matched_pairs, 3)
            self.assertIsNotNone(result.median_offset_ms)
            assert result.median_offset_ms is not None
            self.assertTrue(
                430 <= result.median_offset_ms <= 570,
                msg=json.dumps(
                    {
                        "median": result.median_offset_ms,
                        "offsets": result.offsets_ms,
                        "flashes": result.flash_times_ms,
                        "beeps": result.beep_times_ms,
                    },
                    ensure_ascii=False,
                ),
            )


if __name__ == "__main__":
    unittest.main()
