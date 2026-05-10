#!/usr/bin/env python3
"""Load tcatbal.txt (50-byte records) → tcatbalf table.

Copybook: CVTRA01Y.cpy
"""

from etl_common import get_connection, parse_numeric, data_path, logger

RECORD_LEN = 50
INSERT_SQL = """
    INSERT INTO tcatbalf (
        trancat_acct_id, trancat_type_cd, trancat_cd, tran_cat_bal
    ) VALUES (%s,%s,%s,%s)
    ON CONFLICT (trancat_acct_id, trancat_type_cd, trancat_cd) DO NOTHING
"""


def parse_line(line: str) -> tuple:
    return (
        parse_numeric(line[0:11]),                 # TRANCAT-ACCT-ID   PIC 9(11)
        line[11:13],                               # TRANCAT-TYPE-CD   PIC X(2)
        parse_numeric(line[13:17]),                # TRANCAT-CD        PIC 9(4)
        parse_numeric(line[17:28], 2),             # TRAN-CAT-BAL      PIC S9(9)V99
    )


def main():
    filepath = data_path("tcatbal.txt")
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
    logger.info("tcatbalf: loaded %d rows", loaded)


if __name__ == "__main__":
    main()
