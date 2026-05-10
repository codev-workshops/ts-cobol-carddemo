#!/usr/bin/env python3
"""Load custdata.txt (500-byte records) → custdat table.

Copybook: CVCUS01Y.cpy
"""

from etl_common import get_connection, parse_numeric, data_path, logger

RECORD_LEN = 500
INSERT_SQL = """
    INSERT INTO custdat (
        cust_id, cust_first_name, cust_middle_name, cust_last_name,
        cust_addr_line_1, cust_addr_line_2, cust_addr_line_3,
        cust_addr_state_cd, cust_addr_country_cd, cust_addr_zip,
        cust_phone_num_1, cust_phone_num_2, cust_ssn,
        cust_govt_issued_id, cust_dob_yyyy_mm_dd, cust_eft_account_id,
        cust_pri_card_holder_ind, cust_fico_credit_score
    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    ON CONFLICT (cust_id) DO NOTHING
"""


def parse_line(line: str) -> tuple:
    return (
        parse_numeric(line[0:9]),                  # CUST-ID              PIC 9(9)
        line[9:34].strip(),                        # CUST-FIRST-NAME      PIC X(25)
        line[34:59].strip(),                       # CUST-MIDDLE-NAME     PIC X(25)
        line[59:84].strip(),                       # CUST-LAST-NAME       PIC X(25)
        line[84:134].strip(),                      # CUST-ADDR-LINE-1     PIC X(50)
        line[134:184].strip(),                     # CUST-ADDR-LINE-2     PIC X(50)
        line[184:234].strip(),                     # CUST-ADDR-LINE-3     PIC X(50)
        line[234:236],                             # CUST-ADDR-STATE-CD   PIC X(2)
        line[236:239],                             # CUST-ADDR-COUNTRY-CD PIC X(3)
        line[239:249].strip(),                     # CUST-ADDR-ZIP        PIC X(10)
        line[249:264].strip(),                     # CUST-PHONE-NUM-1     PIC X(15)
        line[264:279].strip(),                     # CUST-PHONE-NUM-2     PIC X(15)
        parse_numeric(line[279:288]),              # CUST-SSN             PIC 9(9)
        line[288:308].strip(),                     # CUST-GOVT-ISSUED-ID  PIC X(20)
        line[308:318].strip(),                     # CUST-DOB-YYYY-MM-DD  PIC X(10)
        line[318:328].strip(),                     # CUST-EFT-ACCOUNT-ID  PIC X(10)
        line[328:329],                             # CUST-PRI-CARD-IND    PIC X(1)
        parse_numeric(line[329:332]),              # CUST-FICO-SCORE      PIC 9(3)
    )


def main():
    filepath = data_path("custdata.txt")
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
    logger.info("custdat: loaded %d rows", loaded)


if __name__ == "__main__":
    main()
