#!/usr/bin/env python3
"""Load trantype.txt (60-byte records) → trantype table.

Copybook: CVTRA03Y.cpy
"""

from etl_common import get_connection, parse_numeric, data_path, logger

RECORD_LEN = 60
INSERT_SQL = """
    INSERT INTO trantype (tran_type, tran_type_desc)
    VALUES (%s,%s)
    ON CONFLICT (tran_type) DO NOTHING
"""


def parse_line(line: str) -> tuple:
    return (
        line[0:2],                                 # TRAN-TYPE       PIC X(2)
        line[2:52].strip(),                        # TRAN-TYPE-DESC  PIC X(50)
    )


def main():
    filepath = data_path("trantype.txt")
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
    logger.info("trantype: loaded %d rows", loaded)


if __name__ == "__main__":
    main()
