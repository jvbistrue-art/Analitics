"""Pass/fail profiles for A/V sync reports."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ThresholdProfile:
    name: str
    min_median_ms: float | None
    max_median_ms: float | None
    max_abs_median_ms: float | None
    max_std_ms: float | None
    measured_only: bool = False


PROFILES: dict[str, ThresholdProfile] = {
    "baseline": ThresholdProfile(
        name="baseline",
        min_median_ms=None,
        max_median_ms=None,
        max_abs_median_ms=None,
        max_std_ms=None,
        measured_only=True,
    ),
    "itu_like": ThresholdProfile(
        name="itu_like",
        min_median_ms=-45.0,
        max_median_ms=125.0,
        max_abs_median_ms=None,
        max_std_ms=40.0,
        measured_only=False,
    ),
    "volte_compensated": ThresholdProfile(
        name="volte_compensated",
        min_median_ms=None,
        max_median_ms=None,
        max_abs_median_ms=100.0,
        max_std_ms=60.0,
        measured_only=False,
    ),
}


def verdict(median_ms: float, std_ms: float, profile_name: str) -> str:
    profile = PROFILES[profile_name]
    if profile.measured_only:
        return "MEASURED_ONLY"

    if profile.max_abs_median_ms is not None and abs(median_ms) > profile.max_abs_median_ms:
        return "FAIL"
    if profile.min_median_ms is not None and median_ms < profile.min_median_ms:
        return "FAIL"
    if profile.max_median_ms is not None and median_ms > profile.max_median_ms:
        return "FAIL"
    if profile.max_std_ms is not None and std_ms > profile.max_std_ms:
        return "FAIL"
    return "PASS"
