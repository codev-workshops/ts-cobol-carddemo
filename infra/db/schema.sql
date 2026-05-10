--------------------------------------------------------------------------------
-- CardDemo Phase 0 – Aurora PostgreSQL Schema
--
-- Derived from COBOL copybooks in app/cpy/.
-- Mapping rules:
--   PIC 9(n)       → NUMERIC(n)
--   PIC S9(n)V99   → NUMERIC(n+2, 2)
--   PIC S9(n)V99   → NUMERIC(n+2, 2)
--   PIC X(n)       → CHAR(n)
--   VSAM PK        → PRIMARY KEY
--   VSAM AIX       → Secondary index
--------------------------------------------------------------------------------

BEGIN;

--------------------------------------------------------------------------------
-- usrsec – User Security (CSUSR01Y.cpy, RECLN 80)
--
-- Layout:
--   SEC-USR-ID        PIC X(08)   offset 0
--   SEC-USR-FNAME     PIC X(20)   offset 8
--   SEC-USR-LNAME     PIC X(20)   offset 28
--   SEC-USR-PWD       PIC X(08)   offset 48
--   SEC-USR-TYPE      PIC X(01)   offset 56
--   SEC-USR-FILLER    PIC X(23)   offset 57
--------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS usrsec (
    sec_usr_id       CHAR(8)     NOT NULL,
    sec_usr_fname    CHAR(20)    NOT NULL,
    sec_usr_lname    CHAR(20)    NOT NULL,
    sec_usr_pwd      CHAR(8)     NOT NULL,
    sec_usr_type     CHAR(1)     NOT NULL,
    sec_usr_filler   CHAR(23),
    PRIMARY KEY (sec_usr_id)
);

--------------------------------------------------------------------------------
-- acctdat – Account Data (CVACT01Y.cpy, RECLN 300)
--
-- Layout:
--   ACCT-ID                 PIC 9(11)       offset 0
--   ACCT-ACTIVE-STATUS      PIC X(01)       offset 11
--   ACCT-CURR-BAL           PIC S9(10)V99   offset 12
--   ACCT-CREDIT-LIMIT       PIC S9(10)V99   offset 24
--   ACCT-CASH-CREDIT-LIMIT  PIC S9(10)V99   offset 36
--   ACCT-OPEN-DATE          PIC X(10)       offset 48
--   ACCT-EXPIRAION-DATE     PIC X(10)       offset 58
--   ACCT-REISSUE-DATE       PIC X(10)       offset 68
--   ACCT-CURR-CYC-CREDIT   PIC S9(10)V99   offset 78
--   ACCT-CURR-CYC-DEBIT    PIC S9(10)V99   offset 90
--   ACCT-ADDR-ZIP           PIC X(10)       offset 102
--   ACCT-GROUP-ID           PIC X(10)       offset 112
--   FILLER                  PIC X(178)      offset 122
--------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS acctdat (
    acct_id                 NUMERIC(11)     NOT NULL,
    acct_active_status      CHAR(1)         NOT NULL,
    acct_curr_bal           NUMERIC(12, 2)  NOT NULL DEFAULT 0,
    acct_credit_limit       NUMERIC(12, 2)  NOT NULL DEFAULT 0,
    acct_cash_credit_limit  NUMERIC(12, 2)  NOT NULL DEFAULT 0,
    acct_open_date          CHAR(10),
    acct_expiraion_date     CHAR(10),
    acct_reissue_date       CHAR(10),
    acct_curr_cyc_credit    NUMERIC(12, 2)  NOT NULL DEFAULT 0,
    acct_curr_cyc_debit     NUMERIC(12, 2)  NOT NULL DEFAULT 0,
    acct_addr_zip           CHAR(10),
    acct_group_id           CHAR(10),
    PRIMARY KEY (acct_id)
);

--------------------------------------------------------------------------------
-- carddat – Card Data (CVACT02Y.cpy, RECLN 150)
--
-- Layout:
--   CARD-NUM               PIC X(16)   offset 0
--   CARD-ACCT-ID           PIC 9(11)   offset 16
--   CARD-CVV-CD            PIC 9(03)   offset 27
--   CARD-EMBOSSED-NAME     PIC X(50)   offset 30
--   CARD-EXPIRAION-DATE    PIC X(10)   offset 80
--   CARD-ACTIVE-STATUS     PIC X(01)   offset 90
--   FILLER                 PIC X(59)   offset 91
--------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS carddat (
    card_num             CHAR(16)     NOT NULL,
    card_acct_id         NUMERIC(11)  NOT NULL,
    card_cvv_cd          NUMERIC(3)   NOT NULL,
    card_embossed_name   CHAR(50),
    card_expiraion_date  CHAR(10),
    card_active_status   CHAR(1)      NOT NULL,
    PRIMARY KEY (card_num)
);

