import pytest

from jsonparser import JSONParseError, loads


def test_empty_object_and_array():
    assert loads("{}") == {}
    assert loads("[]") == []


def test_flat_object():
    assert loads('{"a": 1, "b": "two", "c": true}') == {
        "a": 1,
        "b": "two",
        "c": True,
    }


def test_flat_array():
    assert loads("[1, 2.5, false, null]") == [1, 2.5, False, None]


def test_nested_structure():
    doc = '{"users": [{"id": 1, "tags": ["x", "y"]}, {"id": 2, "tags": []}]}'
    assert loads(doc) == {
        "users": [
            {"id": 1, "tags": ["x", "y"]},
            {"id": 2, "tags": []},
        ]
    }


def test_scalar_at_top_level():
    assert loads("42") == 42
    assert loads('"bare"') == "bare"
    assert loads("null") is None


def test_deeply_nested_arrays():
    assert loads("[[[[[1]]]]]") == [[[[[1]]]]]


def test_whitespace_tolerated():
    assert loads('\n  {\n  "k" :\t[ 1 , 2 ]\n}\n') == {"k": [1, 2]}


def test_unicode_in_keys_and_values():
    assert loads(r'{"naïve": "café"}') == {"naïve": "café"}


def test_trailing_comma_object_rejected():
    with pytest.raises(JSONParseError):
        loads('{"a": 1,}')


def test_trailing_comma_array_rejected():
    with pytest.raises(JSONParseError):
        loads("[1, 2,]")


def test_trailing_data_rejected():
    with pytest.raises(JSONParseError):
        loads("{} {}")


def test_missing_colon_rejected():
    with pytest.raises(JSONParseError):
        loads('{"a" 1}')


def test_unquoted_key_rejected():
    with pytest.raises(JSONParseError):
        loads("{a: 1}")


def test_non_string_input_rejected():
    with pytest.raises(TypeError):
        loads(b"{}")  # bytes, not str


def test_error_carries_location():
    try:
        loads('{\n  "a": }')
    except JSONParseError as exc:
        assert exc.line == 2
    else:
        pytest.fail("expected JSONParseError")
