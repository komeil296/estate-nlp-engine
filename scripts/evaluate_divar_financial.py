#!/usr/bin/env python3
"""Evaluate financial text mentions against Divar structured weak labels.

The database is opened read-only. Raw ad text and evidence are never printed
or saved. Source currency/unit is unspecified and is never inferred.
"""
from __future__ import annotations

import argparse
import json
import random
import sqlite3
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from estate_nlp.extractor import extract_text


# field -> (expected semantic role, mode field)
FINANCIAL_FIELDS = {
    "residential-sell": {
        "price_value": ("asking_price", "price_mode"),
    },
    "commercial-sell": {
        "price_value": ("asking_price", "price_mode"),
    },
    "residential-rent": {
        "rent_value": ("monthly_rent", "rent_mode"),
        "credit_value": ("deposit", "credit_mode"),
    },
    "commercial-rent": {
        "rent_value": ("monthly_rent", "rent_mode"),
        "credit_value": ("deposit", "credit_mode"),
    },
    "temporary-rent": {
        "rent_price_on_regular_days": ("daily_rent", None),
        "rent_price_on_special_days": ("special_day_rent", None),
        "rent_price_at_weekends": ("weekend_rent", None),
        "cost_per_extra_person": ("cost_per_extra_person", None),
    },
}

# Only diagnostic candidates. A factor match is NOT treated as a correct match.
COMMON_SCALE_FACTORS = (
    Decimal("0.1"),
    Decimal("10"),
    Decimal("100"),
    Decimal("1000"),
    Decimal("10000"),
    Decimal("100000"),
    Decimal("1000000"),
    Decimal("1000000000"),
)


