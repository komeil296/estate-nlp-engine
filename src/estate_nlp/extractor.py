"""Deterministic rule-based extractor for Persian real estate text."""

import re
from typing import Any

from .normalization import normalize_persian_text
from .financial import extract_financial_mentions
from .models import (
    BuildingDetails,
    ExtractionResult,
    FieldResult,
    Location,
    PropertyDetails,
    PropertyFeatures,
    Provenance,
    RentalConditions,
)


def _not_found():
    return FieldResult(value=None, status="not_found")


def _collect(text, patterns):
    found = []

    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            value = match.group(0).strip()

            if value and value not in found:
                found.append(value)

    return tuple(found)


def _resolve(matches):
    if not matches:
        return _not_found()

    values = []

    for value, evidence in matches:
        if value not in values:
            values.append(value)

    evidence = tuple(dict.fromkeys(
        item[1] for item in matches
    ))

    if len(values) == 1:
        return FieldResult(
            value=values[0],
            status="extracted",
            evidence=evidence,
        )

    return FieldResult(
        value=None,
        status="ambiguous",
        evidence=evidence,
        candidates=tuple(values),
    )


def _extract_transaction(text):
    temporary = _collect(text, (
        r"اجاره\s*(?:روزانه|شبانه|ساعتی)",
        r"کوتاه\s*مدت",
        r"اقامت\s+روزانه",
    ))

    presale = _collect(text, (
        r"پیش\s*فروش",
    ))

    partnership = _collect(text, (
        r"مشارکت\s+در\s+ساخت",
    ))

    sale = _collect(text, (
        r"فروش",
        r"فروشی",
        r"خرید",
        r"خریدار",
    ))

    rent = _collect(text, (
        r"اجاره",
        r"رهن",
    ))

    service = _collect(text, (
        r"خدمات\s+املاک",
        r"خدمات\s+ملکی",
    ))

    matches = []

    for item in temporary:
        matches.append(("temporary_rent", item))

    for item in presale:
        matches.append(("presale", item))

    for item in partnership:
        matches.append(("partnership", item))

    if sale and not presale:
        matches.extend(("sale", item) for item in sale)

    if rent and not temporary:
        matches.extend(("rent", item) for item in rent)

    matches.extend(("service", item) for item in service)

    return _resolve(matches)


def _extract_property_type(text):
    patterns = {
        "apartment": (
            r"آپارتمان",
            r"واحد\s+مسکونی",
        ),
        "villa": (
            r"ویلا",
            r"ویلایی",
        ),
        "house": (
            r"خانه",
            r"منزل",
        ),
        "land": (
            r"زمین",
            r"قطعه\s+زمین",
            r"باغ",
        ),
        "shop": (
            r"مغازه",
            r"واحد\s+تجاری",
            r"فروشگاه",
        ),
        "office": (
            r"دفتر\s+اداری",
            r"اداری",
        ),
        "workspace": (
            r"فضای\s+کار\s+اشتراکی",
            r"کوارکینگ",
        ),
        "industrial": (
            r"سوله",
            r"کارخانه",
            r"کارگاه",
            r"صنعتی",
        ),
        "suite": (
            r"سوئیت",
            r"سوییت",
        ),
    }

    matches = []

    for property_type, expressions in patterns.items():
        for evidence in _collect(text, expressions):
            matches.append((property_type, evidence))

    return _resolve(matches)


def _extract_document_type(text, transaction, property_type):
    request = _collect(text, (
        r"دنبال",
        r"می\s*خواهم",
        r"میخوام",
        r"می\s*خوام",
        r"نیاز\s+دارم",
        r"بودجه\s+دارم",
        r"قصد\s+خرید",
    ))

    if request:
        return FieldResult(
            value="customer_requirement",
            status="extracted",
            evidence=request,
        )

    listing = _collect(text, (
        r"آگهی",
        r"فروش",
        r"فروشی",
        r"اجاره",
        r"رهن",
        r"پیش\s*فروش",
        r"مشارکت\s+در\s+ساخت",
    ))

    if listing or transaction.evidence or property_type.evidence:
        evidence = tuple(dict.fromkeys(
            listing
            + transaction.evidence
            + property_type.evidence
        ))

        return FieldResult(
            value="listing",
            status="extracted",
            evidence=evidence,
        )

    conversation = _collect(text, (
        r"سلام",
        r"ممنون",
        r"متشکرم",
        r"لطفا",
        r"سپاس",
    ))

    if conversation:
        return FieldResult(
            value="conversation",
            status="extracted",
            evidence=conversation,
        )

    return _not_found()


