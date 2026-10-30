"""Conservative mapping of Divar SQLite source labels to Estate NLP weak labels.

Source metadata is weak supervision, not verified truth. Raw source values,
ambiguity, and provenance are preserved. Financial units are never guessed.
"""
from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

_STATUS_MAPPED = "mapped"
_STATUS_AMBIGUOUS = "ambiguous"
_STATUS_MISSING = "missing"
_STATUS_UNMAPPED = "unmapped"
_STATUS_PRESERVED = "preserved"
_STATUS_UNSELECTED = "unselected"

_TRANSACTION_BY_CAT2 = {
    "residential-sell": "sale",
    "commercial-sell": "sale",
    "residential-rent": "rent",
    "commercial-rent": "rent",
    "temporary-rent": "temporary_rent",
}
_PROPERTY_BY_CAT3 = {
    "plot-old": "land",
    "suite-apartment": "suite",
    "villa": "villa",
    "workspace": "workspace",
}
_ROOM_LABELS = {
    "بدون اتاق": "no_room",
    "یک": "one",
    "دو": "two",
    "سه": "three",
    "چهار": "four",
    "پنج یا بیشتر": "five_or_more",
}
_BOOLEAN_SOURCE_FIELDS = {
    "parking": "has_parking",
    "elevator": "has_elevator",
    "warehouse": "has_warehouse",
    "balcony": "has_balcony",
    "pool": "has_pool",
    "jacuzzi": "has_jacuzzi",
    "sauna": "has_sauna",
    "water": "has_water",
    "electricity": "has_electricity",
    "gas": "has_gas",
    "security_guard": "has_security_guard",
    "is_rebuilt": "is_rebuilt",
    "allow_single_person": "rent_to_single",
    "has_business_deed": "has_business_deed",
    "rent_credit_transform": "rent_credit_transform",
    "transformable_price": "transformable_price",
}
_CATEGORICAL_SOURCE_FIELDS = (
    "rent_mode", "rent_type", "price_mode", "credit_mode", "deed_type",
    "has_warm_water_provider", "has_heating_system", "has_cooling_system",
    "has_restroom", "building_direction", "floor_material", "property_type",
    "extra_person_capacity", "floor", "total_floors_count",
    "construction_year",
)
_FINANCIAL_SOURCES = (
    ("price_value", "asking_price", "price_mode"),
    ("rent_value", "monthly_rent", "rent_mode"),
    ("credit_value", "deposit", "credit_mode"),
    ("rent_price_on_regular_days", "daily_rent", None),
    ("rent_price_on_special_days", "special_day_rent", None),
    ("rent_price_at_weekends", "weekend_rent", None),
    ("cost_per_extra_person", "cost_per_extra_person", None),
)


def _label(value: Any, *, status: str, source_field: str | None,
           raw_value: Any, candidates: tuple[Any, ...] = ()) -> dict[str, Any]:
    return {
        "value": value,
        "status": status,
        "source_field": source_field,
        "raw_value": raw_value,
        "candidates": list(candidates),
    }


def _map_category(record: Mapping[str, Any]):
    cat2, cat3 = record.get("cat2_slug"), record.get("cat3_slug")
    if cat3 == "presell":
        transaction = _label("presale", status=_STATUS_MAPPED,
                             source_field="cat3_slug", raw_value=cat3)
    elif cat3 == "partnership":
        transaction = _label("partnership", status=_STATUS_MAPPED,
                             source_field="cat3_slug", raw_value=cat3)
    elif cat2 in _TRANSACTION_BY_CAT2:
        transaction = _label(_TRANSACTION_BY_CAT2[cat2], status=_STATUS_MAPPED,
                             source_field="cat2_slug", raw_value=cat2)
    else:
        transaction = _label(None, status=_STATUS_UNMAPPED,
                             source_field="cat2_slug", raw_value=cat2)

    if cat3 in {"house-villa-sell", "house-villa-rent"}:
        property_type = _label(None, status=_STATUS_AMBIGUOUS,
                               source_field="cat3_slug", raw_value=cat3,
                               candidates=("house", "villa"))
    elif cat3 in {"apartment-sell", "apartment-rent"}:
        value = "apartment"
        property_type = _label(value, status=_STATUS_MAPPED,
                               source_field="cat3_slug", raw_value=cat3)
    elif cat3 in {"shop-sell", "shop-rent"}:
        property_type = _label("shop", status=_STATUS_MAPPED,
                               source_field="cat3_slug", raw_value=cat3)
    elif cat3 in {"office-sell", "office-rent"}:
        property_type = _label("office", status=_STATUS_MAPPED,
                               source_field="cat3_slug", raw_value=cat3)
    elif cat3 in _PROPERTY_BY_CAT3:
        property_type = _label(_PROPERTY_BY_CAT3[cat3], status=_STATUS_MAPPED,
                               source_field="cat3_slug", raw_value=cat3)
    else:
        property_type = _label(None, status=_STATUS_UNMAPPED,
                               source_field="cat3_slug", raw_value=cat3)
    return transaction, property_type


