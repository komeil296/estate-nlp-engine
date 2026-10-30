"""Deterministic Persian text normalization."""

import re
import unicodedata


CHAR_TRANSLATION = str.maketrans({
    "\u064a": "\u06cc",  # Arabic Yeh -> Persian Yeh
    "\u0649": "\u06cc",  # Alef Maksura -> Persian Yeh
    "\u0643": "\u06a9",  # Arabic Kaf -> Persian Kaf
    "\u0640": None,      # Tatweel
})

DIGIT_TRANSLATION = str.maketrans(
    "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩",
    "01234567890123456789"
)

ARABIC_DIACRITICS = re.compile(r"[\u064b-\u0652\u0670]")

BIDI_CONTROLS = re.compile(
    r"[\u200e\u200f\u202a-\u202e\u2066-\u2069]"
)

ZWNJ_SPACING = re.compile(r"[ \t]*\u200c[ \t]*")

HORIZONTAL_WHITESPACE = re.compile(r"[^\S\n]+")

NEWLINE_SPACING = re.compile(r" *\n *")

MULTIPLE_NEWLINES = re.compile(r"\n{3,}")

MULTIPLE_ZWNJ = re.compile(r"\u200c{2,}")


def normalize_persian_text(text: str) -> str:
    """
    Normalize Persian text without changing its semantic meaning.

    The original input must be stored separately by the caller.

    This function does not:
    - Insert missing half-spaces.
    - Parse prices or areas.
    - Convert Rial to Toman.
    - Remove punctuation.
    - Perform spelling correction.
    """

    if not isinstance(text, str):
        raise TypeError("text must be a string")

    text = unicodedata.normalize("NFC", text)

    text = text.translate(CHAR_TRANSLATION)
    text = text.translate(DIGIT_TRANSLATION)

    text = BIDI_CONTROLS.sub("", text)
    text = ARABIC_DIACRITICS.sub("", text)

    text = text.replace("\r\n", "\n").replace("\r", "\n")

    text = ZWNJ_SPACING.sub("\u200c", text)
    text = MULTIPLE_ZWNJ.sub("\u200c", text)

    text = HORIZONTAL_WHITESPACE.sub(" ", text)
    text = NEWLINE_SPACING.sub("\n", text)
    text = MULTIPLE_NEWLINES.sub("\n\n", text)

    return text.strip()