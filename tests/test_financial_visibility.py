from decimal import Decimal

from estate_nlp.financial_visibility import inspect_amount_visibility


def test_exact_raw_amount_is_detected():
    result = inspect_amount_visibility(
        "قیمت ۲۰۰,۰۰۰,۰۰۰ تومان",
        Decimal("200000000"),
        "asking_price",
    )

    assert result["has_number"] is True
    assert result["has_money_marker"] is True
    assert result["has_target_role_cue"] is True
    assert result["exact_raw_number"] is True
    assert result["exact_scaled_expression"] is False


def test_explicit_million_expression_is_detected():
    result = inspect_amount_visibility(
        "قیمت ۲۰۰ میلیون تومان",
        Decimal("200000000"),
        "asking_price",
    )

    assert result["exact_scaled_expression"] is True
    assert result["has_target_role_cue"] is True


def test_short_million_abbreviation_is_detected():
    result = inspect_amount_visibility(
        "رهن ۲۰۰ م",
        Decimal("200000000"),
        "deposit",
    )

    assert result["exact_scaled_expression"] is True


def test_possible_scale_factor_is_diagnostic_only():
    result = inspect_amount_visibility(
        "قیمت ۲۰۰۰",
        Decimal("2000000000"),
        "asking_price",
    )

    assert result["possible_scale_factor_only"] is True
    assert result["exact_raw_number"] is False
    assert result["exact_scaled_expression"] is False


def test_numeric_measurement_is_not_assumed_to_be_money():
    result = inspect_amount_visibility(
        "آپارتمان ۸۵ متر",
        Decimal("85"),
        "asking_price",
    )

    assert result["exact_raw_number"] is True
    assert result["has_money_marker"] is False
    assert result["has_target_role_cue"] is False


def test_no_number_returns_no_visibility_match():
    result = inspect_amount_visibility(
        "آپارتمان خوش نقشه دارای پارکینگ",
        Decimal("200000000"),
        "asking_price",
    )

    assert result["has_number"] is False
    assert result["exact_raw_number"] is False
    assert result["exact_scaled_expression"] is False
    assert result["possible_scale_factor_only"] is False


def test_persian_half_space_and_currency_normalize():
    result = inspect_amount_visibility(
        "ودیعه: ۱۵۰‌ میلیون تومان",
        Decimal("150000000"),
        "deposit",
    )

    assert result["exact_scaled_expression"] is True
    assert result["has_money_marker"] is True
    assert result["has_target_role_cue"] is True
