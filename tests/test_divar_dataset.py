import pytest

from estate_nlp.divar_dataset import map_divar_record


def test_residential_sale_category_maps_to_sale_and_apartment():
    result = map_divar_record({
        "cat2_slug": "residential-sell",
        "cat3_slug": "apartment-sell",
    })
    labels = result["weak_labels"]

    assert labels["transaction_type"]["value"] == "sale"
    assert labels["transaction_type"]["source_field"] == "cat2_slug"
    assert labels["property_type"]["value"] == "apartment"


def test_presale_and_partnership_use_specific_cat3_label():
    presale = map_divar_record({
        "cat2_slug": "real-estate-services",
        "cat3_slug": "presell",
    })
    partnership = map_divar_record({
        "cat2_slug": "real-estate-services",
        "cat3_slug": "partnership",
    })

    assert presale["weak_labels"]["transaction_type"]["value"] == "presale"
    assert partnership["weak_labels"]["transaction_type"]["value"] == "partnership"


@pytest.mark.parametrize("cat3", ["house-villa-sell", "house-villa-rent"])
def test_house_villa_category_remains_ambiguous(cat3):
    result = map_divar_record({"cat3_slug": cat3})
    field = result["weak_labels"]["property_type"]

    assert field["value"] is None
    assert field["status"] == "ambiguous"
    assert set(field["candidates"]) == {"house", "villa"}


def test_temporary_property_setting_is_not_mapped_to_property_type():
    result = map_divar_record({
        "cat2_slug": "temporary-rent",
        "cat3_slug": "villa",
        "property_type": "jungle",
    })
    labels = result["weak_labels"]

    assert labels["transaction_type"]["value"] == "temporary_rent"
    assert labels["property_type"]["value"] == "villa"
    assert result["source_attributes"]["property_type"]["raw_value"] == "jungle"


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("بدون اتاق", "no_room"),
        ("یک", "one"),
        ("دو", "two"),
        ("سه", "three"),
        ("چهار", "four"),
        ("پنج یا بیشتر", "five_or_more"),
    ],
)
def test_room_count_source_values_are_mapped(raw, expected):
    result = map_divar_record({"rooms_count": raw})
    assert result["weak_labels"]["rooms"]["value"] == expected


def test_null_boolean_is_not_false_and_zero_is_preserved():
    result = map_divar_record({
        "has_parking": 0,
        "has_elevator": None,
        "price_value": 0,
        "price_mode": "مجانی",
    })
    labels = result["weak_labels"]

    assert labels["features"]["parking"]["value"] is False
    assert labels["features"]["elevator"]["value"] is None
    assert labels["features"]["elevator"]["status"] == "missing"

    amount = result["financial_source_values"][0]
    assert amount["raw_value"] == 0
    assert amount["source_mode"] == "مجانی"
    assert amount["currency"] == "unspecified"
    assert amount["unit"] == "source_dataset_unit"
    assert amount["value_status"] == "free"


def test_negotiable_mode_is_kept_when_amount_is_null():
    result = map_divar_record({
        "cat2_slug": "residential-rent",
        "rent_value": None,
        "rent_mode": "توافقی",
    })

    assert result["financial_source_values"] == [{
        "source_field": "rent_value",
        "semantic_role_hint": "monthly_rent",
        "raw_value": None,
        "source_mode": "توافقی",
        "value_status": "negotiable",
        "currency": "unspecified",
        "unit": "source_dataset_unit",
        "status": "source_label",
    }]


def test_special_day_rent_source_field_is_not_lost():
    result = map_divar_record({
        "cat2_slug": "temporary-rent",
        "rent_price_on_special_days": 2_500_000,
    })
    mention = result["financial_source_values"][0]

    assert mention["semantic_role_hint"] == "special_day_rent"
    assert mention["raw_value"] == 2_500_000


def test_original_source_labels_are_preserved_without_ad_text():
    result = map_divar_record({
        "source_row": 123,
        "cat2_slug": "residential-rent",
        "cat3_slug": "apartment-rent",
        "title": "PRIVATE AD TITLE",
        "description": "PRIVATE AD DESCRIPTION",
        "rent_to_single": 1,
    })

    assert result["source_row"] == 123
    assert result["original_dataset_labels"]["cat2_slug"] == "residential-rent"
    assert result["weak_labels"]["rental_conditions"]["allow_single_person"]["value"] is True
    assert "title" not in result
    assert "description" not in result


