import json
from pathlib import Path

import pytest
from jsonschema import validate

from estate_nlp.models import (
    BuildingDetails,
    ExtractionResult,
    FieldResult,
    FinancialMention,
    Location,
    PropertyDetails,
    PropertyFeatures,
    Provenance,
    RentalConditions,
)


ROOT = Path(__file__).resolve().parents[1]

SCHEMA = json.loads(
    (ROOT / "schemas" / "extraction.schema.json").read_text(
        encoding="utf-8"
    )
)


def string_result(value=None, evidence=()):
    return FieldResult(
        value=value,
        status="extracted" if value is not None else "not_found",
        evidence=evidence,
    )


def number_result(value=None, evidence=()):
    return FieldResult(
        value=value,
        status="extracted" if value is not None else "not_found",
        evidence=evidence,
    )


def boolean_result(value=None, evidence=()):
    return FieldResult(
        value=value,
        status="extracted" if value is not None else "not_found",
        evidence=evidence,
    )


def make_result():
    building = BuildingDetails(
        floor=string_result(),
        total_floors=number_result(),
        units_per_floor=number_result(),
        construction_year=number_result(),
        is_rebuilt=boolean_result(),
        deed_type=string_result(),
        building_direction=string_result(),
        floor_material=string_result(),
    )

    features = PropertyFeatures(
        parking=boolean_result(True, ("دارای پارکینگ",)),
        elevator=boolean_result(False, ("بدون آسانسور",)),
        warehouse=boolean_result(),
        balcony=boolean_result(),
        pool=boolean_result(),
        jacuzzi=boolean_result(),
        sauna=boolean_result(),
        water=boolean_result(),
        electricity=boolean_result(),
        gas=boolean_result(),
        heating=boolean_result(),
        cooling=boolean_result(),
        restroom=boolean_result(),
        security_guard=boolean_result(),
    )

    property_details = PropertyDetails(
        building_area_sqm=number_result(85, ("۸۵ متر",)),
        land_area_sqm=number_result(),
        rooms=FieldResult(
            value="two",
            status="extracted",
            evidence=("دو خواب",),
        ),
        building=building,
        features=features,
    )

    financial = (
        FinancialMention(
            semantic_role="deposit",
            raw_value="۵۰۰ میلیون",
            normalized_value=500_000_000,
            currency="toman",
            period="one_time",
            evidence="۵۰۰ میلیون رهن",
        ),
        FinancialMention(
            semantic_role="monthly_rent",
            raw_value="۱۰ میلیون",
            normalized_value=10_000_000,
            currency="toman",
            period="month",
            evidence="۱۰ میلیون اجاره",
        ),
    )

    return ExtractionResult(
        document_type=FieldResult(
            value="listing",
            status="extracted",
            evidence=("آگهی فروش آپارتمان",),
        ),
        transaction_type=FieldResult(
            value="rent",
            status="extracted",
            evidence=("اجاره داده می‌شود",),
        ),
        property_type=FieldResult(
            value="apartment",
            status="extracted",
            evidence=("آپارتمان",),
        ),
        location=Location(
            city=string_result("tehran", ("تهران",)),
            neighborhood=string_result(),
        ),
        property=property_details,
        financial_mentions=financial,
        rental_conditions=RentalConditions(
            allow_single_person=boolean_result()
        ),
        provenance=Provenance(
            source="divar",
            source_style="listing_title_and_description",
            source_row=150,
            original_dataset_labels={
                "intent": "rent",
                "propertyTypeSource": "apartment-rent",
            },
        ),
    )


def test_extraction_result_matches_json_schema():
    result = make_result()

    validate(
        instance=result.to_dict(),
        schema=SCHEMA,
    )


def test_missing_boolean_is_not_false():
    result = make_result().to_dict()

    assert result["rental_conditions"]["allow_single_person"]["value"] is None
    assert result["property"]["features"]["warehouse"]["value"] is None


def test_explicit_false_is_preserved():
    result = make_result().to_dict()

    elevator = result["property"]["features"]["elevator"]

    assert elevator["value"] is False
    assert elevator["status"] == "extracted"


def test_multiple_financial_mentions_are_preserved():
    result = make_result().to_dict()

    mentions = result["financial_mentions"]

    assert len(mentions) == 2
    assert mentions[0]["semantic_role"] == "deposit"
    assert mentions[1]["semantic_role"] == "monthly_rent"


def test_confidence_cannot_be_set_before_calibration():
    with pytest.raises(ValueError):
        FieldResult(
            value="apartment",
            status="extracted",
            confidence=0.95,
        )


def test_negative_financial_value_is_rejected():
    with pytest.raises(ValueError):
        FinancialMention(
            semantic_role="asking_price",
            raw_value="قیمت",
            normalized_value=-100,
            currency="toman",
            period="one_time",
            evidence="قیمت ملک",
        )


def test_original_dataset_labels_are_preserved():
    result = make_result().to_dict()

    labels = result["provenance"]["original_dataset_labels"]

    assert labels["intent"] == "rent"
    assert labels["propertyTypeSource"] == "apartment-rent"


def test_result_can_be_serialized_to_json():
    result = make_result()

    serialized = json.dumps(
        result.to_dict(),
        ensure_ascii=False,
    )

    assert "financial_mentions" in serialized
    assert "provenance" in serialized


def test_invalid_source_row_is_rejected():
    with pytest.raises(ValueError):
        Provenance(
            source="divar",
            source_style=None,
            source_row=0,
        )