"""Recursive-descent parser that turns JSON tokens into Python values."""

from typing import Any, List

from .errors import JSONParseError
from .tokenizer import (
    COLON,
    COMMA,
    EOF,
    FALSE,
    LBRACE,
    LBRACKET,
    NULL,
    NUMBER,
    RBRACE,
    RBRACKET,
    STRING,
    TRUE,
    Token,
    tokenize,
)

_VALUE_START = {STRING, NUMBER, TRUE, FALSE, NULL, LBRACE, LBRACKET}


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    @property
    def current(self) -> Token:
        return self.tokens[self.pos]

    def _advance(self) -> Token:
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def _error(self, message: str, tok: Token) -> JSONParseError:
        return JSONParseError(message, pos=tok.pos, line=tok.line, col=tok.col)

    def _expect(self, kind: str) -> Token:
        tok = self.current
        if tok.kind != kind:
            raise self._error(f"Expected {kind} but found {tok.kind}", tok)
        return self._advance()

    def parse(self) -> Any:
        value = self._parse_value()
        if self.current.kind != EOF:
            raise self._error("Trailing data after JSON value", self.current)
        return value

    def _parse_value(self) -> Any:
        tok = self.current
        if tok.kind == LBRACE:
            return self._parse_object()
        if tok.kind == LBRACKET:
            return self._parse_array()
        if tok.kind in (STRING, NUMBER, TRUE, FALSE, NULL):
            return self._advance().value
        raise self._error(f"Unexpected token {tok.kind}", tok)

    def _parse_object(self) -> dict:
        self._expect(LBRACE)
        obj: dict = {}
        if self.current.kind == RBRACE:
            self._advance()
            return obj
        while True:
            key_tok = self._expect(STRING)
            self._expect(COLON)
            obj[key_tok.value] = self._parse_value()
            nxt = self.current
            if nxt.kind == COMMA:
                self._advance()
                if self.current.kind == RBRACE:
                    raise self._error("Trailing comma in object", self.current)
                continue
            if nxt.kind == RBRACE:
                self._advance()
                return obj
            raise self._error("Expected ',' or '}' in object", nxt)

    def _parse_array(self) -> list:
        self._expect(LBRACKET)
        arr: list = []
        if self.current.kind == RBRACKET:
            self._advance()
            return arr
        while True:
            arr.append(self._parse_value())
            nxt = self.current
            if nxt.kind == COMMA:
                self._advance()
                if self.current.kind == RBRACKET:
                    raise self._error("Trailing comma in array", self.current)
                continue
            if nxt.kind == RBRACKET:
                self._advance()
                return arr
            raise self._error("Expected ',' or ']' in array", nxt)


def loads(text: str) -> Any:
    """Parse a JSON document from a string into Python values."""
    if not isinstance(text, str):
        raise TypeError("loads() expects a string")
    tokens = tokenize(text)
    return Parser(tokens).parse()