CREATE INDEX idx_carddat_acct ON carddat (card_acct_id);

--------------------------------------------------------------------------------
-- cardxref – Card Cross-Reference (CVACT03Y.cpy, RECLN 50)
--
-- Layout:
--   XREF-CARD-NUM   PIC X(16)   offset 0
--   XREF-CUST-ID    PIC 9(09)   offset 16
--   XREF-ACCT-ID    PIC 9(11)   offset 25
--   FILLER           PIC X(14)   offset 36
--------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cardxref (
    xref_card_num   CHAR(16)     NOT NULL,
    xref_cust_id    NUMERIC(9)   NOT NULL,
    xref_acct_id    NUMERIC(11)  NOT NULL,
    PRIMARY KEY (xref_card_num)
);

CREATE INDEX idx_cardxref_acct ON cardxref (xref_acct_id);

--------------------------------------------------------------------------------
-- custdat – Customer Data (CVCUS01Y.cpy, RECLN 500)
--
-- Layout:
--   CUST-ID                    PIC 9(09)   offset 0
--   CUST-FIRST-NAME            PIC X(25)   offset 9
--   CUST-MIDDLE-NAME           PIC X(25)   offset 34
--   CUST-LAST-NAME             PIC X(25)   offset 59
--   CUST-ADDR-LINE-1           PIC X(50)   offset 84
--   CUST-ADDR-LINE-2           PIC X(50)   offset 134
--   CUST-ADDR-LINE-3           PIC X(50)   offset 184
--   CUST-ADDR-STATE-CD         PIC X(02)   offset 234
--   CUST-ADDR-COUNTRY-CD       PIC X(03)   offset 236
--   CUST-ADDR-ZIP              PIC X(10)   offset 239
--   CUST-PHONE-NUM-1           PIC X(15)   offset 249
--   CUST-PHONE-NUM-2           PIC X(15)   offset 264
--   CUST-SSN                   PIC 9(09)   offset 279
--   CUST-GOVT-ISSUED-ID        PIC X(20)   offset 288
--   CUST-DOB-YYYY-MM-DD        PIC X(10)   offset 308
--   CUST-EFT-ACCOUNT-ID        PIC X(10)   offset 318
--   CUST-PRI-CARD-HOLDER-IND   PIC X(01)   offset 328
--   CUST-FICO-CREDIT-SCORE     PIC 9(03)   offset 329
--   FILLER                     PIC X(168)  offset 332
--------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS custdat (
    cust_id                  NUMERIC(9)   NOT NULL,
    cust_first_name          CHAR(25),
    cust_middle_name         CHAR(25),
    cust_last_name           CHAR(25),
    cust_addr_line_1         CHAR(50),
    cust_addr_line_2         CHAR(50),
    cust_addr_line_3         CHAR(50),
    cust_addr_state_cd       CHAR(2),
    cust_addr_country_cd     CHAR(3),
    cust_addr_zip            CHAR(10),
    cust_phone_num_1         CHAR(15),
    cust_phone_num_2         CHAR(15),
    cust_ssn                 NUMERIC(9),
    cust_govt_issued_id      CHAR(20),
    cust_dob_yyyy_mm_dd      CHAR(10),
    cust_eft_account_id      CHAR(10),
    cust_pri_card_holder_ind CHAR(1),
    cust_fico_credit_score   NUMERIC(3),
    PRIMARY KEY (cust_id)
);

