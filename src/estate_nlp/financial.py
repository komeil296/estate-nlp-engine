"""Conservative financial mention extraction for Persian real estate text."""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

from .models import FinancialMention
from .normalization import normalize_persian_text


NUMBER_PATTERN = re.compile(
    r"(?<![\w/])"
    r"(?P<number>(?:\d{1,3}(?:[,،٬]\d{3})+|\d+)"
    r"(?:[٫.]\d+)?)"
    r"(?![\w/])"
)

SCALE_PATTERN = (
    r"(?:میلیارد|ملیارد|مليارد|"
    r"میلیون|ملیون|مليون|هزار)"
)

CURRENCY_PATTERN = r"(?:تومان|تومن|ریال)"

SCALE_FACTORS = {
    "میلیارد": Decimal("1000000000"),
    "ملیارد": Decimal("1000000000"),
    "مليارد": Decimal("1000000000"),
    "میلیون": Decimal("1000000"),
    "ملیون": Decimal("1000000"),
    "مليون": Decimal("1000000"),
    "هزار": Decimal("1000"),
}

ROLE_PATTERNS = {
    "price_per_sqm": (
        r"قیمت\s*(?:هر\s*)?متر",
        r"هر\s*متر",
        r"متری",
    ),

    "cost_per_extra_person": (
        r"هزینه\s+(?:هر\s+)?نفر\s+اضافه",
        r"هر\s+نفر\s+اضافه",
        r"نفر\s+اضافه",
        r"نفر\s+مازاد",
    ),

    "special_day_rent": (
        r"روزهای\s+خاص",
        r"روز\s+خاص",
        r"ایام\s+خاص",
        r"ایام\s+ویژه",
        r"تعطیلات\s+خاص",
    ),

    "weekend_rent": (
        r"آخر\s*هفته",
        r"پنجشنبه",
        r"جمعه",
        r"آخرهفته",
    ),

    "daily_rent": (
        r"روزانه",
        r"شبانه",
        r"هر\s*شب",
        r"شبی",
        r"هر\s*روز",
    ),

    "deposit": (
        r"رهن",
        r"ودیعه",
        r"سپرده",
        r"پول\s*پیش",
        r"پیش\s*پرداخت",
        r"پیش(?!\s*فروش)",
    ),

    "monthly_rent": (
        r"اجاره",
        r"کرایه",
        r"ماهانه",
        r"ماهیانه",
        r"ماهی(?![آ-ی])",
        r"ماه\s*به\s*ماه",
    ),

    "budget": (
        r"بودجه",
        r"حداکثر",
        r"تا\s+سقف",
        r"سقف\s+بودجه",
        r"توان\s+پرداخت",
    ),

    "asking_price": (
        r"قیمت",
        r"فروش",
        r"فروشی",
        r"مبلغ\s+کل",
    ),
}

PERIOD_BY_ROLE = {
    "asking_price": "one_time",
    "budget": "one_time",
    "deposit": "one_time",
    "monthly_rent": "month",
    "daily_rent": "day",
    "weekend_rent": "unspecified",
    "special_day_rent": "unspecified",
    "price_per_sqm": "unspecified",
    "cost_per_extra_person": "unspecified",
    "unknown": "unspecified",
}


def _sentence_bounds(text: str, position: int):
    boundaries = re.compile(r"[\n؛;؟!?]+")

    left_matches = list(
        boundaries.finditer(text[:position])
    )

    start = (
        left_matches[-1].end()
        if left_matches
        else 0
    )

    right_match = boundaries.search(text, position)

    end = (
        right_match.start()
        if right_match
        else len(text)
    )

    return start, end


def _find_role(text: str, number_start: int, number_end: int):
    sentence_start, sentence_end = _sentence_bounds(
        text,
        number_start,
    )

    sentence = text[sentence_start:sentence_end]

    candidates = []

    for role, patterns in ROLE_PATTERNS.items():

        for pattern in patterns:

            for match in re.finditer(
                pattern,
                sentence,
                re.IGNORECASE,
            ):

                cue_start = sentence_start + match.start()
                cue_end = sentence_start + match.end()

                if cue_end <= number_start:
                    distance = number_start - cue_end

                elif cue_start >= number_end:
                    distance = cue_start - number_end

                else:
                    distance = 0

                if distance <= 55:
                    candidates.append(
                        (distance, role, (cue_start, cue_end))
                    )

    if not candidates:
        return "unknown", None, None, False

    minimum = min(item[0] for item in candidates)

    nearest = [
        item for item in candidates
        if item[0] == minimum
    ]

    roles = {item[1] for item in nearest}

    if len(roles) != 1:
        return "unknown", minimum, None, True

    selected = min(
        nearest,
        key=lambda item: item[2][0],
    )

    return selected[1], minimum, selected[2], False


def _currency_code(token: str) -> str:
    if token in {"تومان", "تومن"}:
        return "toman"

    if token == "ریال":
        return "rial"

    return "unspecified"


