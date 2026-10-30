"""Read-only visibility audit for financial weak labels in Divar text."""

from __future__ import annotations

import random
import re
import sqlite3
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path

from .extractor import extract_text
from .financial import ROLE_PATTERNS
from .normalization import normalize_persian_text


FINANCIAL_FIELDS = {
    "residential-sell": {
        "price_value": ("asking_price",),
    },
    "commercial-sell": {
        "price_value": ("asking_price",),
    },
    "residential-rent": {
        "rent_value": ("monthly_rent",),
        "credit_value": ("deposit",),
    },
    "commercial-rent": {
        "rent_value": ("monthly_rent",),
        "credit_value": ("deposit",),
    },
    "temporary-rent": {
        "rent_price_on_regular_days": ("daily_rent",),
        "rent_price_on_special_days": ("special_day_rent",),
        "rent_price_at_weekends": ("weekend_rent",),
        "cost_per_extra_person": ("cost_per_extra_person",),
    },
    "real-estate-services": {},
}

NUMBER_PATTERN = re.compile(
    r"(?<![\w/])"
    r"(?P<number>(?:\d{1,3}(?:[,،٬]\d{3})+|\d+)"
    r"(?:[٫.]\d+)?)"
    r"(?![\w/])"
)

SCALE_PATTERN = re.compile(
    r"\s*(?P<scale>میلیارد|ملیارد|مليارد|"
    r"میلیون|ملیون|مليون|هزار|م)(?![آ-ی])"
)

SCALE_FACTORS = {
    "میلیارد": Decimal("1000000000"),
    "ملیارد": Decimal("1000000000"),
    "مليارد": Decimal("1000000000"),
    "میلیون": Decimal("1000000"),
    "ملیون": Decimal("1000000"),
    "مليون": Decimal("1000000"),
    "هزار": Decimal("1000"),
    "م": Decimal("1000000"),
}

CURRENCY_PATTERN = re.compile(r"تومان|تومن|ریال")
FULL_SCALE_PATTERN = re.compile(
    r"میلیارد|ملیارد|مليارد|میلیون|ملیون|مليون|هزار"
)

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


def _decimal(value):
    if value is None:
        return None
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None
    return result if result.is_finite() else None


def _numeric_candidates(text: str):
    """Return (value, explicit_scale) candidates; never infer currency."""
    normalized = normalize_persian_text(text).replace("\u200c", " ")
    candidates = []

    for match in NUMBER_PATTERN.finditer(normalized):
        token = (
            match.group("number")
            .replace(",", "")
            .replace("،", "")
            .replace("٬", "")
            .replace("٫", ".")
        )
        try:
            value = Decimal(token)
        except InvalidOperation:
            continue

        if not value.is_finite() or value < 0:
            continue

        scale_match = SCALE_PATTERN.match(normalized[match.end():])
        if scale_match:
            scale = scale_match.group("scale")
            value *= SCALE_FACTORS[scale]
            candidates.append((value, True))
        else:
            candidates.append((value, False))

    return normalized, candidates


def inspect_amount_visibility(
    text: str,
    expected_amount,
    expected_role: str,
) -> dict[str, bool]:
    """Inspect whether a source amount is visible in text without printing it."""
    normalized, candidates = _numeric_candidates(text or "")
    expected = _decimal(expected_amount)

    role_patterns = ROLE_PATTERNS.get(expected_role, ())
    has_role_cue = any(
        re.search(pattern, normalized, re.IGNORECASE)
        for pattern in role_patterns
    )

    has_money_marker = bool(
        CURRENCY_PATTERN.search(normalized)
        or FULL_SCALE_PATTERN.search(normalized)
        or re.search(
            r"\d\s*م(?![آ-ی])",
            normalized,
        )
    )

    exact_raw = False
    exact_scaled = False
    possible_factor = False

    if expected is not None and expected > 0:
        for candidate, explicit_scale in candidates:
            if candidate == expected:
                if explicit_scale:
                    exact_scaled = True
                else:
                    exact_raw = True
                continue

            if any(
                candidate * factor == expected
                or expected * factor == candidate
                for factor in COMMON_SCALE_FACTORS
            ):
                possible_factor = True

    return {
        "has_number": bool(candidates),
        "has_money_marker": has_money_marker,
        "has_target_role_cue": has_role_cue,
        "exact_raw_number": exact_raw,
        "exact_scaled_expression": exact_scaled,
        "possible_scale_factor_only": (
            possible_factor and not exact_raw and not exact_scaled
        ),
    }


def _open_read_only(database: Path):
    connection = sqlite3.connect(
        database.resolve().as_uri() + "?mode=ro",
        uri=True,
    )
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA query_only=ON")
    return connection


def _sample_rows(connection, sample_per_category: int, seed: int):
    rng = random.Random(seed)
    selected = []

    for category in sorted(FINANCIAL_FIELDS):
        ids = [
            row[0]
            for row in connection.execute(
                "SELECT source_row FROM divar_ads "
                "WHERE cat2_slug=? ORDER BY source_row",
                (category,),
            )
        ]
        selected.extend(
            (category, source_row)
            for source_row in rng.sample(
                ids,
                min(sample_per_category, len(ids)),
            )
        )

    rows = []
    for start in range(0, len(selected), 300):
        chunk = selected[start:start + 300]
        clauses = " OR ".join(
            "(cat2_slug=? AND source_row=?)" for _ in chunk
        )
        params = [
            value
            for pair in chunk
            for value in pair
        ]
        rows.extend(
            dict(row)
            for row in connection.execute(
                f"SELECT * FROM divar_ads WHERE {clauses}",
                params,
            )
        )

    return rows