--------------------------------------------------------------------------------
-- transact – Transaction Record (CVTRA05Y.cpy, RECLN 350)
--
-- Layout:
--   TRAN-ID              PIC X(16)       offset 0
--   TRAN-TYPE-CD         PIC X(02)       offset 16
--   TRAN-CAT-CD          PIC 9(04)       offset 18
--   TRAN-SOURCE          PIC X(10)       offset 22
--   TRAN-DESC            PIC X(100)      offset 32
--   TRAN-AMT             PIC S9(09)V99   offset 132
--   TRAN-MERCHANT-ID     PIC 9(09)       offset 143
--   TRAN-MERCHANT-NAME   PIC X(50)       offset 152
--   TRAN-MERCHANT-CITY   PIC X(50)       offset 202
--   TRAN-MERCHANT-ZIP    PIC X(10)       offset 252
--   TRAN-CARD-NUM        PIC X(16)       offset 262
--   TRAN-ORIG-TS         PIC X(26)       offset 278
--   TRAN-PROC-TS         PIC X(26)       offset 304
--   FILLER               PIC X(20)       offset 330
--------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS transact (
    tran_id            CHAR(16)        NOT NULL,
    tran_type_cd       CHAR(2)         NOT NULL,
    tran_cat_cd        NUMERIC(4)      NOT NULL,
    tran_source        CHAR(10),
    tran_desc          CHAR(100),
    tran_amt           NUMERIC(11, 2)  NOT NULL DEFAULT 0,
    tran_merchant_id   NUMERIC(9),
    tran_merchant_name CHAR(50),
    tran_merchant_city CHAR(50),
    tran_merchant_zip  CHAR(10),
    tran_card_num      CHAR(16)        NOT NULL,
    tran_orig_ts       CHAR(26),
    tran_proc_ts       CHAR(26),
    PRIMARY KEY (tran_id)
);

CREATE INDEX idx_transact_card ON transact (tran_card_num);
CREATE INDEX idx_transact_acct ON transact (tran_type_cd, tran_cat_cd);

--------------------------------------------------------------------------------
-- trantype – Transaction Type (CVTRA03Y.cpy, RECLN 60)
--
-- Layout:
--   TRAN-TYPE       PIC X(02)   offset 0
--   TRAN-TYPE-DESC  PIC X(50)   offset 2
--   FILLER          PIC X(08)   offset 52
--------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS trantype (
    tran_type       CHAR(2)   NOT NULL,
    tran_type_desc  CHAR(50),
    PRIMARY KEY (tran_type)
);

--------------------------------------------------------------------------------
-- trancatg – Transaction Category (CVTRA04Y.cpy, RECLN 60)
--
-- Layout:
--   TRAN-TYPE-CD        PIC X(02)   offset 0   ┐ composite key
--   TRAN-CAT-CD         PIC 9(04)   offset 2   ┘
--   TRAN-CAT-TYPE-DESC  PIC X(50)   offset 6
--   FILLER              PIC X(04)   offset 56
--------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS trancatg (
    tran_type_cd       CHAR(2)     NOT NULL,
    tran_cat_cd        NUMERIC(4)  NOT NULL,
    tran_cat_type_desc CHAR(50),
    PRIMARY KEY (tran_type_cd, tran_cat_cd)
);

--------------------------------------------------------------------------------
-- discgrp – Disclosure Group (CVTRA02Y.cpy, RECLN 50)
--
-- Layout:
--   DIS-ACCT-GROUP-ID   PIC X(10)       offset 0  ┐
--   DIS-TRAN-TYPE-CD    PIC X(02)       offset 10 │ composite key
--   DIS-TRAN-CAT-CD     PIC 9(04)       offset 12 ┘
--   DIS-INT-RATE        PIC S9(04)V99   offset 16
--   FILLER              PIC X(28)       offset 22
--------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS discgrp (
    dis_acct_group_id   CHAR(10)       NOT NULL,
    dis_tran_type_cd    CHAR(2)        NOT NULL,
    dis_tran_cat_cd     NUMERIC(4)     NOT NULL,
    dis_int_rate        NUMERIC(6, 2)  NOT NULL DEFAULT 0,
    PRIMARY KEY (dis_acct_group_id, dis_tran_type_cd, dis_tran_cat_cd)
);

--------------------------------------------------------------------------------
-- tcatbalf – Transaction Category Balance (CVTRA01Y.cpy, RECLN 50)
--
-- Layout:
--   TRANCAT-ACCT-ID   PIC 9(11)       offset 0  ┐
--   TRANCAT-TYPE-CD   PIC X(02)       offset 11 │ composite key
--   TRANCAT-CD        PIC 9(04)       offset 13 ┘
--   TRAN-CAT-BAL      PIC S9(09)V99   offset 17
--   FILLER            PIC X(22)       offset 28
--------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tcatbalf (
    trancat_acct_id   NUMERIC(11)     NOT NULL,
    trancat_type_cd   CHAR(2)         NOT NULL,
    trancat_cd        NUMERIC(4)      NOT NULL,
    tran_cat_bal      NUMERIC(11, 2)  NOT NULL DEFAULT 0,
    PRIMARY KEY (trancat_acct_id, trancat_type_cd, trancat_cd)
);

COMMIT;
