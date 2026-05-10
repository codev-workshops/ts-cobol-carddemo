#!/usr/bin/env python3
"""Load carddata.txt (150-byte records) → carddat table.

Copybook: CVACT02Y.cpy
"""

from etl_common import get_connection, parse_numeric, data_path, logger

RECORD_LEN = 150
INSERT_SQL = """
    INSERT INTO carddat (
        card_num, card_acct_id, card_cvv_cd,
        card_embossed_name, card_expiraion_date, card_active_status
    ) VALUES (%s,%s,%s,%s,%s,%s)
    ON CONFLICT (card_num) DO NOTHING
"""


def parse_line(line: str) -> tuple:
    return (
        line[0:16].strip(),                        # CARD-NUM            PIC X(16)
        parse_numeric(line[16:27]),                # CARD-ACCT-ID        PIC 9(11)
        parse_numeric(line[27:30]),                # CARD-CVV-CD         PIC 9(3)
        line[30:80].strip(),                       # CARD-EMBOSSED-NAME  PIC X(50)
        line[80:90].strip(),                       # CARD-EXPIRAION-DATE PIC X(10)
        line[90:91],                               # CARD-ACTIVE-STATUS  PIC X(1)
    )


def main():
    filepath = data_path("carddata.txt")
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
    logger.info("carddat: loaded %d rows", loaded)


if __name__ == "__main__":
    main()