def _map_rooms(raw: Any) -> dict[str, Any]:
    if raw is None or (isinstance(raw, str) and not raw.strip()):
        return _label(None, status=_STATUS_MISSING,
                      source_field="rooms_count", raw_value=raw)
    value = _ROOM_LABELS.get(str(raw).strip())
    if value is None:
        return _label(None, status=_STATUS_UNMAPPED,
                      source_field="rooms_count", raw_value=raw)
    return _label(value, status=_STATUS_MAPPED,
                  source_field="rooms_count", raw_value=raw)


def _map_number(raw: Any, source_field: str) -> dict[str, Any]:
    if raw is None:
        return _label(None, status=_STATUS_MISSING,
                      source_field=source_field, raw_value=raw)
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return _label(None, status=_STATUS_UNMAPPED,
                      source_field=source_field, raw_value=raw)
    if not math.isfinite(value) or value < 0:
        return _label(None, status=_STATUS_UNMAPPED,
                      source_field=source_field, raw_value=raw)
    if value.is_integer():
        value = int(value)
    return _label(value, status=_STATUS_MAPPED,
                  source_field=source_field, raw_value=raw)


def _map_boolean(raw: Any, source_field: str) -> dict[str, Any]:
    if raw is None:
        return _label(None, status=_STATUS_MISSING,
                      source_field=source_field, raw_value=raw)
    if raw in (0, False):
        value = False
    elif raw in (1, True):
        value = True
    else:
        return _label(None, status=_STATUS_UNMAPPED,
                      source_field=source_field, raw_value=raw)
    return _label(value, status=_STATUS_MAPPED,
                  source_field=source_field, raw_value=raw)


def _preserve(raw: Any, source_field: str) -> dict[str, Any]:
    if raw is None or (isinstance(raw, str) and not raw.strip()):
        status = _STATUS_MISSING
    elif isinstance(raw, str) and raw.strip().lower() == "unselect":
        status = _STATUS_UNSELECTED
    else:
        status = _STATUS_PRESERVED
    return _label(raw, status=status, source_field=source_field,
                  raw_value=raw)



def _financial_role_hint(source_field: str, cat2: Any) -> str:
    if source_field == "price_value":
        return "asking_price" if cat2 in {
            "residential-sell", "commercial-sell"
        } else "unknown"
    if source_field == "rent_value":
        return "monthly_rent" if cat2 in {
            "residential-rent", "commercial-rent"
        } else "unknown"
    if source_field == "credit_value":
        return "deposit" if cat2 in {
            "residential-rent", "commercial-rent"
        } else "unknown"
    return {
        "rent_price_on_regular_days": "daily_rent",
        "rent_price_on_special_days": "special_day_rent",
        "rent_price_at_weekends": "weekend_rent",
        "cost_per_extra_person": "cost_per_extra_person",
    }.get(source_field, "unknown")


def _financial_value_status(
    amount: Any,
    mode: Any,
    mode_field: str | None,
) -> str:
    """Interpret the source's financial mode without inferring currency.

    Divar's observed source pairs are internally consistent:
    مقطوع -> positive amount, مجانی -> zero, توافقی -> NULL.
    This remains source metadata, not a verified claim about the ad text.
    """
    if amount is None:
        amount_kind = "missing"
    else:
        try:
            numeric = float(amount)
        except (TypeError, ValueError):
            amount_kind = "invalid"
        else:
            if not math.isfinite(numeric) or numeric < 0:
                amount_kind = "invalid"
            elif numeric == 0:
                amount_kind = "zero"
            else:
                amount_kind = "positive"

    # Temporary-rent fields do not have an associated *_mode column.
    if mode_field is None:
        return {
            "missing": "missing",
            "zero": "zero_amount",
            "positive": "amount_present",
            "invalid": "invalid_amount",
        }[amount_kind]

    if mode is None or (isinstance(mode, str) and not mode.strip()):
        return {
            "missing": "unknown",
            "zero": "zero_without_mode",
            "positive": "amount_without_mode",
            "invalid": "invalid_amount",
        }[amount_kind]

    mode = str(mode).strip()

    if mode == "مقطوع":
        return "fixed_amount" if amount_kind == "positive" else "mode_value_conflict"

    if mode == "مجانی":
        return "free" if amount_kind == "zero" else "mode_value_conflict"

    if mode == "توافقی":
        return "negotiable" if amount_kind == "missing" else "mode_value_conflict"

    return "unrecognized_mode"

