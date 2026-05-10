#!/usr/bin/env python3
"""Load acctdata.txt (300-byte records) → acctdat table.

Copybook: CVACT01Y.cpy
"""

from etl_common import get_connection, parse_numeric, data_path, logger

RECORD_LEN = 300
INSERT_SQL = """
    INSERT INTO acctdat (
        acct_id, acct_active_status, acct_curr_bal, acct_credit_limit,
        acct_cash_credit_limit, acct_open_date, acct_expiraion_date,
        acct_reissue_date, acct_curr_cyc_credit, acct_curr_cyc_debit,
        acct_addr_zip, acct_group_id
    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    ON CONFLICT (acct_id) DO NOTHING
"""


def parse_line(line: str) -> tuple:
    """Parse a single 300-char fixed-width line per CVACT01Y layout."""
    return (
        parse_numeric(line[0:11]),                 # ACCT-ID            PIC 9(11)
        line[11:12],                               # ACCT-ACTIVE-STATUS PIC X(1)
        parse_numeric(line[12:24], 2),             # ACCT-CURR-BAL      PIC S9(10)V99
        parse_numeric(line[24:36], 2),             # ACCT-CREDIT-LIMIT  PIC S9(10)V99
        parse_numeric(line[36:48], 2),             # ACCT-CASH-CR-LIM   PIC S9(10)V99
        line[48:58].strip(),                       # ACCT-OPEN-DATE     PIC X(10)
        line[58:68].strip(),                       # ACCT-EXPIRAION-DATE PIC X(10)
        line[68:78].strip(),                       # ACCT-REISSUE-DATE  PIC X(10)
        parse_numeric(line[78:90], 2),             # ACCT-CURR-CYC-CR   PIC S9(10)V99
        parse_numeric(line[90:102], 2),            # ACCT-CURR-CYC-DB   PIC S9(10)V99
        line[102:112].strip(),                     # ACCT-ADDR-ZIP      PIC X(10)
        line[112:122].strip(),                     # ACCT-GROUP-ID      PIC X(10)
    )


def main():
    filepath = data_path("acctdata.txt")
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
    logger.info("acctdat: loaded %d rows", loaded)


if __name__ == "__main__":
    main()
