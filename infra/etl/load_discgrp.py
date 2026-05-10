#!/usr/bin/env python3
"""Load discgrp.txt (50-byte records) → discgrp table.

Copybook: CVTRA02Y.cpy
"""

from etl_common import get_connection, parse_numeric, data_path, logger

RECORD_LEN = 50
INSERT_SQL = """
    INSERT INTO discgrp (
        dis_acct_group_id, dis_tran_type_cd, dis_tran_cat_cd, dis_int_rate
    ) VALUES (%s,%s,%s,%s)
    ON CONFLICT (dis_acct_group_id, dis_tran_type_cd, dis_tran_cat_cd) DO NOTHING
"""


def parse_line(line: str) -> tuple:
    return (
        line[0:10].strip(),                        # DIS-ACCT-GROUP-ID  PIC X(10)
        line[10:12],                               # DIS-TRAN-TYPE-CD   PIC X(2)
        parse_numeric(line[12:16]),                # DIS-TRAN-CAT-CD    PIC 9(4)
        parse_numeric(line[16:22], 2),             # DIS-INT-RATE       PIC S9(4)V99
    )


def main():
    filepath = data_path("discgrp.txt")
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
    logger.info("discgrp: loaded %d rows", loaded)


if __name__ == "__main__":
    main()