def open_read_only(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA query_only=ON")
    return connection


def to_decimal(value):
    if value is None:
        return None
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None
    return result if result.is_finite() else None


def sample_rows(connection, sample_per_category: int, seed: int):
    rng = random.Random(seed)
    selected_ids = []
    categories = [
        row[0] for row in connection.execute(
            "SELECT DISTINCT cat2_slug FROM divar_ads "
            "WHERE cat2_slug IS NOT NULL ORDER BY cat2_slug"
        )
    ]
    for category in categories:
        ids = [
            row[0] for row in connection.execute(
                "SELECT source_row FROM divar_ads "
                "WHERE cat2_slug=? ORDER BY source_row",
                (category,),
            )
        ]
        selected_ids.extend(
            rng.sample(ids, min(sample_per_category, len(ids)))
        )

    rows = []
    for start in range(0, len(selected_ids), 400):
        chunk = selected_ids[start:start + 400]
        marks = ",".join("?" for _ in chunk)
        rows.extend(
            dict(row) for row in connection.execute(
                f"SELECT * FROM divar_ads WHERE source_row IN ({marks})",
                chunk,
            )
        )
    return rows, categories


def new_counter():
    return {
        "labeled_positive": 0,
        "source_zero": 0,
        "source_null": 0,
        "exact_role_value": 0,
        "exact_value_wrong_role": 0,
        "role_found_wrong_value": 0,
        "no_financial_mention": 0,
        "other_financial_mentions_only": 0,
        "possible_scale_factor_same_role": 0,
    }


def evaluate(database: Path, sample_per_category: int, seed: int) -> str:
    stats = defaultdict(new_counter)
    category_sample_counts = defaultdict(int)
    mode_counts = defaultdict(lambda: defaultdict(int))
    examples = defaultdict(list)

    required = {"source_row", "cat2_slug", "title", "description"}
    for mapping in FINANCIAL_FIELDS.values():
        required.update(mapping)
        required.update(
            mode for _, mode in mapping.values() if mode is not None
        )

    with open_read_only(database) as connection:
        columns = {
            row[1] for row in connection.execute(
                'PRAGMA table_info("divar_ads")'
            )
        }
        missing = required - columns
        if missing:
            raise RuntimeError(f"Missing database columns: {sorted(missing)}")

        rows, categories = sample_rows(
            connection, sample_per_category, seed
        )

    for row in rows:
        category = row["cat2_slug"] or "(missing)"
        category_sample_counts[category] += 1

        text = "\n".join(
            part for part in (row.get("title") or "",
                              row.get("description") or "")
            if part.strip()
        )
        result = extract_text(text)
        mentions = result.financial_mentions

        for field, (expected_role, mode_field) in FINANCIAL_FIELDS.get(
            category, {}
        ).items():
            amount = to_decimal(row.get(field))
            mode = row.get(mode_field) if mode_field else None

            key = (category, field)
            item = stats[key]

            if mode_field:
                mode_counts[(category, mode_field)][
                    str(mode) if mode is not None else "(NULL)"
                ] += 1

            if amount is None:
                item["source_null"] += 1
                continue

            if amount == 0:
                item["source_zero"] += 1
                continue

            item["labeled_positive"] += 1

            exact_role = [
                mention for mention in mentions
                if mention.semantic_role == expected_role
            ]
            exact_value_any_role = [
                mention for mention in mentions
                if to_decimal(mention.normalized_value) == amount
            ]
            exact_role_value = [
                mention for mention in exact_role
                if to_decimal(mention.normalized_value) == amount
            ]

            if exact_role_value:
                item["exact_role_value"] += 1
                continue

            if exact_value_any_role:
                item["exact_value_wrong_role"] += 1
                if len(examples[key]) < 3:
                    examples[key].append({
                        "source_row": row["source_row"],
                        "expected": str(amount),
                        "predicted": [
                            f"{m.semantic_role}:{m.normalized_value}"
                            for m in exact_value_any_role
                        ],
                        "kind": "exact amount, role differs",
                    })
                continue

            if exact_role:
                item["role_found_wrong_value"] += 1
                predicted_values = [
                    to_decimal(m.normalized_value) for m in exact_role
                ]
                if any(
                    value is not None
                    and any(value * factor == amount or amount * factor == value
                            for factor in COMMON_SCALE_FACTORS)
                    for value in predicted_values
                ):
                    item["possible_scale_factor_same_role"] += 1

                if len(examples[key]) < 3:
                    examples[key].append({
                        "source_row": row["source_row"],
                        "expected": str(amount),
                        "predicted": [
                            f"{m.semantic_role}:{m.normalized_value}"
                            for m in exact_role
                        ],
                        "kind": "role found, amount differs",
                    })
                continue

            if not mentions:
                item["no_financial_mention"] += 1
            else:
                item["other_financial_mentions_only"] += 1

    lines = [
        "# Estate NLP — Divar Financial Weak-Label Evaluation",
        "",
        f"- Database: `{database.name}`",
        f"- Sample per category: **{sample_per_category}**",
        f"- Seed: **{seed}**",
        f"- Actual sample size: **{len(rows):,}**",
        "- Database access: read-only",
        "- Raw advertisement text/evidence: not printed or saved",
        "- Source currency/unit: unspecified; no currency conversion applied",
        "",
        "> Source numeric columns are weak labels, not gold annotations. "
        "An amount may not be repeated in the text. Exact amount matches are "
        "reported separately from role matches. Possible scale factors are "
        "diagnostic only and are not counted as correct.",
        "",
        "## Sample size by category",
        "",
        "| Category | Sample records |",
        "|---|---:|",
    ]
    for category in sorted(category_sample_counts):
        lines.append(f"| `{category}` | {category_sample_counts[category]:,} |")

    lines.extend([
        "",
        "## Financial field results",
        "",
        "| Category | Source field | Expected role | Positive labels | Zero labels | NULL labels | Exact role + value | Exact value, wrong role | Role, wrong value | No financial mention | Other mentions only | Possible scale factor |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])

    for (category, field), item in sorted(stats.items()):
        role = FINANCIAL_FIELDS[category][field][0]
        role_display = f"`{role}`"
        lines.append(
            f"| `{category}` | `{field}` | {role_display} | "
            f"{item['labeled_positive']:,} | {item['source_zero']:,} | "
            f"{item['source_null']:,} | {item['exact_role_value']:,} | "
            f"{item['exact_value_wrong_role']:,} | "
            f"{item['role_found_wrong_value']:,} | "
            f"{item['no_financial_mention']:,} | "
            f"{item['other_financial_mentions_only']:,} | "
            f"{item['possible_scale_factor_same_role']:,} |"
        )

    lines.extend([
        "",
        "## Source mode distribution in sampled records",
        "",
        "| Category | Mode field | Value | Count |",
        "|---|---|---|---:|",
    ])
    for (category, mode_field), values in sorted(mode_counts.items()):
        for value, count in sorted(values.items()):
            lines.append(
                f"| `{category}` | `{mode_field}` | `{value}` | {count:,} |"
            )

    lines.extend([
        "",
        "## Diagnostic mismatches (IDs and numbers only; no ad text)",
        "",
    ])
    any_examples = False
    for key, items in sorted(examples.items()):
        if not items:
            continue
        any_examples = True
        lines.extend([
            f"### `{key[0]}.{key[1]}`",
            "",
        ])
        for example in items:
            lines.append(
                f"- source_row={example['source_row']}; "
                f"expected={example['expected']}; "
                f"predicted={', '.join(example['predicted'])}; "
                f"kind={example['kind']}"
            )
        lines.append("")
    if not any_examples:
        lines.append("No diagnostic mismatches were selected for display.")

    lines.extend([
        "",
        "## Interpretation and limitations",
        "",
        "- `Exact role + value` is the strictest agreement category; it is not gold-standard accuracy.",
        "- `Exact value, wrong role` suggests the amount was seen but its financial meaning was misclassified.",
        "- `Role, wrong value` suggests a role cue was found but a different nearby amount was selected.",
        "- `No financial mention` means the extractor emitted no financial mentions for that sampled ad.",
        "- `Other mentions only` means it emitted financial mentions but none matched this source field/role/value.",
        "- A possible scale factor can indicate a unit or scale mismatch; it must be reviewed, never silently converted.",
        "- The current schema distinguishes `special_day_rent` from `weekend_rent`; the evaluator checks them separately.",
        "- Zero and NULL source amounts are reported separately and are not evaluated as positive text amounts.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", required=True, type=Path)
    parser.add_argument("--sample-per-category", type=int, default=300)
    parser.add_argument("--seed", type=int, default=20261030)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    if not args.database.is_file():
        parser.error(f"Database does not exist: {args.database}")
    if args.sample_per_category < 1:
        parser.error("--sample-per-category must be >= 1")

    report = evaluate(args.database, args.sample_per_category, args.seed)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
        print(f"Financial evaluation report written: {args.output}")
    else:
        print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
