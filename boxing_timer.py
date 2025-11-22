"""Simple boxing round timer for the command line.

This script lets you run configurable boxing rounds with rest periods.
Use Ctrl+C to stop the timer early.
"""

from __future__ import annotations

import argparse
import sys
import time
from dataclasses import dataclass
from typing import Iterable


@dataclass
class TimerConfig:
    rounds: int
    round_seconds: int
    rest_seconds: int
    warmup_seconds: int
    bell: bool


def _format_time(seconds: int) -> str:
    minutes, secs = divmod(seconds, 60)
    return f"{minutes:02d}:{secs:02d}"


def _play_bell(enabled: bool) -> None:
    if enabled:
        sys.stdout.write("\a")
        sys.stdout.flush()


def _countdown(label: str, seconds: int, bell: bool) -> None:
    for remaining in range(seconds, -1, -1):
        sys.stdout.write(f"\r{label}: {_format_time(remaining)}   ")
        sys.stdout.flush()
        if remaining > 0:
            time.sleep(1)
    sys.stdout.write("\n")
    _play_bell(bell)


def _round_intervals(config: TimerConfig) -> Iterable[tuple[str, int]]:
    if config.warmup_seconds:
        yield "Warmup", config.warmup_seconds
    for round_number in range(1, config.rounds + 1):
        yield f"Round {round_number}/{config.rounds}", config.round_seconds
        if round_number != config.rounds and config.rest_seconds:
            yield "Rest", config.rest_seconds


def run_timer(config: TimerConfig) -> None:
    try:
        for label, seconds in _round_intervals(config):
            _countdown(label, seconds, bell=config.bell)
    except KeyboardInterrupt:
        sys.stdout.write("\nTimer stopped.\n")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Boxing style round timer")
    parser.add_argument(
        "--rounds",
        type=int,
        default=3,
        help="Number of rounds (default: 3)",
    )
    parser.add_argument(
        "--round-seconds",
        type=int,
        default=180,
        help="Seconds per round (default: 180, i.e. 3 minutes)",
    )
    parser.add_argument(
        "--rest-seconds",
        type=int,
        default=60,
        help="Seconds of rest between rounds (default: 60)",
    )
    parser.add_argument(
        "--warmup-seconds",
        type=int,
        default=10,
        help="Optional warmup before round 1 (default: 10)",
    )
    parser.add_argument(
        "--no-bell",
        action="store_true",
        help="Disable the terminal bell sound",
    )
    return parser


def parse_args(argv: list[str] | None = None) -> TimerConfig:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.rounds < 1:
        parser.error("--rounds must be at least 1")
    for name in ("round_seconds", "rest_seconds", "warmup_seconds"):
        value = getattr(args, name)
        if value < 0:
            parser.error(f"--{name.replace('_', '-')} cannot be negative")
    return TimerConfig(
        rounds=args.rounds,
        round_seconds=args.round_seconds,
        rest_seconds=args.rest_seconds,
        warmup_seconds=args.warmup_seconds,
        bell=not args.no_bell,
    )


def main(argv: list[str] | None = None) -> int:
    config = parse_args(argv)
    run_timer(config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
