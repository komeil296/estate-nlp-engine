#!/usr/bin/env python3
"""Run a privacy-preserving, read-only financial text-visibility audit."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from estate_nlp.financial_visibility import evaluate_visibility


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", required=True, type=Path)
    parser.add_argument("--sample-per-category", type=int, default=300)
    parser.add_argument("--seed", type=int, default=20261030)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    if not args.database.is_file():
        parser.error(f"Database does not exist: {args.database}")

    report = evaluate_visibility(
        args.database,
        sample_per_category=args.sample_per_category,
        seed=args.seed,
    )

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
        print(f"Visibility audit report written: {args.output}")
    else:
        print(report)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
