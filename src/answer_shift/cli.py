"""CLI for saved JSONL snapshots; never calls a model-generation API."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .core import compare, read_jsonl
from .model import LocalNLI


def main() -> int:
    parser = argparse.ArgumentParser(description="Review semantic changes between AI answer snapshots")
    parser.add_argument("--baseline", required=True, type=Path, help="previous JSONL snapshot")
    parser.add_argument("--candidate", required=True, type=Path, help="new JSONL snapshot")
    parser.add_argument("--out", type=Path, help="optional JSON report path (default: stdout)")
    parser.add_argument("--threshold", type=float, default=0.70, help="NLI threshold for review signals")
    args = parser.parse_args()
    try:
        baseline = read_jsonl(args.baseline.read_text(encoding="utf-8"))
        candidate = read_jsonl(args.candidate.read_text(encoding="utf-8"))
        report = compare(baseline, candidate, LocalNLI(), args.threshold)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    output = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        args.out.write_text(output, encoding="utf-8")
    else:
        sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