ROOM_PATTERN = re.compile(
    r"(?P<zero>بدون\s+(?:اتاق\s+)?خواب)"
    r"|(?P<count>\d+|یک|یه|دو|سه|چهار|پنج|شش)"
    r"\s*(?:اتاق\s*خواب|خوابه|خواب)",
    re.IGNORECASE,
)

ROOM_WORDS = {
    "یک": 1,
    "یه": 1,
    "دو": 2,
    "سه": 3,
    "چهار": 4,
    "پنج": 5,
    "شش": 6,
}


def _extract_rooms(text):
    matches = []

    for match in ROOM_PATTERN.finditer(text):
        if match.group("zero"):
            value = "no_room"
        else:
            token = match.group("count")

            number = (
                int(token)
                if token.isdigit()
                else ROOM_WORDS[token]
            )

            if number == 0:
                value = "no_room"
            elif number == 1:
                value = "one"
            elif number == 2:
                value = "two"
            elif number == 3:
                value = "three"
            elif number == 4:
                value = "four"
            else:
                value = "five_or_more"

        matches.append((value, match.group(0)))

    return _resolve(matches)


AREA_PATTERN = re.compile(
    r"(?P<number>\d[\d,]*(?:\.\d+)?)"
    r"\s*(?:متر\s*مربع|مترمربع|متری|متر|m2|sqm)",
    re.IGNORECASE,
)

LAND_CUES = (
    r"زمین",
    r"عرصه",
    r"قطعه",
    r"باغ",
)

BUILDING_CUES = (
    r"زیربنا",
    r"زیر\s+بنا",
    r"بنا",
    r"ساختمان",
    r"آپارتمان",
    r"واحد",
    r"مغازه",
    r"دفتر",
    r"سوله",
)

BUILDING_TYPES = {
    "apartment",
    "house",
    "villa",
    "shop",
    "office",
    "workspace",
    "industrial",
    "suite",
}


def _nearest_cue_distance(window, start, end, cues):
    distances = []

    for cue in cues:
        for match in re.finditer(cue, window):
            if match.end() <= start:
                distance = start - match.end()
            elif match.start() >= end:
                distance = match.start() - end
            else:
                distance = 0

            distances.append(distance)

    return min(distances) if distances else None


def _extract_areas(text, property_type):
    building_matches = []
    land_matches = []

    for match in AREA_PATTERN.finditer(text):
        raw_number = match.group("number").replace(",", "")

        try:
            value = float(raw_number)
        except ValueError:
            continue

        window_start = max(0, match.start() - 32)
        window_end = min(len(text), match.end() + 32)

        window = text[window_start:window_end]

        local_start = match.start() - window_start
        local_end = match.end() - window_start

        land_distance = _nearest_cue_distance(
            window,
            local_start,
            local_end,
            LAND_CUES,
        )

        building_distance = _nearest_cue_distance(
            window,
            local_start,
            local_end,
            BUILDING_CUES,
        )

        if land_distance is not None or building_distance is not None:

            if (
                land_distance is not None
                and (
                    building_distance is None
                    or land_distance < building_distance
                )
            ):
                target = "land"

            elif (
                building_distance is not None
                and (
                    land_distance is None
                    or building_distance < land_distance
                )
            ):
                target = "building"

            else:
                continue

        elif property_type.value == "land":
            target = "land"

        elif property_type.value in BUILDING_TYPES:
            target = "building"

        else:
            continue

        evidence = match.group(0)

        if target == "land":
            land_matches.append((value, evidence))
        else:
            building_matches.append((value, evidence))

    return (
        _resolve(building_matches),
        _resolve(land_matches),
    )


def _boolean_field(text, positive_patterns, negative_patterns):
    positive = _collect(text, positive_patterns)
    negative = _collect(text, negative_patterns)

    evidence = tuple(dict.fromkeys(positive + negative))

    if positive and negative:
        return FieldResult(
            value=None,
            status="conflict",
            evidence=evidence,
            candidates=(True, False),
        )

    if positive:
        return FieldResult(
            value=True,
            status="extracted",
            evidence=positive,
        )

    if negative:
        return FieldResult(
            value=False,
            status="extracted",
            evidence=negative,
        )

    return _not_found()


