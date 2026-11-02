"""minijson: a small, dependency-free JSON parser.

Public API:
    loads(text) -> Python value
    JSONParseError
"""

from .errors import JSONParseError
from .parser import loads

__all__ = ["loads", "JSONParseError"]
__version__ = "0.1.0"
