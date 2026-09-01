import pytest

from app.forms import InvalidNumberError, parse_float_fr, parse_int_fr, parse_optional_float_fr


def test_parse_float_fr_accepts_period_and_comma():
    assert parse_float_fr("12.5") == 12.5
    assert parse_float_fr("12,5") == 12.5
    assert parse_float_fr("  3  ") == 3.0


def test_parse_float_fr_rejects_empty_with_clear_message():
    with pytest.raises(InvalidNumberError, match="obligatoire"):
        parse_float_fr("")
    with pytest.raises(InvalidNumberError, match="obligatoire"):
        parse_float_fr("   ")


def test_parse_float_fr_rejects_garbage():
    with pytest.raises(InvalidNumberError, match="pas un nombre valide"):
        parse_float_fr("douze")


def test_parse_optional_float_fr_treats_blank_as_none():
    assert parse_optional_float_fr("") is None
    assert parse_optional_float_fr("   ") is None
    assert parse_optional_float_fr("2,5") == 2.5


def test_parse_int_fr_accepts_comma_and_truncates():
    assert parse_int_fr("7") == 7
    assert parse_int_fr("7,0") == 7


def test_parse_int_fr_rejects_garbage():
    with pytest.raises(InvalidNumberError):
        parse_int_fr("abc")
