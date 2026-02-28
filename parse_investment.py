"""
parse_investment.py
-------------------
Parse LLM-generated investment range strings into numeric (min, max) pairs.

Handles the full variety of LLM output formats without the comma-stripping bug
that concatenates thousands separators into incorrect values.

The Bug This Module Avoids
--------------------------
A naive approach strips all commas before running a regex:

    raw.replace(',', '')    # "$1,500-$2,000" -> "$1500-$2000" (works here)
                            # but "$1,500,$2,000" -> "$1500$2000" (corrupted!)

Instead this module captures each number token WITH its commas intact, then
strips the comma only from the already-captured group. This means thousands
separators are honoured correctly at every step.

Two additional regex bugs this module avoids
--------------------------------------------
Bug 1 - Separator as character class:
    [-to]+  is a CHARACTER CLASS containing '-', 't', 'o' individually.
    It would match the leading '1' in "1000" as "-t" + "o" = separator,
    then mis-read "000" as the second number.
    Fix: use a proper alternation  (?:[-]+|\bto\b)

Bug 2 - Amount pattern rejects bare 4-digit numbers:
    The pattern d{1,3}(?:,d{3})* matches "1,000" but NOT "1000" (4 bare digits).
    Fix: use  (?:d{1,3}(?:,d{3})+|d+)  — either comma-grouped or any digits.

Usage
-----
    from parse_investment import parse_investment_range

    parse_investment_range("$500-1000")          # (500.0, 1000.0)
    parse_investment_range("$1,500-$2,000")      # (1500.0, 2000.0)
    parse_investment_range("$2k-$5k")            # (2000.0, 5000.0)
    parse_investment_range("under $200")         # (None, 200.0)
    parse_investment_range("approximately $300") # (300.0, 300.0)
    parse_investment_range("free to $100")       # (0.0, 100.0)
    parse_investment_range("minimal investment") # (0.0, None)
    parse_investment_range(None)                 # (None, None)
"""

from __future__ import annotations

import re
from typing import Optional


# ---------------------------------------------------------------------------
# Number pattern — the core building block
# ---------------------------------------------------------------------------
# Two alternatives joined by |:
#   A) \d{1,3}(?:,\d{3})+   matches comma-grouped thousands: "1,500", "10,000"
#   B) \d+                   matches any plain run of digits:  "1000", "500"
# Together they cover every integer format without misreading 4-digit bare
# numbers. The (?:\.\d+)? appended handles decimals on either branch.
#
# The suffix group ([kKmM]?) captures k/K/m/M multiplier shorthand.
# Commas are stripped inside _apply_suffix(), never on the raw string.

_NUM = r"""
    (?:
        \d{1,3}(?:,\d{3})+   # comma-grouped: 1,500  10,000  1,234,567
        |
        \d+                  # plain digits:  1000   500     0
    )
    (?:\.\d+)?               # optional decimal: 2.5k  1.25m
"""

# Full currency-amount pattern: optional $, number, optional k/m suffix
_AMOUNT_PAT = r"(?:\$\s*)?(?P<digits>" + _NUM + r")\s*(?P<suffix>[kKmM])?"
_AMOUNT_RE  = re.compile(_AMOUNT_PAT, re.VERBOSE)

# Separator between two amounts in a range.
# MUST be alternation, NOT a character class, to avoid treating 't'/'o'
# as individual separator characters that consume digits from "1000".
_SEP_PAT = r"(?:\s*(?:[-\u2013\u2014]+|\bto\b)\s*)"

