"""Minimal example of using minijson to parse a document.

Run with:  python examples/basic_usage.py
"""

from jsonparser import JSONParseError, loads

DOCUMENT = '{"name": "ada", "active": true, "scores": [10, 9.5, null]}'


def main() -> None:
    value = loads(DOCUMENT)
    print("Parsed value:", value)
    print("name field:", value["name"])

    try:
        loads('{"broken": }')
    except JSONParseError as exc:
        print("Caught expected error:", exc)


if __name__ == "__main__":
    main()