# Copilot instructions for minijson

This repository is a small, dependency-free JSON parser written from
scratch in Python. It is organized as a tokenizer (`tokenizer.py`), a
recursive-descent parser (`parser.py`), and an error type (`errors.py`).

When reviewing code:

- Focus on parsing correctness and edge-case handling: empty input,
  deep nesting, string escapes including `\uXXXX`, numeric forms
  (integers, floats, exponents, negatives), and malformed input.
- Prefer that errors raise `JSONParseError` with line and column
  information rather than bare or generic exceptions.
- Keep the public API small: `loads()` and `JSONParseError`.
- The library must stay dependency-free; flag any new third-party
  runtime dependency.
- Point out missing tests for new behavior and unclear docstrings on
  public functions.

Keep review comments concise and actionable.