FEATURE_PATTERNS = {
    "parking": (
        (
            r"دارای\s+پارکینگ",
            r"با\s+پارکینگ",
            r"پارکینگ\s+دارد",
        ),
        (
            r"بدون\s+پارکینگ",
            r"فاقد\s+پارکینگ",
            r"پارکینگ\s+ندارد",
        ),
    ),
    "elevator": (
        (
            r"دارای\s+آسانسور",
            r"با\s+آسانسور",
            r"آسانسور\s+دارد",
        ),
        (
            r"بدون\s+آسانسور",
            r"فاقد\s+آسانسور",
            r"آسانسور\s+ندارد",
        ),
    ),
    "warehouse": (
        (
            r"دارای\s+انباری",
            r"با\s+انباری",
            r"انباری\s+دارد",
        ),
        (
            r"بدون\s+انباری",
            r"فاقد\s+انباری",
            r"انباری\s+ندارد",
        ),
    ),
    "balcony": (
        (
            r"دارای\s+بالکن",
            r"با\s+بالکن",
            r"بالکن\s+دارد",
        ),
        (
            r"بدون\s+بالکن",
            r"فاقد\s+بالکن",
            r"بالکن\s+ندارد",
        ),
    ),
    "pool": (
        (
            r"دارای\s+استخر",
            r"استخر\s+دارد",
        ),
        (
            r"بدون\s+استخر",
            r"فاقد\s+استخر",
            r"استخر\s+ندارد",
        ),
    ),
    "jacuzzi": (
        (
            r"دارای\s+جکوزی",
            r"جکوزی\s+دارد",
        ),
        (
            r"بدون\s+جکوزی",
            r"فاقد\s+جکوزی",
            r"جکوزی\s+ندارد",
        ),
    ),
    "sauna": (
        (
            r"دارای\s+سونا",
            r"سونا\s+دارد",
        ),
        (
            r"بدون\s+سونا",
            r"فاقد\s+سونا",
            r"سونا\s+ندارد",
        ),
    ),
    "water": (
        (
            r"دارای\s+آب",
            r"انشعاب\s+آب",
            r"آب\s+شهری",
            r"آب\s+دارد",
        ),
        (
            r"بدون\s+آب",
            r"فاقد\s+آب",
            r"آب\s+ندارد",
        ),
    ),
    "electricity": (
        (
            r"دارای\s+برق",
            r"انشعاب\s+برق",
            r"برق\s+دارد",
        ),
        (
            r"بدون\s+برق",
            r"فاقد\s+برق",
            r"برق\s+ندارد",
        ),
    ),
    "gas": (
        (
            r"دارای\s+گاز",
            r"انشعاب\s+گاز",
            r"گاز\s+دارد",
        ),
        (
            r"بدون\s+گاز",
            r"فاقد\s+گاز",
            r"گاز\s+ندارد",
        ),
    ),
    "heating": (
        (
            r"سیستم\s+گرمایش",
            r"دارای\s+گرمایش",
            r"گرمایش\s+مرکزی",
            r"شوفاژ\s+دارد",
            r"پکیج\s+دارد",
        ),
        (
            r"بدون\s+(?:سیستم\s+)?گرمایش",
            r"فاقد\s+گرمایش",
            r"گرمایش\s+ندارد",
            r"بدون\s+شوفاژ",
        ),
    ),
    "cooling": (
        (
            r"سیستم\s+سرمایش",
            r"دارای\s+سرمایش",
            r"کولر\s+دارد",
            r"اسپیلت\s+دارد",
        ),
        (
            r"بدون\s+(?:سیستم\s+)?سرمایش",
            r"فاقد\s+سرمایش",
            r"سرمایش\s+ندارد",
            r"بدون\s+کولر",
        ),
    ),
    "restroom": (
        (
            r"دارای\s+سرویس\s+بهداشتی",
            r"سرویس\s+بهداشتی\s+دارد",
            r"دارای\s+توالت",
        ),
        (
            r"بدون\s+سرویس\s+بهداشتی",
            r"فاقد\s+سرویس\s+بهداشتی",
            r"توالت\s+ندارد",
        ),
    ),
    "security_guard": (
        (
            r"دارای\s+نگهبان",
            r"نگهبان\s+دارد",
            r"سرایدار\s+دارد",
            r"نگهبانی\s+۲۴\s+ساعته",
        ),
        (
            r"بدون\s+نگهبان",
            r"فاقد\s+نگهبان",
            r"نگهبان\s+ندارد",
        ),
    ),
}