def _parse_expression(
    text: str,
    match: re.Match,
    *,
    allow_short_million: bool = False,
):
    number_text = match.group("number")

    cleaned_number = (
        number_text
        .replace(",", "")
        .replace("،", "")
        .replace("٬", "")
        .replace("٫", ".")
    )

    try:
        amount = Decimal(cleaned_number)

    except InvalidOperation:
        return None

    if not amount.is_finite() or amount < 0:
        return None

    cursor = match.end()

    scale_match = re.match(
        r"\s*(?P<scale>" + SCALE_PATTERN + r")(?![آ-ی])",
        text[cursor:],
    )

    scale = None

    if scale_match:
        scale = scale_match.group("scale")

        amount *= SCALE_FACTORS[scale]

        cursor += scale_match.end()

    elif allow_short_million:
        # In property ads, a standalone "م" commonly abbreviates million.
        # Only enable it when a nearby financial-role cue exists; otherwise
        # it could be confused with meter or another abbreviation.
        short_million = re.match(r"\s*م(?![آ-ی])", text[cursor:])
        if short_million:
            scale = "م"
            amount *= Decimal("1000000")
            cursor += short_million.end()

    suffix_currency = re.match(
        r"\s*(?P<currency>" + CURRENCY_PATTERN + r")(?![آ-ی])",
        text[cursor:],
    )

    prefix_start = match.start()
    prefix_currency = None

    prefix_left = max(0, match.start() - 20)

    prefix = text[prefix_left:match.start()]

    prefix_match = re.search(
        r"(?P<currency>" + CURRENCY_PATTERN + r")\s*$",
        prefix,
    )

    if prefix_match:
        prefix_currency = prefix_match.group("currency")

        prefix_start = (
            prefix_left + prefix_match.start()
        )

    suffix_code = None
    suffix_end = cursor

    if suffix_currency:
        suffix_code = suffix_currency.group("currency")

        suffix_end = cursor + suffix_currency.end()

    currency_codes = []

    if prefix_currency:
        currency_codes.append(
            _currency_code(prefix_currency)
        )

    if suffix_code:
        currency_codes.append(
            _currency_code(suffix_code)
        )

    unique_codes = set(currency_codes)

    currency = (
        next(iter(unique_codes))
        if len(unique_codes) == 1
        else "unspecified"
    )

    raw_end = (
        suffix_end
        if suffix_currency
        else cursor
    )

    normalized_value = (
        int(amount)
        if amount == amount.to_integral_value()
        else float(amount)
    )

    raw_value = text[prefix_start:raw_end].strip()

    has_money_marker = bool(
        scale or prefix_currency or suffix_code
    )

    return (
        normalized_value,
        currency,
        raw_value,
        prefix_start,
        raw_end,
        has_money_marker,
    )


def _is_non_financial_measurement(
    text: str,
    number_start: int,
    raw_end: int,
    role: str,
):
    suffix = text[raw_end:raw_end + 24]

    if role != "cost_per_extra_person":

        if re.match(
            r"\s*(?:متر(?:\s*مربع)?|مترمربع|متری|مربع|"
            r"خواب(?:ه)?|طبقه|سال(?:ه)?|ساعت(?:ه)?|"
            r"درصد|درجه|کیلومتر|واحد|اتاق|نفر)(?![آ-ی])",
            suffix,
        ):
            return True

    prefix = text[max(0, number_start - 24):number_start]

    if re.search(
        r"(?:ساخت|سال(?:\s+ساخت)?|طبقه|خواب|اتاق|"
        r"متراژ|مساحت|ابعاد|شماره|کد|پلاک|واحد|"
        r"تعداد\s+واحد)\s*$",
        prefix,
    ):
        return True

    if re.search(
        r"(?:تماس|تلفن|موبایل|شماره\s+تماس)\s*$",
        prefix,
    ):
        return True

    return False


def _make_evidence(
    text: str,
    number_start: int,
    raw_end: int,
    cue_span,
):
    start, end = _sentence_bounds(text, number_start)

    if end - start <= 220:
        return text[start:end].strip()

    left = number_start - 45
    right = raw_end + 45

    if cue_span:
        left = min(left, cue_span[0] - 12)
        right = max(right, cue_span[1] + 12)

    return text[
        max(start, left):min(end, right)
    ].strip()


def extract_financial_mentions(
    text: str,
    transaction_type: str | None = None,
) -> tuple[FinancialMention, ...]:
    """
    Extract financial amounts while preserving currency and semantic roles.

    Unknown currency is never silently converted.
    Numbers without financial context are ignored.
    Multiple financial mentions are preserved independently.
    """

    if not isinstance(text, str):
        raise TypeError("text must be a string")

    normalized = normalize_persian_text(text)

    normalized = normalized.replace("\u200c", " ")

    mentions = []

    for match in NUMBER_PATTERN.finditer(normalized):

        role, distance, cue_span, ambiguous_role = _find_role(
            normalized,
            match.start(),
            match.end(),
        )

        parsed = _parse_expression(
            normalized,
            match,
            allow_short_million=(
                role in {
                    "asking_price",
                    "budget",
                    "deposit",
                    "monthly_rent",
                    "daily_rent",
                    "weekend_rent",
                    "special_day_rent",
                    "price_per_sqm",
                    "cost_per_extra_person",
                }
                and distance is not None
                and distance <= 32
            ),
        )

        if parsed is None:
            continue

        (
            value,
            currency,
            raw_value,
            raw_start,
            raw_end,
            has_money_marker,
        ) = parsed

        if (
            role == "unknown"
            and not ambiguous_role
            and transaction_type == "sale"
            and has_money_marker
        ):
            role = "asking_price"

        if (
            not has_money_marker
            and (distance is None or distance > 32)
        ):
            continue

        if _is_non_financial_measurement(
            normalized,
            match.start(),
            raw_end,
            role,
        ):
            continue

        evidence = _make_evidence(
            normalized,
            match.start(),
            raw_end,
            cue_span,
        )

        if not evidence:
            evidence = raw_value

        mentions.append(
            FinancialMention(
                semantic_role=role,
                raw_value=raw_value,
                normalized_value=value,
                currency=currency,
                period=PERIOD_BY_ROLE[role],
                evidence=evidence,
            )
        )

    return tuple(mentions)
