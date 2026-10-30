import pytest

from estate_nlp import normalize_persian_text


def test_arabic_letters_are_normalized():
    assert normalize_persian_text("ي ك ى") == "ی ک ی"


def test_persian_and_arabic_digits_are_normalized():
    assert normalize_persian_text("۱۲۳٤٥٦٧٨٩٠") == "1234567890"


def test_punctuation_is_preserved():
    text = "قیمت: ۱۲,۵۰۰,۰۰۰ تومان؛ رهن ۳۰۰ میلیون"

    expected = "قیمت: 12,500,000 تومان؛ رهن 300 میلیون"

    assert normalize_persian_text(text) == expected


def test_tatweel_is_removed():
    assert normalize_persian_text("آپاــــرتمان") == "آپارتمان"


def test_arabic_diacritics_are_removed():
    assert normalize_persian_text("مُسکِن") == "مسکن"


def test_spaces_around_zwnj_are_removed():
    assert normalize_persian_text("می‌ رود") == "می‌رود"
    assert normalize_persian_text("می ‌رود") == "می‌رود"


def test_missing_zwnj_is_not_invented():
    assert normalize_persian_text("می رود") == "می رود"


def test_whitespace_is_normalized():
    text = "  آپارتمان\t ۸۵ متر \r\n\r\n پارکینگ "

    expected = "آپارتمان 85 متر\n\nپارکینگ"

    assert normalize_persian_text(text) == expected


def test_bidi_controls_are_removed():
    text = "\u200fآپارتمان\u200e"

    assert normalize_persian_text(text) == "آپارتمان"


def test_empty_string():
    assert normalize_persian_text("") == ""


def test_non_string_input_is_rejected():
    with pytest.raises(TypeError):
        normalize_persian_text(None)


def test_normalization_is_idempotent():
    text = "ي ك آپارتمان ۸۵ متر، دارای پارکینگ"

    first = normalize_persian_text(text)
    second = normalize_persian_text(first)

    assert first == second