#!/usr/bin/env python3
"""Read-only structural audit for the Divar SQLite dataset.

The report contains aggregates only. It never prints listing titles,
descriptions, phone numbers, or other raw advertisement text.
"""
from __future__ import annotations

import argparse
import re
import sqlite3
from collections import Counter
from pathlib import Path


CATEGORICAL_FIELDS = (
    "cat2_slug", "cat3_slug", "created_at_month", "user_type",
    "rent_mode", "rent_type", "price_mode", "credit_mode", "deed_type",
    "rooms_count", "has_warm_water_provider", "has_heating_system",
    "has_cooling_system", "has_restroom", "building_direction",
    "floor_material", "property_type", "extra_person_capacity", "floor",
    "total_floors_count", "construction_year",
)
NUMERIC_FIELDS = (
    "price_value", "rent_value", "credit_value", "building_size",
    "land_size", "rent_price_on_regular_days",
    "rent_price_on_special_days", "rent_price_at_weekends",
    "cost_per_extra_person",
)
TEXT_FEATURES = {
    "persian_digits": re.compile(r"[۰-۹]"),
    "arabic_indic_digits": re.compile(r"[٠-٩]"),
    "zwnj": re.compile("\u200c"),
    "arabic_diacritics": re.compile(r"[\u064b-\u0652\u0670]"),
    "tatweel": re.compile("\u0640"),
    "bidi_controls": re.compile(r"[\u200e\u200f\u202a-\u202e\u2066-\u2069]"),
}