def test_unknown_category_is_not_guessed():
    result = map_divar_record({
        "cat2_slug": "future-category",
        "cat3_slug": "future-subcategory",
    })
    labels = result["weak_labels"]

    assert labels["transaction_type"]["value"] is None
    assert labels["transaction_type"]["status"] == "unmapped"
    assert labels["property_type"]["value"] is None
    assert labels["property_type"]["status"] == "unmapped"


def test_negative_or_non_numeric_area_is_not_mapped():
    result = map_divar_record({
        "building_size": -1,
        "land_size": "not-a-number",
    })
    labels = result["weak_labels"]

    assert labels["building_area_sqm"]["status"] == "unmapped"
    assert labels["land_area_sqm"]["status"] == "unmapped"


def test_sqlite_style_row_is_supported():
    import sqlite3

    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    con.execute("CREATE TABLE ads (cat2_slug TEXT, cat3_slug TEXT)")
    con.execute("INSERT INTO ads VALUES (?, ?)", ("residential-sell", "apartment-sell"))
    row = con.execute("SELECT * FROM ads").fetchone()

    result = map_divar_record(row)
    assert result["weak_labels"]["transaction_type"]["value"] == "sale"


def test_unselect_is_not_treated_as_a_real_value():
    result = map_divar_record({"floor": "unselect"})
    field = result["weak_labels"]["building"]["floor"]

    assert field["raw_value"] == "unselect"
    assert field["status"] == "unselected"


def test_price_value_in_services_category_has_unknown_role_hint():
    result = map_divar_record({
        "cat2_slug": "real-estate-services",
        "cat3_slug": "presell",
        "price_value": 1_000_000_000,
    })
    mention = result["financial_source_values"][0]

    assert mention["semantic_role_hint"] == "unknown"
    assert mention["currency"] == "unspecified"


def test_source_metadata_is_preserved():
    result = map_divar_record({
        "source_row": 77,
        "created_at_month": "2024-07-01 00:00:00",
        "user_type": "شخصی",
        "location_latitude": 35.7,
        "location_longitude": 51.4,
    })

    metadata = result["source_metadata"]
    assert metadata["created_at_month"] == "2024-07-01 00:00:00"
    assert metadata["user_type"] == "شخصی"
    assert metadata["location_latitude"] == 35.7
    assert metadata["location_longitude"] == 51.4



def test_fixed_mode_with_positive_amount_is_labeled_fixed_amount():
    result = map_divar_record({
        "cat2_slug": "residential-sell",
        "price_value": 2_500_000_000,
        "price_mode": "مقطوع",
    })
    item = result["financial_source_values"][0]

    assert item["value_status"] == "fixed_amount"
    assert item["raw_value"] == 2_500_000_000
    assert item["currency"] == "unspecified"


def test_free_mode_with_zero_amount_is_labeled_free_not_missing():
    result = map_divar_record({
        "cat2_slug": "residential-rent",
        "rent_value": 0,
        "rent_mode": "مجانی",
    })
    item = result["financial_source_values"][0]

    assert item["value_status"] == "free"
    assert item["raw_value"] == 0


def test_negotiable_mode_with_null_amount_is_not_a_missing_label():
    result = map_divar_record({
        "cat2_slug": "commercial-rent",
        "credit_value": None,
        "credit_mode": "توافقی",
    })
    item = result["financial_source_values"][0]

    assert item["value_status"] == "negotiable"
    assert item["raw_value"] is None


def test_conflicting_mode_and_amount_are_flagged_not_repaired():
    result = map_divar_record({
        "cat2_slug": "residential-sell",
        "price_value": 0,
        "price_mode": "مقطوع",
    })
    item = result["financial_source_values"][0]

    assert item["value_status"] == "mode_value_conflict"
    assert item["raw_value"] == 0
    assert item["source_mode"] == "مقطوع"


def test_amount_without_mode_is_preserved_without_guessing_status():
    result = map_divar_record({
        "cat2_slug": "residential-sell",
        "price_value": 3_000_000_000,
        "price_mode": None,
    })
    item = result["financial_source_values"][0]

    assert item["value_status"] == "amount_without_mode"
    assert item["raw_value"] == 3_000_000_000


def test_temporary_rent_amount_without_mode_is_only_amount_present():
    result = map_divar_record({
        "cat2_slug": "temporary-rent",
        "rent_price_on_regular_days": 1_500_000,
    })
    item = result["financial_source_values"][0]

    assert item["value_status"] == "amount_present"
    assert item["source_mode"] is None


def test_zero_temporary_rent_amount_is_not_assumed_to_mean_free():
    result = map_divar_record({
        "cat2_slug": "temporary-rent",
        "rent_price_at_weekends": 0,
    })
    item = result["financial_source_values"][0]

    assert item["value_status"] == "zero_amount"