def _extract_features(text):
    fields = {}

    for name, (positive, negative) in FEATURE_PATTERNS.items():
        fields[name] = _boolean_field(
            text,
            positive,
            negative,
        )

    return PropertyFeatures(**fields)


def _extract_single_person(text):
    positive = (
        r"اجاره\s+به\s+مجرد(?:ین)?(?![آ-ی])"
        r"(?!\s+(?:(?:داده|پذیرفته)\s+)?نمی\s*شود)"
        r"(?!\s+ممنوع)",

        r"مناسب\s+مجرد(?:ین)?(?![آ-ی])(?!\s+نیست)",

        r"مجرد(?:ین)?\s+پذیرفته\s+می\s*شود",

        r"پذیرش\s+مجرد(?:ین)?\s+(?:داریم|مجاز\s+است)",

        r"فقط\s+مجرد(?:ین)?(?![آ-ی])"
        r"(?!\s+(?:پذیرفته\s+)?نمی\s*شوند)",
    )

    negative = (
        r"فقط\s+خانواده",

        r"مجرد(?:ین)?\s+پذیرش\s+ندارد",

        r"(?:به\s+)?مجرد(?:ین)?\s+اجاره\s+داده\s+نمی\s*شود",

        r"اجاره\s+به\s+مجرد(?:ین)?\s+"
        r"(?:نداریم|ممنوع(?:\s+است)?|نیست|"
        r"(?:(?:داده|پذیرفته)\s+)?نمی\s*شود)",

        r"مناسب\s+مجرد(?:ین)?\s+نیست",

        r"مجرد(?:ین)?\s+پذیرفته\s+نمی\s*شوند",

        r"پذیرش\s+مجرد(?:ین)?\s+(?:نداریم|ممنوع\s+است)",

        r"فقط\s+مجرد(?:ین)?\s+(?:پذیرفته\s+)?نمی\s*شوند",
    )

    return _boolean_field(text, positive, negative)


def extract_text(
    text: str,
    *,
    source: str | None = None,
    source_style: str | None = "free_text",
    source_row: int | None = None,
    original_dataset_labels: dict[str, Any] | None = None,
) -> ExtractionResult:
    """Extract conservative structured facts from Persian property text."""

    normalized = normalize_persian_text(text)

    # Make half-spaces equivalent to ordinary spaces for pattern matching.
    text = normalized.replace("\u200c", " ")

    transaction = _extract_transaction(text)
    property_type = _extract_property_type(text)

    document_type = _extract_document_type(
        text,
        transaction,
        property_type,
    )

    building_area, land_area = _extract_areas(
        text,
        property_type,
    )

    rooms = _extract_rooms(text)

    building = BuildingDetails(
        floor=_not_found(),
        total_floors=_not_found(),
        units_per_floor=_not_found(),
        construction_year=_not_found(),
        is_rebuilt=_not_found(),
        deed_type=_not_found(),
        building_direction=_not_found(),
        floor_material=_not_found(),
    )

    property_details = PropertyDetails(
        building_area_sqm=building_area,
        land_area_sqm=land_area,
        rooms=rooms,
        building=building,
        features=_extract_features(text),
    )

    return ExtractionResult(
        document_type=document_type,
        transaction_type=transaction,
        property_type=property_type,
        location=Location(
            city=_not_found(),
            neighborhood=_not_found(),
        ),
        property=property_details,
        financial_mentions=extract_financial_mentions(
            text,
            transaction_type=transaction.value,
        ),
        rental_conditions=RentalConditions(
            allow_single_person=_extract_single_person(text)
        ),
        provenance=Provenance(
            source=source,
            source_style=source_style,
            source_row=source_row,
            original_dataset_labels=(
                original_dataset_labels or {}
            ),
        ),
    )