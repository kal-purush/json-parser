"""Serialize Python values into JSON text.

This is the inverse of :func:`jsonparser.loads`. It walks a Python value
and produces a JSON string, with optional pretty-printing, key sorting,
and ASCII escaping. It is deliberately strict about what it accepts:
only the JSON data model (dict, list, str, int, float, bool, None) is
supported, and anything else raises :class:`JSONSerializeError`.
"""

import math
from typing import Any, List

from .errors import JSONParseError


class JSONSerializeError(JSONParseError):
    """Raised when a Python value cannot be represented as JSON."""


_ESCAPE_MAP = {
    '"': '\\"',
    "\\": "\\\\",
    "\b": "\\b",
    "\f": "\\f",
    "\n": "\\n",
    "\r": "\\r",
    "\t": "\\t",
}


def _escape_string(s: str, ensure_ascii: bool) -> str:
    out: List[str] = ['"']
    for ch in s:
        if ch in _ESCAPE_MAP:
            out.append(_ESCAPE_MAP[ch])
        elif ord(ch) < 0x20:
            out.append(f"\\u{ord(ch):04x}")
        elif ensure_ascii and ord(ch) > 0x7E:
            code = ord(ch)
            if code > 0xFFFF:
                # Encode as a UTF-16 surrogate pair.
                code -= 0x10000
                high = 0xD800 + (code >> 10)
                low = 0xDC00 + (code & 0x3FF)
                out.append(f"\\u{high:04x}\\u{low:04x}")
            else:
                out.append(f"\\u{code:04x}")
        else:
            out.append(ch)
    out.append('"')
    return "".join(out)


def _format_number(value: Any) -> str:
    if isinstance(value, bool):
        # bool is a subclass of int; handle it before int.
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            raise JSONSerializeError(f"Cannot serialize non-finite float {value!r}")
        return repr(value)
    raise JSONSerializeError(f"Unsupported number type {type(value).__name__}")


class _Serializer:
    def __init__(self, indent, sort_keys, ensure_ascii):
        self.sort_keys = sort_keys
        self.ensure_ascii = ensure_ascii
        if indent is None:
            self.newline = ""
            self.indent_unit = ""
            self.item_sep = ", "
            self.kv_sep = ": "
        else:
            if isinstance(indent, int):
                if indent < 0:
                    raise JSONSerializeError("indent must be non-negative")
                indent = " " * indent
            self.newline = "\n"
            self.indent_unit = indent
            self.item_sep = ","
            self.kv_sep = ": "

    def serialize(self, value: Any) -> str:
        parts: List[str] = []
        self._write(value, 0, parts)
        return "".join(parts)

    def _pad(self, depth: int) -> str:
        return self.indent_unit * depth

    def _write(self, value: Any, depth: int, parts: List[str]) -> None:
        if value is None:
            parts.append("null")
        elif isinstance(value, str):
            parts.append(_escape_string(value, self.ensure_ascii))
        elif isinstance(value, bool) or isinstance(value, (int, float)):
            parts.append(_format_number(value))
        elif isinstance(value, dict):
            self._write_object(value, depth, parts)
        elif isinstance(value, (list, tuple)):
            self._write_array(value, depth, parts)
        else:
            raise JSONSerializeError(
                f"Object of type {type(value).__name__} is not JSON serializable"
            )

    def _write_object(self, obj: dict, depth: int, parts: List[str]) -> None:
        if not obj:
            parts.append("{}")
            return
        items = obj.items()
        if self.sort_keys:
            items = sorted(items, key=lambda kv: kv[0])
        parts.append("{")
        parts.append(self.newline)
        inner = depth + 1
        last = len(obj) - 1
        for idx, (key, val) in enumerate(items):
            if not isinstance(key, str):
                raise JSONSerializeError(
                    f"Object keys must be strings, got {type(key).__name__}"
                )
            parts.append(self._pad(inner))
            parts.append(_escape_string(key, self.ensure_ascii))
            parts.append(self.kv_sep)
            self._write(val, inner, parts)
            if idx != last:
                parts.append(self.item_sep)
            parts.append(self.newline)
        parts.append(self._pad(depth))
        parts.append("}")

    def _write_array(self, arr, depth: int, parts: List[str]) -> None:
        if not arr:
            parts.append("[]")
            return
        parts.append("[")
        parts.append(self.newline)
        inner = depth + 1
        last = len(arr) - 1
        for idx, val in enumerate(arr):
            parts.append(self._pad(inner))
            self._write(val, inner, parts)
            if idx != last:
                parts.append(self.item_sep)
            parts.append(self.newline)
        parts.append(self._pad(depth))
        parts.append("]")


def dumps(value: Any, *, indent=None, sort_keys: bool = False,
          ensure_ascii: bool = True) -> str:
    """Serialize ``value`` to a JSON-formatted string.

    Args:
        value: A Python value made of dict, list, str, int, float, bool, None.
        indent: If None, produce compact output on one line. If an int or a
            string, pretty-print with that indentation per level.
        sort_keys: If True, object keys are emitted in sorted order.
        ensure_ascii: If True, escape all non-ASCII characters as ``\\uXXXX``.

    Returns:
        The JSON text.

    Raises:
        JSONSerializeError: If the value contains an unsupported type, a
            non-string object key, or a non-finite float.
    """
    return _Serializer(indent, sort_keys, ensure_ascii).serialize(value)