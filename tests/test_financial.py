import pytest
from jsonschema import validate
import json
from pathlib import Path

from estate_nlp.extractor import extract_text


ROOT = Path(__file__).resolve().parents[1]

SCHEMA = json.loads(
    (ROOT / "schemas" / "extraction.schema.json").read_text(
        encoding="utf-8"
    )
)


def mentions(text):
    return extract_text(text).financial_mentions


def test_sale_price_in_billion_toman():
    result = mentions(
        "فروش آپارتمان با قیمت ۸ میلیارد تومان"
    )

    assert len(result) == 1

    item = result[0]

    assert item.semantic_role == "asking_price"
    assert item.normalized_value == 8_000_000_000
    assert item.currency == "toman"
    assert item.period == "one_time"


def test_deposit_and_monthly_rent_are_separated():
    result = mentions(
        "رهن ۵۰۰ میلیون تومان و اجاره ماهانه ۲۰ میلیون تومان"
    )

    assert len(result) == 2

    assert result[0].semantic_role == "deposit"
    assert result[0].normalized_value == 500_000_000

    assert result[1].semantic_role == "monthly_rent"
    assert result[1].normalized_value == 20_000_000
    assert result[1].period == "month"


def test_daily_rent():
    result = mentions(
        "اجاره روزانه ۲ میلیون تومان"
    )

    assert len(result) == 1

    assert result[0].semantic_role == "daily_rent"
    assert result[0].normalized_value == 2_000_000
    assert result[0].period == "day"


def test_weekend_rent():
    result = mentions(
        "اجاره آخر هفته ۵ میلیون تومان"
    )

    assert len(result) == 1

    assert result[0].semantic_role == "weekend_rent"
    assert result[0].normalized_value == 5_000_000


def test_price_per_square_meter():
    result = mentions(
        "قیمت هر متر ۱۰۰ میلیون تومان"
    )

    assert len(result) == 1

    assert result[0].semantic_role == "price_per_sqm"
    assert result[0].normalized_value == 100_000_000


def test_budget_extraction():
    result = mentions(
        "بودجه تا سقف ۳ میلیارد تومان"
    )

    assert len(result) == 1

    assert result[0].semantic_role == "budget"
    assert result[0].normalized_value == 3_000_000_000


def test_extra_person_cost():
    result = mentions(
        "هزینه هر نفر اضافه ۵۰۰ هزار تومان"
    )

    assert len(result) == 1

    assert result[0].semantic_role == "cost_per_extra_person"
    assert result[0].normalized_value == 500_000


def test_rial_is_not_converted_to_toman():
    result = mentions(
        "قیمت ۲۰۰۰۰۰ ریال"
    )

    assert len(result) == 1

    assert result[0].normalized_value == 200_000
    assert result[0].currency == "rial"


def test_unspecified_currency_is_not_guessed():
    result = mentions(
        "قیمت ۲ میلیارد"
    )

    assert len(result) == 1

    assert result[0].normalized_value == 2_000_000_000
    assert result[0].currency == "unspecified"


def test_decimal_scale_is_supported():
    result = mentions(
        "قیمت ۱.۵ میلیارد تومان"
    )

    assert len(result) == 1

    assert result[0].normalized_value == 1_500_000_000


def test_grouped_numbers_are_supported():
    result = mentions(
        "قیمت ۱,۵۰۰,۰۰۰ تومان"
    )

    assert len(result) == 1

    assert result[0].normalized_value == 1_500_000


def test_currency_prefix_is_supported():
    result = mentions(
        "قیمت تومان ۵۰۰ میلیون"
    )

    assert len(result) == 1

    assert result[0].currency == "toman"
    assert result[0].normalized_value == 500_000_000


def test_area_rooms_and_year_are_not_financial_mentions():
    result = mentions(
        "فروش آپارتمان ۸۵ متر، دو خواب، ساخت ۱۳۹۸"
    )

    assert result == ()


def test_area_is_not_extracted_as_rent():
    result = mentions(
        "اجاره آپارتمان ۸۵ متر"
    )

    assert result == ()


def test_multiple_amounts_are_preserved():
    result = mentions(
        "رهن ۳۰۰ میلیون و اجاره ۱۵ میلیون"
    )

    assert len(result) == 2

    assert [item.normalized_value for item in result] == [
        300_000_000,
        15_000_000,
    ]


def test_financial_evidence_is_preserved():
    result = mentions(
        "رهن ۵۰۰ میلیون تومان"
    )

    assert len(result) == 1

    assert result[0].raw_value
    assert result[0].evidence
    assert "رهن" in result[0].evidence


def test_extraction_output_matches_json_schema():
    result = extract_text(
        "فروش آپارتمان ۸۵ متری، قیمت ۸ میلیارد تومان"
    )

    validate(
        instance=result.to_dict(),
        schema=SCHEMA,
    )


def test_non_string_input_is_rejected():
    with pytest.raises(TypeError):
        from estate_nlp.financial import extract_financial_mentions
        extract_financial_mentions(None)


def test_special_day_rent_has_distinct_role():
    result = mentions("اجاره ایام خاص ۵ میلیون تومان")

    assert len(result) == 1
    assert result[0].semantic_role == "special_day_rent"
    assert result[0].normalized_value == 5_000_000


def test_deposit_synonyms_include_sepadde_and_pish():
    result = mentions(
        "سپرده ۱۰۰ میلیون تومان؛ پیش پرداخت ۵۰ میلیون تومان"
    )

    assert [item.semantic_role for item in result] == [
        "deposit",
        "deposit",
    ]


def test_monthly_rent_synonyms_include_keraye_and_mahi():
    result = mentions(
        "کرایه ۱۶ میلیون تومان؛ ماهی ۱۵ میلیون تومان"
    )

    assert [item.semantic_role for item in result] == [
        "monthly_rent",
        "monthly_rent",
    ]


def test_contextual_m_abbreviation_means_million():
    result = mentions("پیش ۱۰۰ م و ماهی ۱۵ م")

    assert [item.semantic_role for item in result] == [
        "deposit",
        "monthly_rent",
    ]
    assert [item.normalized_value for item in result] == [
        100_000_000,
        15_000_000,
    ]


def test_plaque_number_is_not_extracted_as_asking_price():
    result = mentions("فروش مغازه با پلاک ۲۲۱۶")

    assert result == ()


def test_special_day_is_not_merged_with_weekend_role():
    result = mentions("اجاره آخر هفته ۵ میلیون تومان")

    assert len(result) == 1
    assert result[0].semantic_role == "weekend_rent"


def test_short_m_is_not_a_money_scale_without_financial_context():
    result = mentions("زمین ۱۰۰ م")

    assert result == ()


def test_special_day_rent_output_validates_against_schema():
    from jsonschema import validate

    result = extract_text("اجاره ایام خاص ۵ میلیون تومان")

    validate(instance=result.to_dict(), schema=SCHEMA)
