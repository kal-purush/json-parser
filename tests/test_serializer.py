import math

import pytest

from jsonparser import JSONSerializeError, dumps, loads


def test_scalars():
    assert dumps(None) == "null"
    assert dumps(True) == "true"
    assert dumps(False) == "false"
    assert dumps(42) == "42"
    assert dumps("hi") == '"hi"'


def test_empty_containers():
    assert dumps({}) == "{}"
    assert dumps([]) == "[]"


def test_compact_object_and_array():
    assert dumps({"a": 1, "b": 2}) == '{"a": 1, "b": 2}'
    assert dumps([1, "two", True, None]) == '[1, "two", true, null]'


def test_sort_keys():
    assert dumps({"b": 1, "a": 2}, sort_keys=True) == '{"a": 2, "b": 1}'


def test_string_escaping():
    assert dumps('a"b\\c') == '"a\\"b\\\\c"'
    assert dumps("line\nbreak") == '"line\\nbreak"'
    assert dumps("\x01") == '"\\u0001"'


def test_ensure_ascii_default_escapes_unicode():
    assert dumps("caf\u00e9") == '"caf\\u00e9"'


def test_ensure_ascii_false_keeps_unicode():
    assert dumps("caf\u00e9", ensure_ascii=False) == '"caf\u00e9"'


def test_ensure_ascii_surrogate_pair():
    # U+1F600 GRINNING FACE
    assert dumps("\U0001f600") == '"\\ud83d\\ude00"'


def test_indent_pretty_print():
    out = dumps({"a": [1, 2]}, indent=2)
    assert out == '{\n  "a": [\n    1,\n    2\n  ]\n}'


def test_indent_string():
    out = dumps({"a": 1}, indent="\t")
    assert out == '{\n\t"a": 1\n}'


def test_rejects_unsupported_type():
    with pytest.raises(JSONSerializeError):
        dumps({1, 2, 3})  # a set


def test_rejects_non_string_key():
    with pytest.raises(JSONSerializeError):
        dumps({1: "a"})


def test_rejects_non_finite_float():
    with pytest.raises(JSONSerializeError):
        dumps(float("nan"))
    with pytest.raises(JSONSerializeError):
        dumps(math.inf)


def test_negative_indent_rejected():
    with pytest.raises(JSONSerializeError):
        dumps({"a": 1}, indent=-2)


@pytest.mark.parametrize(
    "value",
    [
        {},
        [],
        {"nested": {"arr": [1, 2, {"deep": [True, None, "x"]}]}},
        [1, 2.5, -3, "s", None, False],
        {"unicode": "na\u00efve caf\u00e9", "n": 0},
    ],
)
def test_round_trip(value):
    assert loads(dumps(value)) == value
    assert loads(dumps(value, indent=2)) == value