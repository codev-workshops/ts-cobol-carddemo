#!/usr/bin/env python3
"""Load cardxref.txt (50-byte records) → cardxref table.

Copybook: CVACT03Y.cpy
"""

from etl_common import get_connection, parse_numeric, data_path, logger

RECORD_LEN = 50
INSERT_SQL = """
    INSERT INTO cardxref (xref_card_num, xref_cust_id, xref_acct_id)
    VALUES (%s,%s,%s)
    ON CONFLICT (xref_card_num) DO NOTHING
"""


def parse_line(line: str) -> tuple:
    return (
        line[0:16].strip(),                        # XREF-CARD-NUM  PIC X(16)
        parse_numeric(line[16:25]),                # XREF-CUST-ID   PIC 9(9)
        parse_numeric(line[25:36]),                # XREF-ACCT-ID   PIC 9(11)
    )


def main():
    filepath = data_path("cardxref.txt")
    conn = get_connection()
    cur = conn.cursor()
    loaded = 0

    with open(filepath, "r") as f:
        for lineno, line in enumerate(f, 1):
            line = line.rstrip("\n").rstrip("\r")
            if not line:
                continue
            line = line.ljust(RECORD_LEN)
            try:
                row = parse_line(line)
                cur.execute(INSERT_SQL, row)
                loaded += 1
            except Exception as exc:
                logger.error("Line %d: %s", lineno, exc)

    conn.commit()
    cur.close()
    conn.close()
    logger.info("cardxref: loaded %d rows", loaded)


if __name__ == "__main__":
    main()
