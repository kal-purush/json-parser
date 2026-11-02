"""minijson: a small, dependency-free JSON parser and serializer.

Public API:
    loads(text) -> Python value
    dumps(value, ...) -> JSON string
    JSONParseError
    JSONSerializeError
"""

from .errors import JSONParseError
from .parser import loads
from .serializer import JSONSerializeError, dumps

__all__ = ["loads", "dumps", "JSONParseError", "JSONSerializeError"]
__version__ = "0.2.0"