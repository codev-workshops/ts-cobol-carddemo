#!/usr/bin/env python3
"""Load trancatg.txt (60-byte records) → trancatg table.

Copybook: CVTRA04Y.cpy
"""

from etl_common import get_connection, parse_numeric, data_path, logger

RECORD_LEN = 60
INSERT_SQL = """
    INSERT INTO trancatg (tran_type_cd, tran_cat_cd, tran_cat_type_desc)
    VALUES (%s,%s,%s)
    ON CONFLICT (tran_type_cd, tran_cat_cd) DO NOTHING
"""


def parse_line(line: str) -> tuple:
    return (
        line[0:2],                                 # TRAN-TYPE-CD       PIC X(2)
        parse_numeric(line[2:6]),                  # TRAN-CAT-CD        PIC 9(4)
        line[6:56].strip(),                        # TRAN-CAT-TYPE-DESC PIC X(50)
    )


def main():
    filepath = data_path("trancatg.txt")
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
    logger.info("trancatg: loaded %d rows", loaded)


if __name__ == "__main__":
    main()
