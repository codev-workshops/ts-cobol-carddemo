#!/usr/bin/env python3
"""Validate loaded data – compare row counts and checksums against source files.

Usage:
    python validate.py
"""

import sys

from etl_common import get_connection, data_path, logger

EXPECTED_COUNTS = {
    "acctdat":  ("acctdata.txt",  50),
    "carddat":  ("carddata.txt",  50),
    "cardxref": ("cardxref.txt",  50),
    "custdat":  ("custdata.txt",  50),
    "discgrp":  ("discgrp.txt",   51),
    "tcatbalf": ("tcatbal.txt",   50),
    "trancatg": ("trancatg.txt",  18),
    "trantype": ("trantype.txt",   7),
}


def count_source_lines(filename: str) -> int:
    """Count non-empty lines in a source data file."""
    path = data_path(filename)
    count = 0
    with open(path, "r") as f:
        for line in f:
            if line.strip():
                count += 1
    return count


def main():
    conn = get_connection()
    cur = conn.cursor()
    all_ok = True

    for table, (src_file, expected) in EXPECTED_COUNTS.items():
        cur.execute(f"SELECT COUNT(*) FROM {table}")  # noqa: S608
        db_count = cur.fetchone()[0]
        src_count = count_source_lines(src_file)

        status = "OK" if db_count == src_count else "MISMATCH"
        if status == "MISMATCH":
            all_ok = False

        logger.info(
            "%-10s  db=%4d  src=%4d  expected=%4d  [%s]",
            table,
            db_count,
            src_count,
            expected,
            status,
        )

    # Checksum: verify key column distinct counts
    checksums = [
        ("acctdat",  "acct_id"),
        ("carddat",  "card_num"),
        ("cardxref", "xref_card_num"),
        ("custdat",  "cust_id"),
        ("trantype", "tran_type"),
    ]
    for table, key_col in checksums:
        cur.execute(f"SELECT COUNT(DISTINCT {key_col}) FROM {table}")  # noqa: S608
        distinct = cur.fetchone()[0]
        cur.execute(f"SELECT COUNT(*) FROM {table}")  # noqa: S608
        total = cur.fetchone()[0]
        if distinct != total:
            logger.warning(
                "%s: distinct(%s)=%d != total=%d — possible duplicates",
                table,
                key_col,
                distinct,
                total,
            )
            all_ok = False

    cur.close()
    conn.close()

    if all_ok:
        logger.info("Validation PASSED – all counts match")
    else:
        logger.error("Validation FAILED – see mismatches above")
        sys.exit(1)


if __name__ == "__main__":
    main()