def quote_identifier(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def open_read_only(path: Path) -> sqlite3.Connection:
    uri = path.resolve().as_uri() + "?mode=ro"
    connection = sqlite3.connect(uri, uri=True)
    connection.execute("PRAGMA query_only=ON")
    return connection


def audit(database: Path, include_unicode_scan: bool = False) -> str:
    with open_read_only(database) as connection:
        table = connection.execute(
            "SELECT sql FROM sqlite_master "
            "WHERE type='table' AND name='divar_ads'"
        ).fetchone()
        if table is None:
            raise RuntimeError("Table 'divar_ads' was not found.")

        columns = [
            row[1] for row in connection.execute(
                'PRAGMA table_info("divar_ads")'
            )
        ]
        column_set = set(columns)
        required = {"source_row", "cat2_slug", "cat3_slug", "title", "description"}
        missing = required - column_set
        if missing:
            raise RuntimeError(f"Missing required columns: {sorted(missing)}")

        total = connection.execute(
            "SELECT COUNT(*) FROM divar_ads"
        ).fetchone()[0]
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]

        lines = [
            "# Divar SQLite — Structural Audit",
            "",
            f"- Database file: `{database.name}`",
            f"- Total records: **{total:,}**",
            f"- Column count: **{len(columns)}**",
            f"- SQLite integrity check: **{integrity}**",
            "- Access mode: read-only",
            "- Raw advertisement text is not included in this report.",
            "",
            "## Main categories",
            "",
            "| cat2_slug | Records | Share |",
            "|---|---:|---:|",
        ]
        for category, count in connection.execute(
            "SELECT cat2_slug, COUNT(*) FROM divar_ads "
            "GROUP BY cat2_slug ORDER BY COUNT(*) DESC"
        ):
            lines.append(
                f"| `{category or '(NULL)'}` | {count:,} | "
                f"{count / total * 100:.2f}% |"
            )

        lines.extend([
            "",
            "## Subcategories",
            "",
            "| cat2_slug | cat3_slug | Records |",
            "|---|---|---:|",
        ])
        for cat2, cat3, count in connection.execute(
            "SELECT cat2_slug, cat3_slug, COUNT(*) FROM divar_ads "
            "GROUP BY cat2_slug, cat3_slug ORDER BY cat2_slug, COUNT(*) DESC"
        ):
            lines.append(
                f"| `{cat2 or '(NULL)'}` | `{cat3 or '(NULL)'}` | {count:,} |"
            )

        lines.extend([
            "",
            "## Field coverage",
            "",
            "| Field | Non-NULL | NULL | Distinct non-NULL |",
            "|---|---:|---:|---:|",
        ])
        aggregate_expressions = []
        for field in columns:
            qfield = quote_identifier(field)
            aggregate_expressions.append(f"COUNT({qfield})")
            if field in CATEGORICAL_FIELDS:
                aggregate_expressions.append(f"COUNT(DISTINCT {qfield})")
        aggregate = connection.execute(
            "SELECT " + ", ".join(aggregate_expressions) + " FROM divar_ads"
        ).fetchone()
        aggregate_index = 0
        for field in columns:
            nonnull = aggregate[aggregate_index]
            aggregate_index += 1
            if field in CATEGORICAL_FIELDS:
                distinct = aggregate[aggregate_index]
                aggregate_index += 1
            elif field in {"title", "description"}:
                distinct = "not calculated (free text)"
            else:
                distinct = "not calculated"
            nulls = total - nonnull
            lines.append(
                f"| `{field}` | {nonnull:,} | {nulls:,} | {distinct} |"
            )

        lines.extend([
            "",
            "## Categorical value distributions",
            "",
        ])
        for field in CATEGORICAL_FIELDS:
            if field not in column_set:
                continue
            lines.extend([
                f"### `{field}`",
                "",
                "| Value | Count |",
                "|---|---:|",
            ])
            for value, count in connection.execute(
                f"SELECT {quote_identifier(field)}, COUNT(*) "
                f"FROM divar_ads WHERE {quote_identifier(field)} IS NOT NULL "
                f"GROUP BY {quote_identifier(field)} ORDER BY COUNT(*) DESC "
                "LIMIT 40"
            ):
                safe_value = str(value).replace("|", "\\|").replace("`", "'")
                lines.append(f"| `{safe_value}` | {count:,} |")
            lines.append("")

        lines.extend([
            "## Numeric field ranges",
            "",
            "| Field | Non-NULL | Zero | Minimum | Maximum |",
            "|---|---:|---:|---:|---:|",
        ])
        for field in NUMERIC_FIELDS:
            if field not in column_set:
                continue
            nonnull, zero, minimum, maximum = connection.execute(
                f"SELECT COUNT({quote_identifier(field)}), "
                f"SUM(CASE WHEN {quote_identifier(field)}=0 THEN 1 ELSE 0 END), "
                f"MIN({quote_identifier(field)}), MAX({quote_identifier(field)}) "
                "FROM divar_ads"
            ).fetchone()
            lines.append(
                f"| `{field}` | {nonnull:,} | {int(zero or 0):,} | "
                f"{minimum} | {maximum} |"
            )

        if {"location_latitude", "location_longitude"} <= column_set:
            both, neither, partial = connection.execute("""
                SELECT
                    SUM(CASE WHEN location_latitude IS NOT NULL
                              AND location_longitude IS NOT NULL THEN 1 ELSE 0 END),
                    SUM(CASE WHEN location_latitude IS NULL
                              AND location_longitude IS NULL THEN 1 ELSE 0 END),
                    SUM(CASE WHEN (location_latitude IS NULL)
                               != (location_longitude IS NULL) THEN 1 ELSE 0 END)
                FROM divar_ads
            """).fetchone()
            lines.extend([
                "",
                "## Coordinates",
                "",
                f"- Both coordinates present: **{int(both or 0):,}**",
                f"- Both coordinates missing: **{int(neither or 0):,}**",
                f"- Only one coordinate present: **{int(partial or 0):,}**",
            ])

        lines.extend([
            "",
            "## Text-length and Unicode profile",
            "",
            "| Field | Non-empty | Average length | Maximum length |",
            "|---|---:|---:|---:|",
        ])
        for field in ("title", "description"):
            nonempty, average, maximum = connection.execute(
                f"SELECT SUM(CASE WHEN TRIM(COALESCE({quote_identifier(field)},''))<>'' "
                f"THEN 1 ELSE 0 END), "
                f"AVG(LENGTH({quote_identifier(field)})), "
                f"MAX(LENGTH({quote_identifier(field)})) FROM divar_ads"
            ).fetchone()
            lines.append(
                f"| `{field}` | {int(nonempty or 0):,} | "
                f"{float(average or 0):.1f} | {int(maximum or 0):,} |"
            )

        if include_unicode_scan:
            unicode_counts = Counter()
            cursor = connection.execute("SELECT title, description FROM divar_ads")
            for title, description in cursor:
                combined = (title or "") + "\\n" + (description or "")
                for name, pattern in TEXT_FEATURES.items():
                    if pattern.search(combined):
                        unicode_counts[name] += 1
            lines.extend([
                "",
                "| Unicode feature | Records containing feature |",
                "|---|---:|",
            ])
            for name in TEXT_FEATURES:
                lines.append(f"| `{name}` | {unicode_counts[name]:,} |")
        else:
            lines.extend([
                "",
                "Unicode feature scan: **skipped** (pass `--scan-unicode` to enable the slower full-text scan).",
            ])

        lines.extend([
            "",
            "## Interpretation notes",
            "",
            "- NULL means missing/unknown; it is not equivalent to `false` or zero.",
            "- Categorical heating, cooling, restroom, and hot-water fields must not be flattened to booleans.",
            "- `30+`, `unselect`, and Persian year ranges must retain their raw forms until a range-aware parser is designed.",
            "- Structured financial values are source labels; currency and unit must not be inferred from the column name.",
            "- Source category labels are weak supervision, not a gold-standard annotation.",
            "",
            "Audit completed without changing the database.",
            "",
        ])
        return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--scan-unicode", action="store_true",
        help="scan all title/description text for Unicode normalization markers",
    )
    args = parser.parse_args()

    if not args.database.is_file():
        parser.error(f"Database does not exist: {args.database}")

    report = audit(args.database, include_unicode_scan=args.scan_unicode)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
        print(f"Audit report written: {args.output}")
    else:
        print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
