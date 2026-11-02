"""Error types for the JSON parser."""


class JSONParseError(Exception):
    """Raised when input cannot be parsed as JSON.

    Carries the byte offset plus line and column of the offending
    character so callers can point at the problem.
    """

    def __init__(self, message, pos=None, line=None, col=None):
        self.message = message
        self.pos = pos
        self.line = line
        self.col = col
        location = ""
        if line is not None and col is not None:
            location = f" at line {line}, column {col}"
        super().__init__(f"{message}{location}")