# Full range: AMOUNT [SEP AMOUNT]
# Written without named groups so it can be used with re.findall as well.
_RANGE_RE = re.compile(
    r"""
    (?:\$\s*)?
    (?P<n1>""" + _NUM + r""")\s*(?P<s1>[kKmM])?   # first amount
    (?:                                              # optional second amount
        """ + _SEP_PAT + r"""
        (?:\$\s*)?
        (?P<n2>""" + _NUM + r""")\s*(?P<s2>[kKmM])?
    )?
    """,
    re.VERBOSE | re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# Qualifier patterns
# ---------------------------------------------------------------------------
_UNDER_RE  = re.compile(
    r"\b(?:under|less\s+than|below|up\s+to|max(?:imum)?|at\s+most|or\s+less)\b", re.I
)
_OVER_RE   = re.compile(
    r"\b(?:over|more\s+than|above|at\s+least|from|starting(?:\s+at)?|min(?:imum)?)\b", re.I
)
_APPROX_RE = re.compile(
    r"\b(?:approx(?:imate(?:ly)?)?|about|around|roughly|circa)\b|~", re.I
)
_FREE_RE   = re.compile(r"^free$", re.I)
_FREE_TO_RE = re.compile(
    r"free\s*(?:to|-)\s*(?:\$\s*)?(" + _NUM + r")\s*([kKmM])?",
    re.VERBOSE | re.I,
)
_FREE_SIGNAL_RE = re.compile(r"\bfree\b", re.I)
_NONE_RE   = re.compile(
    r"^\s*(?:none|null|n/?a|unknown|tbd|varies|negotiable)\s*$", re.I
)
_MINIMAL_RE = re.compile(
    r"\b(?:minimal|very\s+low|low(?:\s+cost)?|small|negligible"
    r"|bootstrap(?:ped)?|no\s+(?:real\s+)?(?:upfront\s+)?invest\w*"
    r"|free\s+to\s+start)\b",
    re.I,
)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _apply_suffix(digits_with_commas: str, suffix: Optional[str]) -> float:
    """
    Convert a captured digit string and optional k/m suffix to a float.

    Commas are stripped HERE, on the already-isolated capture group,
    so they never corrupt adjacent number groups in the raw string.
    """
    value = float(digits_with_commas.replace(",", ""))
    if suffix:
        sl = suffix.lower()
        if sl == "k":
            value *= 1_000
        elif sl == "m":
            value *= 1_000_000
    return value


def _first_amount(text: str) -> Optional[float]:
    """Extract the first valid currency amount from text, or None."""
    m = _AMOUNT_RE.search(text)
    if not m:
        return None
    return _apply_suffix(m.group("digits"), m.group("suffix"))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse_investment_range(raw) -> tuple[Optional[float], Optional[float]]:
    """
    Parse an LLM-generated investment string into a (min_usd, max_usd) pair.

    Parameters
    ----------
    raw:
        The raw string from LLM output. May also be int/float (passed through
        as a point estimate), or None/""/null-like strings.

    Returns
    -------
    (min_usd, max_usd) where each element is float | None.

    Semantic conventions
    --------------------
    (None, None)  - completely unparseable / no information
    (0.0, None)   - free/minimal start, upper bound unknown
    (None, X)     - upper-bounded only ("under X")
    (X, None)     - lower-bounded only ("from X", "at least X")
    (X, X)        - single point estimate ("approximately $300", "$500")
    (X, Y) X < Y  - proper range

    Examples
    --------
    >>> parse_investment_range("$500-1000")
    (500.0, 1000.0)
    >>> parse_investment_range("$1,500-$2,000")
    (1500.0, 2000.0)
    >>> parse_investment_range("$2k-$5k")
    (2000.0, 5000.0)
    >>> parse_investment_range("under $200")
    (None, 200.0)
    >>> parse_investment_range("approximately $300")
    (300.0, 300.0)
    >>> parse_investment_range("free to $100")
    (0.0, 100.0)
    >>> parse_investment_range("minimal investment required")
    (0.0, None)
    >>> parse_investment_range(None)
    (None, None)
    """
    # --- Numeric passthrough -------------------------------------------
    if isinstance(raw, (int, float)):
        v = float(raw)
        return (v, v)

    # --- Coerce to string, normalise whitespace -------------------------
    if raw is None:
        return (None, None)

    text: str = str(raw).strip()
    if not text:
        return (None, None)

    # --- Hard no-information patterns -----------------------------------
    if _NONE_RE.match(text):
        return (None, None)

    # --- Standalone "free" ----------------------------------------------
    if _FREE_RE.match(text):
        return (0.0, 0.0)

    # --- "free to $X" or "free - $X" ------------------------------------
    m_ft = _FREE_TO_RE.search(text)
    if m_ft:
        hi = _apply_suffix(m_ft.group(1), m_ft.group(2))
        return (0.0, hi)

    # --- Soft qualitative "minimal / bootstrap / low cost" signals ------
    # Only trigger when there is NO dollar figure in the string at all,
    # so "minimal investment: $500" still parses the number.
    if _MINIMAL_RE.search(text) and not _AMOUNT_RE.search(text):
        return (0.0, None)

    # Similarly, "free to start" with no dollar figure
    if _FREE_SIGNAL_RE.search(text) and not _AMOUNT_RE.search(text):
        return (0.0, None)

    # --- Qualifier + single-amount patterns (checked before range) ------
    under_match  = _UNDER_RE.search(text)
    over_match   = _OVER_RE.search(text)
    approx_match = _APPROX_RE.search(text)

    if under_match:
        amount = _first_amount(text)
        if amount is not None:
            return (None, amount)

    if over_match:
        amount = _first_amount(text)
        if amount is not None:
            return (amount, None)

    if approx_match:
        amount = _first_amount(text)
        if amount is not None:
            return (amount, amount)

    # --- Range / single amount via full range regex ---------------------
    m = _RANGE_RE.search(text)
    if not m or not m.group("n1"):
        return (None, None)

    lo = _apply_suffix(m.group("n1"), m.group("s1"))

    n2 = m.group("n2")
    if n2 is not None:
        hi = _apply_suffix(n2, m.group("s2"))
        if lo > hi:
            lo, hi = hi, lo   # normalise reversed ranges
        return (lo, hi)

    # Single amount with no qualifier -> point estimate
    return (lo, lo)


# ---------------------------------------------------------------------------
# Self-contained unit tests
# ---------------------------------------------------------------------------

def _run_tests() -> bool:
    """Run all test cases. Returns True if all pass."""
    cases = [
        # (input, expected, description)

        # Core range formats
        ("$500-1000",          (500.0, 1000.0),       "simple dash range, second has no $"),
        ("$500 - $1000",       (500.0, 1000.0),       "dash range with spaces"),
        ("$500 to $1000",      (500.0, 1000.0),       "'to' separator"),
        ("500-1000",           (500.0, 1000.0),       "range without dollar signs"),

        # Thousands separators — the primary bug target
        ("$1,500-$2,000",      (1500.0, 2000.0),      "thousands separators on both sides"),
        ("$1,500 - $2,000",    (1500.0, 2000.0),      "thousands separators with spaces"),
        ("$10,000-$50,000",    (10000.0, 50000.0),    "large thousands-separated range"),
        ("$1,000",             (1000.0, 1000.0),      "single thousands-separated value"),
        ("$1,000,000",         (1000000.0, 1000000.0),"million with thousands separators"),

        # k/K/m/M shorthand
        ("$2k-$5k",            (2000.0, 5000.0),      "k suffix both sides"),
        ("$2K-$5K",            (2000.0, 5000.0),      "K suffix uppercase"),
        ("2.5k",               (2500.0, 2500.0),      "decimal k suffix, no $"),
        ("$1k-$1,500",         (1000.0, 1500.0),      "k suffix mixed with plain number"),
        ("$500k-$1m",          (500000.0, 1000000.0), "k and m suffix range"),
        ("$2.5M",              (2500000.0, 2500000.0),"M suffix single value"),

        # Qualifier: under / up to / less than
        ("under $200",         (None, 200.0),          "'under' keyword"),
        ("less than $500",     (None, 500.0),          "'less than' keyword"),
        ("up to $1,000",       (None, 1000.0),         "'up to' keyword"),
        ("maximum $5k",        (None, 5000.0),         "'maximum' keyword"),
        ("$500 or less",       (None, 500.0),          "'or less' — treated as under"),

        # Qualifier: over / at least / from
        ("over $1000",         (1000.0, None),         "'over' keyword"),
        ("at least $500",      (500.0, None),          "'at least' keyword"),
        ("from $200",          (200.0, None),          "'from' keyword"),
        ("starting at $300",   (300.0, None),          "'starting at' keyword"),

        # Qualifier: approximately / about / tilde
        ("approximately $300", (300.0, 300.0),         "'approximately' -> point estimate"),
        ("about $500",         (500.0, 500.0),         "'about' -> point estimate"),
        ("~$1,000",            (1000.0, 1000.0),       "tilde approximation"),
        ("roughly $750",       (750.0, 750.0),         "'roughly' -> point estimate"),

        # Free / zero cost
        ("free",               (0.0, 0.0),             "standalone 'free'"),
        ("free to $100",       (0.0, 100.0),           "'free to X' range"),
        ("free to start",      (0.0, None),            "'free to start' - no dollar amount"),

        # Minimal / low investment qualitative signals (no dollar figure)
        ("minimal investment required", (0.0, None),   "minimal investment, no amount"),
        ("minimal",                     (0.0, None),   "bare 'minimal'"),
        ("very low cost",               (0.0, None),   "'very low cost' with no amount"),
        ("bootstrapped",                (0.0, None),   "'bootstrapped' keyword"),
        ("no upfront investment needed",(0.0, None),   "'no investment' phrasing"),

        # LLM failure / null / empty
        (None,                 (None, None),            "None input"),
        ("",                   (None, None),            "empty string"),
        ("None",               (None, None),            "string 'None'"),
        ("null",               (None, None),            "string 'null'"),
        ("N/A",                (None, None),            "N/A"),
        ("TBD",                (None, None),            "TBD"),
        ("varies",             (None, None),            "'varies'"),

        # Numeric passthrough
        (500,                  (500.0, 500.0),          "integer passthrough"),
        (1500.0,               (1500.0, 1500.0),        "float passthrough"),

        # Edge cases
        ("$0",                 (0.0, 0.0),              "explicit zero"),
        ("$500-$200",          (200.0, 500.0),          "reversed range - normalised"),
    ]

    passed = 0
    failed = 0

    for raw, expected, description in cases:
        result = parse_investment_range(raw)
        ok = (result == expected)
        status = "PASS" if ok else "FAIL"
        if not ok:
            failed += 1
            print(f"  [{status}] {description}")
            print(f"         input:    {raw!r}")
            print(f"         expected: {expected}")
            print(f"         got:      {result}")
        else:
            passed += 1
            print(f"  [{status}] {description}")

    total = passed + failed
    print(f"\n{passed}/{total} tests passed", end="")
    if failed:
        print(f"  ({failed} FAILED)")
    else:
        print(" -- all green.")
    return failed == 0


if __name__ == "__main__":
    import sys
    ok = _run_tests()
    sys.exit(0 if ok else 1)
