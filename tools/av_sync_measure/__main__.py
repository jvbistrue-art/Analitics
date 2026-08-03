"""CLI entry: python -m tools.av_sync_measure <measure|generate> ..."""

from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in {"-h", "--help"}:
        print(
            "usage: python -m tools.av_sync_measure measure|generate [options]\n"
            "       python -m tools.av_sync_measure.measure --input capture.mkv\n"
            "       python -m tools.av_sync_measure.generate_stimulus --output stim.mp4"
        )
        return 0
    cmd, *rest = argv
    if cmd in {"measure", "meas"}:
        from .measure import main as measure_main

        return measure_main(rest)
    if cmd in {"generate", "gen", "stimulus"}:
        from .generate_stimulus import main as gen_main

        return gen_main(rest)
    print(f"unknown command: {cmd}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
