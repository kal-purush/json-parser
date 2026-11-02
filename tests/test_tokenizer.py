import pytest

from jsonparser.errors import JSONParseError
from jsonparser.tokenizer import (
    EOF,
    NUMBER,
    STRING,
    TRUE,
    tokenize,
)


def kinds(text):
    return [t.kind for t in tokenize(text)]


def test_punctuation_sequence():
    assert kinds("{}[]:,") == [
        "LBRACE",
        "RBRACE",
        "LBRACKET",
        "RBRACKET",
        "COLON",
        "COMMA",
        EOF,
    ]


def test_whitespace_is_skipped():
    assert kinds("  \n\t [ ] ") == ["LBRACKET", "RBRACKET", EOF]


def test_string_value():
    toks = tokenize('"hello"')
    assert toks[0].kind == STRING
    assert toks[0].value == "hello"


def test_string_escapes():
    toks = tokenize(r'"a\n\t\"b\\"')
    assert toks[0].value == 'a\n\t"b\\'


def test_unicode_escape():
    toks = tokenize(r'"é"')
    assert toks[0].value == "é"


def test_integer_and_float():
    assert tokenize("42")[0].value == 42
    assert tokenize("3.14")[0].value == 3.14


def test_negative_and_exponent():
    assert tokenize("-7")[0].value == -7
    assert tokenize("1e3")[0].value == 1000.0
    assert tokenize("2.5E-2")[0].value == 0.025


def test_literals():
    assert tokenize("true")[0].kind == TRUE
    assert tokenize("false")[0].value is False
    assert tokenize("null")[0].value is None


def test_token_positions_track_lines():
    toks = tokenize('{\n  "k": 1\n}')
    string_tok = [t for t in toks if t.kind == STRING][0]
    assert string_tok.line == 2


def test_unterminated_string_raises():
    with pytest.raises(JSONParseError):
        tokenize('"no end')


def test_unknown_literal_raises():
    with pytest.raises(JSONParseError):
        tokenize("nul")


def test_unexpected_character_raises():
    with pytest.raises(JSONParseError):
        tokenize("@")