def _new_stats():
    return {
        "positive": 0,
        "zero": 0,
        "null": 0,
        "has_number": 0,
        "has_money_marker": 0,
        "has_target_role_cue": 0,
        "exact_raw_number": 0,
        "exact_scaled_expression": 0,
        "possible_scale_factor_only": 0,
        "extractor_any_mention": 0,
        "extractor_expected_role": 0,
        "extractor_exact_role_value": 0,
    }


def evaluate_visibility(
    database: Path,
    sample_per_category: int = 300,
    seed: int = 20261030,
) -> str:
    if sample_per_category < 1:
        raise ValueError("sample_per_category must be >= 1")

    stats = defaultdict(_new_stats)
    category_counts = defaultdict(int)

    with _open_read_only(database) as connection:
        columns = {
            row[1]
            for row in connection.execute(
                'PRAGMA table_info("divar_ads")'
            )
        }

        required = {
            "source_row", "cat2_slug", "title", "description",
            *(
                field
                for mapping in FINANCIAL_FIELDS.values()
                for field in mapping
            ),
        }
        missing = required - columns
        if missing:
            raise RuntimeError(
                f"Missing database columns: {sorted(missing)}"
            )

        rows = _sample_rows(
            connection,
            sample_per_category,
            seed,
        )

    for row in rows:
        category = row["cat2_slug"]
        category_counts[category] += 1

        text = "\n".join(
            part
            for part in (
                row.get("title") or "",
                row.get("description") or "",
            )
            if part.strip()
        )

        extraction = extract_text(text)
        mentions = extraction.financial_mentions

        for field, (expected_role,) in FINANCIAL_FIELDS.get(
            category, {}
        ).items():
            item = stats[(category, field)]
            amount = _decimal(row.get(field))

            if amount is None:
                item["null"] += 1
                continue

            if amount == 0:
                item["zero"] += 1
                continue

            item["positive"] += 1

            visibility = inspect_amount_visibility(
                text,
                amount,
                expected_role,
            )

            for key, value in visibility.items():
                if value:
                    item[key] += 1

            if mentions:
                item["extractor_any_mention"] += 1

            role_mentions = [
                mention
                for mention in mentions
                if mention.semantic_role == expected_role
            ]

            if role_mentions:
                item["extractor_expected_role"] += 1

            if any(
                _decimal(mention.normalized_value) == amount
                for mention in role_mentions
            ):
                item["extractor_exact_role_value"] += 1

    lines = [
        "# Divar Financial Text-Visibility Audit",
        "",
        f"- Database: `{database.name}`",
        f"- Sample per category: **{sample_per_category}**",
        f"- Seed: **{seed}**",
        f"- Actual sample size: **{len(rows):,}**",
        "- Database access: read-only",
        "- Raw advertisement text/evidence: not printed or saved",
        "- Currency conversion: none",
        "",
        "> This audit separates source-label visibility from extractor performance. "
        "It does not treat source columns as gold annotations.",
        "",
        "## Sample size",
        "",
        "| Category | Records |",
        "|---|---:|",
    ]

    for category in sorted(category_counts):
        lines.append(
            f"| `{category}` | {category_counts[category]:,} |"
        )

    lines.extend([
        "",
        "## Positive financial labels",
        "",
        "| Category | Field | Positive | Zero | NULL | Has number | Money marker | Role cue | Exact raw | Exact scaled | Possible factor | Extractor any | Extractor role | Extractor exact |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])

    for (category, field), item in sorted(stats.items()):
        lines.append(
            f"| `{category}` | `{field}` | "
            f"{item['positive']} | {item['zero']} | {item['null']} | "
            f"{item['has_number']} | {item['has_money_marker']} | "
            f"{item['has_target_role_cue']} | "
            f"{item['exact_raw_number']} | "
            f"{item['exact_scaled_expression']} | "
            f"{item['possible_scale_factor_only']} | "
            f"{item['extractor_any_mention']} | "
            f"{item['extractor_expected_role']} | "
            f"{item['extractor_exact_role_value']} |"
        )

    lines.extend([
        "",
        "## Interpretation",
        "",
        "- `Exact raw` means the source amount appears as a numeric value without an explicit scale word.",
        "- `Exact scaled` means a numeric token plus an explicit scale word such as million, billion, thousand, or the abbreviated `م` equals the source amount.",
        "- `Possible factor` is diagnostic only; it is not counted as a match and must never trigger automatic conversion.",
        "- `Money marker` means a currency or scale marker occurs somewhere in the text; it does not prove that it belongs to the target amount.",
        "- `Role cue` means a phrase associated with the expected semantic role occurs somewhere in the text; it does not prove that it modifies the target amount.",
        "- `Extractor exact` is the current extractor's exact role-and-value agreement with the source field.",
        "- A source amount absent from text cannot be recovered by a text-only extractor. Such records must remain unavailable/unknown for NLP training labels.",
        "- Zero and NULL source values are reported separately and are not treated as positive numeric labels.",
        "",
        "No raw advertisement text, titles, descriptions, phone numbers, addresses, or evidence snippets are included.",
        "",
    ])

    return "\n".join(lines)
