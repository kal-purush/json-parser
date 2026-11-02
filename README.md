# minijson

A small, dependency-free JSON parser written from scratch in Python. It
tokenizes a JSON document and parses it into native Python values with a
hand-written recursive-descent parser. The goal is clarity and precise
error messages, not raw speed.

## Features

- Objects, arrays, strings, numbers, and the `true` / `false` / `null` literals
- String escapes including `\uXXXX` unicode escapes
- Integer and floating-point numbers, including exponents and negatives
- Errors report the line and column of the offending character
- Strict mode: trailing commas and trailing data are rejected
- Serialization back to JSON via `dumps`, with optional indentation,
  key sorting, and ASCII escaping

## Install

```bash
pip install -e ".[dev]"
```

## Usage

```python
from jsonparser import loads

loads('{"name": "ada", "ids": [1, 2, 3]}')
# {'name': 'ada', 'ids': [1, 2, 3]}
```

On malformed input it raises `JSONParseError` with position information:

```python
from jsonparser import JSONParseError, loads

try:
    loads('{"a": 1,}')
except JSONParseError as exc:
    print(exc)  # Trailing comma in object at line 1, column 9
```

## Serializing

```python
from jsonparser import dumps

dumps({"name": "ada", "ids": [1, 2, 3]})
# '{"name": "ada", "ids": [1, 2, 3]}'

print(dumps({"a": [1, 2]}, indent=2, sort_keys=True))
# {
#   "a": [
#     1,
#     2
#   ]
# }
```

## Layout

```
src/jsonparser/
    tokenizer.py   # source string -> list of tokens
    parser.py      # tokens -> Python values
    serializer.py  # Python values -> JSON string
    errors.py      # JSONParseError, JSONSerializeError
tests/
    test_tokenizer.py
    test_parser.py
    test_serializer.py
```

## Development

```bash
python -m pytest
```

## License

MIT. See [LICENSE](LICENSE).