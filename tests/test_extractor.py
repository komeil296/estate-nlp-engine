import json
from pathlib import Path

import pytest
from jsonschema import validate

from estate_nlp.extractor import extract_text


ROOT = Path(__file__).resolve().parents[1]

SCHEMA = json.loads(
    (ROOT / "schemas" / "extraction.schema.json").read_text(
        encoding="utf-8"
    )
)


def test_basic_listing_extraction():
    text = (
        "فروش آپارتمان ۸۵ متری، دو خواب، "
        "دارای پارکینگ، دارای آسانسور، بدون انباری"
    )

    result = extract_text(text)

    assert result.document_type.value == "listing"
    assert result.transaction_type.value == "sale"
    assert result.property_type.value == "apartment"

    assert result.property.building_area_sqm.value == 85.0
    assert result.property.rooms.value == "two"

    assert result.property.features.parking.value is True
    assert result.property.features.elevator.value is True
    assert result.property.features.warehouse.value is False


def test_land_area_is_separated_from_building_area():
    result = extract_text("فروش زمین ۲۰۰ متر")

    assert result.property_type.value == "land"
    assert result.property.land_area_sqm.value == 200.0
    assert result.property.building_area_sqm.value is None


def test_building_and_land_areas_are_separated():
    result = extract_text(
        "فروش آپارتمان ۸۵ متر بنا و ۱۲۰ متر زمین"
    )

    assert result.property.building_area_sqm.value == 85.0
    assert result.property.land_area_sqm.value == 120.0


def test_ambiguous_room_count_is_preserved():
    result = extract_text("آپارتمان دو خواب و سه خواب")

    assert result.property.rooms.value is None
    assert result.property.rooms.status == "ambiguous"
    assert set(result.property.rooms.candidates) == {"two", "three"}


def test_ambiguous_transaction_is_preserved():
    result = extract_text("فروش یا اجاره آپارتمان")

    assert result.transaction_type.value is None
    assert result.transaction_type.status == "ambiguous"
    assert set(result.transaction_type.candidates) == {"sale", "rent"}


def test_customer_requirement_is_detected():
    result = extract_text(
        "دنبال آپارتمان دو خواب برای خرید هستم"
    )

    assert result.document_type.value == "customer_requirement"
    assert result.transaction_type.value == "sale"


def test_conflicting_feature_mentions_are_not_guessed():
    result = extract_text(
        "آپارتمان دارای پارکینگ، بدون پارکینگ"
    )

    parking = result.property.features.parking

    assert parking.value is None
    assert parking.status == "conflict"
    assert set(parking.candidates) == {True, False}


def test_unknown_features_are_not_false():
    result = extract_text("فروش آپارتمان ۸۰ متری")

    parking = result.property.features.parking

    assert parking.value is None
    assert parking.status == "not_found"


def test_single_person_rental_condition():
    result = extract_text(
        "اجاره آپارتمان، اجاره به مجردین پذیرفته می‌شود"
    )

    condition = result.rental_conditions.allow_single_person

    assert condition.value is True
    assert condition.status == "extracted"


def test_conflicting_single_person_conditions():
    result = extract_text(
        "اجاره به مجردین پذیرفته می‌شود، فقط خانواده"
    )

    condition = result.rental_conditions.allow_single_person

    assert condition.value is None
    assert condition.status == "conflict"


def test_ambiguous_area_without_context_is_not_guessed():
    result = extract_text("۸۵ متر")

    assert result.property.building_area_sqm.value is None
    assert result.property.land_area_sqm.value is None


def test_empty_text():
    result = extract_text("")

    assert result.document_type.value is None
    assert result.transaction_type.value is None
    assert result.financial_mentions == ()


def test_non_string_input_is_rejected():
    with pytest.raises(TypeError):
        extract_text(None)


def test_extraction_output_matches_json_schema():
    result = extract_text(
        "فروش آپارتمان ۸۵ متری، دو خواب، دارای پارکینگ"
    )

    validate(
        instance=result.to_dict(),
        schema=SCHEMA,
    )


def test_provenance_is_preserved():
    result = extract_text(
        "فروش آپارتمان",
        source="divar",
        source_style="listing",
        source_row=150,
        original_dataset_labels={
            "intent": "sale",
            "propertyTypeSource": "apartment-sell",
        },
    )

    provenance = result.to_dict()["provenance"]

    assert provenance["source"] == "divar"
    assert provenance["source_row"] == 150
    assert provenance["original_dataset_labels"]["intent"] == "sale"

def test_single_person_explicit_rejections_are_false():
    examples = (
        "اجاره به مجردین داده نمی‌شود",
        "اجاره به مجردین پذیرفته نمی‌شود",
        "مناسب مجردین نیست",
        "مجردین پذیرفته نمی‌شوند",
    )

    for text in examples:
        result = extract_text(text)
        condition = result.rental_conditions.allow_single_person

        assert condition.value is False, text
        assert condition.status == "extracted", text


def test_single_person_separate_positive_and_negative_mentions():
    result = extract_text(
        "اجاره به مجردین پذیرفته می‌شود، "
        "ولی مناسب مجردین نیست"
    )

    condition = result.rental_conditions.allow_single_person

    assert condition.value is None
    assert condition.status == "conflict"


def test_single_person_positive_pattern_still_works():
    result = extract_text(
        "اجاره به مجردین پذیرفته می‌شود"
    )

    condition = result.rental_conditions.allow_single_person

    assert condition.value is True
    assert condition.status == "extracted"


def test_single_person_family_only_is_false():
    result = extract_text("اجاره آپارتمان فقط خانواده")

    condition = result.rental_conditions.allow_single_person

    assert condition.value is False
    assert condition.status == "extracted"