def map_divar_record(record: Mapping[str, Any]) -> dict[str, Any]:
    """Map one Divar row without copying title/description into the result.

    Financial amounts retain the source dataset's numeric unit. Currency is
    unspecified because the database itself does not establish a currency.
    """
    if isinstance(record, Mapping):
        pass
    elif hasattr(record, "keys"):
        record = {key: record[key] for key in record.keys()}
    else:
        raise TypeError("record must be a mapping or sqlite-style row")

    transaction, property_type = _map_category(record)
    features = {
        name: _map_boolean(record.get(source), source)
        for name, source in _BOOLEAN_SOURCE_FIELDS.items()
        if name not in {"is_rebuilt", "allow_single_person",
                        "has_business_deed", "rent_credit_transform",
                        "transformable_price"}
    }
    building = {
        "floor": _preserve(record.get("floor"), "floor"),
        "total_floors_count": _preserve(
            record.get("total_floors_count"), "total_floors_count"),
        "units_per_floor": _map_number(
            record.get("unit_per_floor"), "unit_per_floor"),
        "construction_year": _preserve(
            record.get("construction_year"), "construction_year"),
        "is_rebuilt": _map_boolean(record.get("is_rebuilt"), "is_rebuilt"),
        "deed_type": _preserve(record.get("deed_type"), "deed_type"),
        "building_direction": _preserve(
            record.get("building_direction"), "building_direction"),
        "floor_material": _preserve(
            record.get("floor_material"), "floor_material"),
    }
    source_attributes = {
        name: _preserve(record.get(name), name)
        for name in _CATEGORICAL_SOURCE_FIELDS
    }
    source_attributes.update({
        name: _map_boolean(record.get(source), source)
        for name, source in _BOOLEAN_SOURCE_FIELDS.items()
        if name in {"has_business_deed", "rent_credit_transform",
                    "transformable_price"}
    })
    source_attributes["has_barbecue"] = _map_boolean(
        record.get("has_barbecue"), "has_barbecue"
    )

    financial_source_values = []
    cat2 = record.get("cat2_slug")
    for source_field, _role, mode_field in _FINANCIAL_SOURCES:
        amount = record.get(source_field)
        mode = record.get(mode_field) if mode_field else None
        if amount is None and mode is None:
            continue
        financial_source_values.append({
            "source_field": source_field,
            "semantic_role_hint": _financial_role_hint(source_field, cat2),
            "raw_value": amount,
            "source_mode": mode,
            "value_status": _financial_value_status(
                amount, mode, mode_field
            ),
            "currency": "unspecified",
            "unit": "source_dataset_unit",
            "status": "source_label",
        })

    other_source_values = {}
    for name in ("transformable_credit", "transformable_rent",
                 "transformed_credit", "transformed_rent",
                 "regular_person_capacity", "location_radius"):
        raw = record.get(name)
        if raw is not None:
            other_source_values[name] = raw

    source_row = record.get("source_row")
    if source_row is not None:
        try:
            source_row = int(source_row)
        except (TypeError, ValueError):
            source_row = None

    original_labels = {
        name: record.get(name)
        for name in (
            "cat2_slug", "cat3_slug", "city_slug", "neighborhood_slug",
            "created_at_month", "user_type", "rent_mode", "rent_type", "price_mode",
            "credit_mode", "deed_type", "rooms_count",
            "has_warm_water_provider", "has_heating_system",
            "has_cooling_system", "has_restroom", "building_direction",
            "floor_material", "property_type", "extra_person_capacity",
            "floor", "total_floors_count", "construction_year",
            "rent_to_single", "has_barbecue",
        )
    }

    return {
        "mapping_version": "0.2",
        "source": "divar",
        "source_row": source_row,
        "source_category": {
            "cat2_slug": record.get("cat2_slug"),
            "cat3_slug": record.get("cat3_slug"),
        },
        "source_metadata": {
            "created_at_month": record.get("created_at_month"),
            "user_type": record.get("user_type"),
            "location_latitude": record.get("location_latitude"),
            "location_longitude": record.get("location_longitude"),
            "location_radius": record.get("location_radius"),
        },
        "weak_labels": {
            "document_type": _label(
                "listing", status=_STATUS_MAPPED,
                source_field="dataset_record_type",
                raw_value="classified_ad"),
            "transaction_type": transaction,
            "property_type": property_type,
            "building_area_sqm": _map_number(
                record.get("building_size"), "building_size"),
            "land_area_sqm": _map_number(
                record.get("land_size"), "land_size"),
            "rooms": _map_rooms(record.get("rooms_count")),
            "city": _preserve(record.get("city_slug"), "city_slug"),
            "neighborhood": _preserve(
                record.get("neighborhood_slug"), "neighborhood_slug"),
            "features": features,
            "building": building,
            "rental_conditions": {
                "allow_single_person": _map_boolean(
                    record.get("rent_to_single"), "rent_to_single")
            },
        },
        "source_attributes": source_attributes,
        "financial_source_values": financial_source_values,
        "other_source_values": other_source_values,
        "original_dataset_labels": original_labels,
    }
