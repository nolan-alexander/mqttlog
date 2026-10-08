from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from .record import parse_line, topic_match
from .rotate import RotatingLog
from .sim import simulate


def _read_records(path: Path) -> list:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        rec = parse_line(line)
        if rec is not None:
            rows.append(rec)
    return rows


def cmd_sim(args: argparse.Namespace) -> int:
    rows = simulate(args.count, tz_name=args.timezone)
    if args.out:
        log = RotatingLog(Path(args.out), max_bytes=args.max_bytes)
        try:
            last = None
            for rec in rows:
                last = log.write(rec)
            print(f"wrote {len(rows)} records to {last}")
        finally:
            log.close()
        return 0
    for rec in rows:
        print(rec.line())
    return 0


def cmd_replay(args: argparse.Namespace) -> int:
    rows = [r for r in _read_records(Path(args.file)) if topic_match(r.topic, args.topic)]
    out = Path(args.out)
    log = RotatingLog(out, max_bytes=args.max_bytes)
    try:
        last = None
        for rec in rows:
            last = log.write(rec)
    finally:
        log.close()
    dest = last if last is not None else out
    print(f"wrote {len(rows)} records to {dest}")
    return 0


def cmd_csv(args: argparse.Namespace) -> int:
    rows = [r for r in _read_records(Path(args.file)) if topic_match(r.topic, args.topic)]
    dest = sys.stdout if args.out == "-" else open(args.out, "w", encoding="utf-8", newline="")
    close = dest is not sys.stdout
    try:
        writer = csv.writer(dest)
        writer.writerow(["ts", "topic", "payload"])
        for rec in rows:
            writer.writerow([rec.ts, rec.topic, rec.payload])
    finally:
        if close:
            dest.close()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="mqttlog", description="Rotate and export MQTT-style topic logs")
    parser.add_argument("--timezone", default="America/Los_Angeles")
    parser.add_argument("--max-bytes", type=int, default=4096)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_sim = sub.add_parser("sim", help="emit fake sensor records")
    p_sim.add_argument("--count", type=int, default=8)
    p_sim.add_argument("--out", default="")
    p_sim.set_defaults(func=cmd_sim)

    p_rep = sub.add_parser("replay", help="filter a log file onto rotating outputs")
    p_rep.add_argument("file")
    p_rep.add_argument("--topic", default="#")
    p_rep.add_argument("--out", required=True)
    p_rep.set_defaults(func=cmd_replay)

    p_csv = sub.add_parser("csv", help="export matching records as CSV")
    p_csv.add_argument("file")
    p_csv.add_argument("--topic", default="#")
    p_csv.add_argument("--out", default="-")
    p_csv.set_defaults(func=cmd_csv)

    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
