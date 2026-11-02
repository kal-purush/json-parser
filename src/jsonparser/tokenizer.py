"""A small hand-written tokenizer for JSON.

Turns a source string into a flat list of tokens. Each token records
its source position so the parser can produce useful error messages.
"""

from dataclasses import dataclass
from typing import Any, List

from .errors import JSONParseError

# Token kinds
LBRACE = "LBRACE"
RBRACE = "RBRACE"
LBRACKET = "LBRACKET"
RBRACKET = "RBRACKET"
COLON = "COLON"
COMMA = "COMMA"
STRING = "STRING"
NUMBER = "NUMBER"
TRUE = "TRUE"
FALSE = "FALSE"
NULL = "NULL"
EOF = "EOF"

_PUNCT = {
    "{": LBRACE,
    "}": RBRACE,
    "[": LBRACKET,
    "]": RBRACKET,
    ":": COLON,
    ",": COMMA,
}

_WHITESPACE = " \t\n\r"

_ESCAPES = {
    '"': '"',
    "\\": "\\",
    "/": "/",
    "b": "\b",
    "f": "\f",
    "n": "\n",
    "r": "\r",
    "t": "\t",
}


@dataclass
class Token:
    kind: str
    value: Any
    pos: int
    line: int
    col: int


class Tokenizer:
    def __init__(self, text: str):
        self.text = text
        self.i = 0
        self.line = 1
        self.col = 1

    def _advance(self) -> str:
        ch = self.text[self.i]
        self.i += 1
        if ch == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def _error(self, message: str) -> JSONParseError:
        return JSONParseError(message, pos=self.i, line=self.line, col=self.col)

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []
        while self.i < len(self.text):
            ch = self.text[self.i]
            if ch in _WHITESPACE:
                self._advance()
                continue
            start_pos, start_line, start_col = self.i, self.line, self.col
            if ch in _PUNCT:
                self._advance()
                tokens.append(Token(_PUNCT[ch], ch, start_pos, start_line, start_col))
            elif ch == '"':
                value = self._read_string()
                tokens.append(Token(STRING, value, start_pos, start_line, start_col))
            elif ch == "-" or ch.isdigit():
                value = self._read_number()
                tokens.append(Token(NUMBER, value, start_pos, start_line, start_col))
            elif ch.isalpha():
                kind, value = self._read_literal()
                tokens.append(Token(kind, value, start_pos, start_line, start_col))
            else:
                raise self._error(f"Unexpected character {ch!r}")
        tokens.append(Token(EOF, None, self.i, self.line, self.col))
        return tokens

    def _read_string(self) -> str:
        self._advance()  # opening quote
        chars: List[str] = []
        while True:
            if self.i >= len(self.text):
                raise self._error("Unterminated string")
            ch = self._advance()
            if ch == '"':
                return "".join(chars)
            if ch == "\\":
                chars.append(self._read_escape())
            elif ord(ch) < 0x20:
                raise self._error("Control character in string")
            else:
                chars.append(ch)

    def _read_escape(self) -> str:
        if self.i >= len(self.text):
            raise self._error("Unterminated escape sequence")
        esc = self._advance()
        if esc in _ESCAPES:
            return _ESCAPES[esc]
        if esc == "u":
            return self._read_unicode_escape()
        raise self._error(f"Invalid escape sequence \\{esc}")

    def _read_unicode_escape(self) -> str:
        if self.i + 4 > len(self.text):
            raise self._error("Incomplete unicode escape")
        hex_digits = self.text[self.i : self.i + 4]
        try:
            code = int(hex_digits, 16)
        except ValueError:
            raise self._error(f"Invalid unicode escape \\u{hex_digits}")
        for _ in range(4):
            self._advance()
        return chr(code)

    def _read_number(self) -> Any:
        start = self.i
        if self.text[self.i] == "-":
            self._advance()
        self._read_digits()
        is_float = False
        if self.i < len(self.text) and self.text[self.i] == ".":
            is_float = True
            self._advance()
            self._read_digits(required=True)
        if self.i < len(self.text) and self.text[self.i] in "eE":
            is_float = True
            self._advance()
            if self.i < len(self.text) and self.text[self.i] in "+-":
                self._advance()
            self._read_digits(required=True)
        raw = self.text[start : self.i]
        return float(raw) if is_float else int(raw)

    def _read_digits(self, required: bool = False) -> None:
        seen = False
        while self.i < len(self.text) and self.text[self.i].isdigit():
            self._advance()
            seen = True
        if required and not seen:
            raise self._error("Expected digit")

    def _read_literal(self):
        start = self.i
        while self.i < len(self.text) and self.text[self.i].isalpha():
            self._advance()
        word = self.text[start : self.i]
        if word == "true":
            return TRUE, True
        if word == "false":
            return FALSE, False
        if word == "null":
            return NULL, None
        raise JSONParseError(
            f"Unknown literal {word!r}", pos=start, line=self.line, col=self.col
        )


def tokenize(text: str) -> List[Token]:
    return Tokenizer(text).tokenize()
