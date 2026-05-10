"""Shared utilities for CardDemo seed data ETL scripts."""

import os
import logging
import psycopg2

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
)
logger = logging.getLogger("carddemo_etl")


def get_connection():
    """Return a psycopg2 connection using environment variables."""
    return psycopg2.connect(
        host=os.environ.get("PGHOST", "localhost"),
        port=int(os.environ.get("PGPORT", 5432)),
        dbname=os.environ.get("PGDATABASE", "carddemo"),
        user=os.environ.get("PGUSER", "carddemo_admin"),
        password=os.environ.get("PGPASSWORD", ""),
    )


def parse_numeric(raw: str, decimal_places: int = 0) -> str:
    """Parse a COBOL zoned-decimal / unsigned numeric string.

    Handles the trailing overpunch sign characters used in COBOL
    PIC S9(n)V99 fields stored in zoned-decimal (DISPLAY) format.
    The last byte of a signed field uses a letter to encode both the
    digit and the sign.

    Returns a string suitable for NUMERIC column insertion.
    """
    raw = raw.strip()
    if not raw:
        return "0"

    sign = ""
    overpunch_pos = {
        "{": ("0", "+"), "A": ("1", "+"), "B": ("2", "+"), "C": ("3", "+"),
        "D": ("4", "+"), "E": ("5", "+"), "F": ("6", "+"), "G": ("7", "+"),
        "H": ("8", "+"), "I": ("9", "+"),
        "}": ("0", "-"), "J": ("1", "-"), "K": ("2", "-"), "L": ("3", "-"),
        "M": ("4", "-"), "N": ("5", "-"), "O": ("6", "-"), "P": ("7", "-"),
        "Q": ("8", "-"), "R": ("9", "-"),
    }

    last_char = raw[-1]
    if last_char in overpunch_pos:
        digit, sign = overpunch_pos[last_char]
        raw = raw[:-1] + digit

    raw = raw.lstrip("0") or "0"

    if decimal_places > 0:
        if len(raw) <= decimal_places:
            raw = raw.zfill(decimal_places + 1)
        integer_part = raw[:-decimal_places]
        decimal_part = raw[-decimal_places:]
        result = f"{integer_part}.{decimal_part}"
    else:
        result = raw

    if sign == "-":
        result = "-" + result

    return result


def data_path(filename: str) -> str:
    """Resolve a seed data file path relative to the repo root."""
    repo_root = os.environ.get(
        "CARDDEMO_REPO_ROOT",
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")),
    )
    return os.path.join(repo_root, "app", "data", "ASCII", filename)
