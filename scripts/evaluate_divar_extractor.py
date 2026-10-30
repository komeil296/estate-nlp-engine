#!/usr/bin/env python3
"""Measure weak-label agreement of Estate NLP against a stratified Divar sample.

The source database is opened read-only. This is not a gold-standard accuracy
benchmark: category and structured-field values can be missing, stale, or not
repeated in advertisement text. Raw text is never printed.
"""
from __future__ import annotations

import argparse
import math
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from estate_nlp.divar_dataset import map_divar_record
from estate_nlp.extractor import extract_text


def open_read_only(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(
        path.resolve().as_uri() + "?mode=ro", uri=True
    )
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA query_only=ON")
    return connection


def take_stratified_sample(connection, sample_per_category: int):
    categories = [
        row[0] for row in connection.execute(
            "SELECT DISTINCT cat2_slug FROM divar_ads "
            "WHERE cat2_slug IS NOT NULL ORDER BY cat2_slug"
        )
    ]
    selected = {}
    for category in categories:
        rows = connection.execute(
            "SELECT * FROM divar_ads WHERE cat2_slug=? "
            "ORDER BY RANDOM() LIMIT ?",
            (category, sample_per_category),
        )
        for row in rows:
            selected[row["source_row"]] = dict(row)

    # Keep every explicit single-person label; the field is very sparse.
    labeled_rows = connection.execute(
        "SELECT * FROM divar_ads WHERE rent_to_single IN (0,1)"
    )
    for row in labeled_rows:
        selected[row["source_row"]] = dict(row)

    return list(selected.values())


def add_metric(metrics, field, category, expected, predicted, tolerance=0.0):
    if expected is None:
        return
    if isinstance(expected, (int, float)) and not isinstance(expected, bool):
        if expected <= 0:
            return

    item = metrics[field][category]
    item["labeled"] += 1
    if predicted is None:
        item["abstain"] += 1
    else:
        equal = (
            math.isclose(float(expected), float(predicted),
                         rel_tol=0.0, abs_tol=tolerance)
            if isinstance(expected, (int, float)) and
               not isinstance(expected, bool)
            else predicted == expected
        )
        item["match" if equal else "mismatch"] += 1


def summarize(item):
    labeled = item["labeled"]
    decided = item["match"] + item["mismatch"]
    return {
        **item,
        "coverage_pct": round(decided / labeled * 100, 2) if labeled else None,
        "agreement_decided_pct": round(item["match"] / decided * 100, 2)
        if decided else None,
        "agreement_all_pct": round(item["match"] / labeled * 100, 2)
        if labeled else None,
    }


def evaluate(database: Path, sample_per_category: int) -> str:
    metrics = defaultdict(lambda: defaultdict(
        lambda: {"labeled": 0, "match": 0, "mismatch": 0, "abstain": 0}
    ))
    category_counts = defaultdict(int)

    with open_read_only(database) as connection:
        columns = {
            row[1] for row in connection.execute(
                'PRAGMA table_info("divar_ads")'
            )
        }
        required = {"source_row", "cat2_slug", "cat3_slug", "title",
                    "description", "building_size", "land_size",
                    "rooms_count", "rent_to_single"}
        missing = required - columns
        if missing:
            raise RuntimeError(f"Missing columns: {sorted(missing)}")

        sample = take_stratified_sample(connection, sample_per_category)

    for row in sample:
        category = row["cat2_slug"] or "(missing)"
        category_counts[category] += 1
        mapped = map_divar_record(row)
        weak = mapped["weak_labels"]
        text = "\n".join(
            part for part in (row.get("title") or "",
                              row.get("description") or "")
            if part.strip()
        )
        extracted = extract_text(text)

        expected = weak["transaction_type"]
        if expected["status"] == "mapped":
            add_metric(metrics, "transaction_type", category,
                       expected["value"], extracted.transaction_type.value)

        expected = weak["property_type"]
        if expected["status"] == "mapped":
            add_metric(metrics, "property_type", category,
                       expected["value"], extracted.property_type.value)

        for field_name, extracted_name in (
            ("building_area_sqm", "building_area_sqm"),
            ("land_area_sqm", "land_area_sqm"),
        ):
            expected = weak[field_name]
            if expected["status"] == "mapped":
                add_metric(
                    metrics, field_name, category, expected["value"],
                    getattr(extracted.property, extracted_name).value,
                    tolerance=0.01,
                )

        expected = weak["rooms"]
        if expected["status"] == "mapped":
            add_metric(metrics, "rooms", category, expected["value"],
                       extracted.property.rooms.value)

        for feature_name, expected in weak["features"].items():
            if expected["status"] == "mapped":
                add_metric(
                    metrics, f"feature.{feature_name}", category,
                    expected["value"],
                    getattr(extracted.property.features, feature_name).value,
                )

        expected = weak["rental_conditions"]["allow_single_person"]
        if expected["status"] == "mapped":
            add_metric(
                metrics, "allow_single_person", category, expected["value"],
                extracted.rental_conditions.allow_single_person.value,
            )

    lines = [
        "# Estate NLP — Divar Weak-Label Agreement",
        "",
        f"- Database: `{database.name}`",
        f"- Sample per category: **{sample_per_category}**",
        f"- Actual sample size: **{len(sample):,}** (includes all explicit `rent_to_single` labels)",
        "- Database access: read-only",
        "- Raw advertisement text: not printed or saved",
        "",
        "> These are agreement measurements against source labels, not gold-standard accuracy. "
        "A structured source value may be absent from the text or may not be perfectly reliable.",
        "",
        "## Sample size by category",
        "",
        "| Category | Sample records |",
        "|---|---:|",
    ]
    for category, count in sorted(category_counts.items()):
        lines.append(f"| `{category}` | {count:,} |")

    lines.extend([
        "",
        "## Overall weak-label agreement",
        "",
        "| Field | Labeled | Decided | Abstained | Matches | Mismatches | Coverage | Agreement on decided | Agreement on all |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])

    for field in sorted(metrics):
        aggregate = {"labeled": 0, "match": 0, "mismatch": 0, "abstain": 0}
        for item in metrics[field].values():
            for key in aggregate:
                aggregate[key] += item[key]
        summary = summarize(aggregate)
        decided = aggregate["match"] + aggregate["mismatch"]
        lines.append(
            f"| `{field}` | {aggregate['labeled']:,} | {decided:,} | "
            f"{aggregate['abstain']:,} | {aggregate['match']:,} | "
            f"{aggregate['mismatch']:,} | "
            f"{summary['coverage_pct'] if summary['coverage_pct'] is not None else 'n/a'}% | "
            f"{summary['agreement_decided_pct'] if summary['agreement_decided_pct'] is not None else 'n/a'}% | "
            f"{summary['agreement_all_pct'] if summary['agreement_all_pct'] is not None else 'n/a'}% |"
        )

    lines.extend([
        "",
        "## Field agreement by category",
        "",
    ])
    for field in sorted(metrics):
        lines.extend([
            f"### `{field}`",
            "",
            "| Category | Labeled | Decided | Matches | Mismatches | Abstained | Coverage | Agreement on decided |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ])
        for category, item in sorted(metrics[field].items()):
            summary = summarize(item)
            decided = item["match"] + item["mismatch"]
            coverage = summary["coverage_pct"]
            agreement = summary["agreement_decided_pct"]
            lines.append(
                f"| `{category}` | {item['labeled']:,} | {decided:,} | "
                f"{item['match']:,} | {item['mismatch']:,} | "
                f"{item['abstain']:,} | "
                f"{coverage if coverage is not None else 'n/a'}% | "
                f"{agreement if agreement is not None else 'n/a'}% |"
            )
        lines.append("")

    lines.extend([
        "## Interpretation",
        "",
        "- Low coverage means the extractor often abstains; it is not automatically a wrong prediction.",
        "- Agreement is not precision/recall because the source labels are weak and may not be expressed in the ad text.",
        "- The `house-villa-*` source classes are intentionally excluded from a single property-type target because they combine two types.",
        "- The complete `rent_to_single` labeled subset is included because the source field has very few labeled rows.",
        "- Do not use this report alone to claim model quality or to train a final model.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", required=True, type=Path)
    parser.add_argument("--sample-per-category", type=int, default=300)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    if not args.database.is_file():
        parser.error(f"Database does not exist: {args.database}")
    if args.sample_per_category < 1:
        parser.error("--sample-per-category must be >= 1")

    report = evaluate(args.database, args.sample_per_category)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
        print(f"Evaluation report written: {args.output}")
    else:
        print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
