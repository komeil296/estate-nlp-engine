import copy
import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "extraction.schema.json"

SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
VALIDATOR = Draft202012Validator(SCHEMA)


def not_found():
    return {
        "value": None,
        "status": "not_found",
        "evidence": [],
        "confidence": None,
        "candidates": []
    }


def extracted(value, evidence):
    return {
        "value": value,
        "status": "extracted",
        "evidence": [evidence],
        "confidence": None,
        "candidates": []
    }


def valid_payload():
    features = {
        name: not_found()
        for name in [
            "parking", "elevator", "warehouse", "balcony",
            "pool", "jacuzzi", "sauna", "water",
            "electricity", "gas", "heating", "cooling",
            "restroom", "security_guard"
        ]
    }

    features["parking"] = extracted(False, "بدون پارکینگ")

    return {
        "schema_version": "0.2",
        "document_type": extracted("listing", "فروش آپارتمان"),
        "transaction_type": extracted("sale", "فروش"),
        "property_type": extracted("apartment", "آپارتمان"),
        "location": {
            "city": extracted("tehran", "تهران"),
            "neighborhood": not_found()
        },
        "property": {
            "building_area_sqm": extracted(85, "۸۵ متر"),
            "land_area_sqm": not_found(),
            "rooms": extracted("two", "دو خواب"),
            "building": {
                "floor": not_found(),
                "total_floors": not_found(),
                "units_per_floor": not_found(),
                "construction_year": not_found(),
                "is_rebuilt": not_found(),
                "deed_type": not_found(),
                "building_direction": not_found(),
                "floor_material": not_found()
            },
            "features": features
        },
        "financial_mentions": [
            {
                "semantic_role": "asking_price",
                "raw_value": "۱۲ میلیارد تومان",
                "normalized_value": 12000000000,
                "currency": "toman",
                "period": "one_time",
                "evidence": "۱۲ میلیارد تومان"
            }
        ],
        "rental_conditions": {
            "allow_single_person": not_found()
        },
        "provenance": {
            "source": "divar",
            "source_style": "listing_title_and_description",
            "source_row": 2,
            "original_dataset_labels": {
                "intent": "sell"
            }
        }
    }


def assert_valid(payload):
    errors = list(VALIDATOR.iter_errors(payload))
    assert not errors, [
        f"{error.json_path}: {error.message}"
        for error in errors
    ]


def test_schema_definition_is_valid():
    Draft202012Validator.check_schema(SCHEMA)


def test_valid_extraction_result():
    assert_valid(valid_payload())


def test_false_is_a_valid_extracted_boolean():
    payload = valid_payload()
    parking = payload["property"]["features"]["parking"]

    assert parking["value"] is False
    assert parking["status"] == "extracted"

    assert_valid(payload)


def test_extracted_field_requires_evidence():
    payload = valid_payload()
    payload["location"]["city"]["evidence"] = []

    errors = list(VALIDATOR.iter_errors(payload))
    assert errors


def test_not_found_cannot_contain_value():
    payload = valid_payload()
    payload["location"]["neighborhood"] = extracted(
        "saadat-abad",
        "سعادت آباد"
    )
    payload["location"]["neighborhood"]["status"] = "not_found"

    assert list(VALIDATOR.iter_errors(payload))


def test_ambiguous_requires_multiple_candidates():
    payload = valid_payload()

    payload["location"]["city"] = {
        "value": None,
        "status": "ambiguous",
        "evidence": ["تهران یا کرج"],
        "confidence": None,
        "candidates": ["tehran"]
    }

    assert list(VALIDATOR.iter_errors(payload))


def test_confidence_must_remain_null():
    payload = valid_payload()
    payload["document_type"]["confidence"] = 0.95

    assert list(VALIDATOR.iter_errors(payload))


def test_negative_financial_value_is_rejected():
    payload = valid_payload()
    payload["financial_mentions"][0]["normalized_value"] = -100

    assert list(VALIDATOR.iter_errors(payload))


def test_unknown_root_properties_are_rejected():
    payload = valid_payload()
    payload["unexpected"] = "invalid"

    assert list(VALIDATOR.iter_errors(payload))


def test_not_found_is_distinct_from_false():
    payload = valid_payload()

    parking = payload["property"]["features"]["parking"]
    elevator = payload["property"]["features"]["elevator"]

    assert parking["value"] is False
    assert parking["status"] == "extracted"

    assert elevator["value"] is None
    assert elevator["status"] == "not_found"

    assert_valid(payload)


def test_ambiguous_field_can_preserve_candidates():
    payload = valid_payload()

    payload["location"]["city"] = {
        "value": None,
        "status": "ambiguous",
        "evidence": ["تهران یا کرج"],
        "confidence": None,
        "candidates": ["tehran", "karaj"]
    }

    assert_valid(payload)