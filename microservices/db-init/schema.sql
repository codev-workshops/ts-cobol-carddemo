-- =============================================================================
-- CardDemo Microservices - PostgreSQL Schema
-- Migrated from COBOL VSAM/KSDS data structures (copybooks)
-- =============================================================================
-- Migration Mapping:
--   CSUSR01Y.cpy  -> users (SEC-USER-DATA)
--   CVACT01Y.cpy  -> accounts (ACCOUNT-RECORD)
--   CVACT02Y.cpy  -> cards (CARD-RECORD)
--   CVCUS01Y.cpy  -> customers (CUSTOMER-RECORD)
--   CVACT03Y.cpy  -> card_xref (CARD-XREF-RECORD)
--   CVTRA05Y.cpy  -> transactions (TRAN-RECORD)
--   CVTRA03Y.cpy  -> transaction_types
--   CVTRA04Y.cpy  -> transaction_categories
--   CVTRA02Y.cpy  -> disclosure_groups
-- =============================================================================

-- Users table (from CSUSR01Y.cpy / SEC-USER-DATA)
-- Original: VSAM KSDS keyed on SEC-USR-ID (8 bytes)
CREATE TABLE IF NOT EXISTS users (
    user_id       VARCHAR(8) PRIMARY KEY,          -- SEC-USR-ID PIC X(08)
    first_name    VARCHAR(20) NOT NULL DEFAULT '',  -- SEC-USR-FNAME PIC X(20)
    last_name     VARCHAR(20) NOT NULL DEFAULT '',  -- SEC-USR-LNAME PIC X(20)
    password      VARCHAR(128) NOT NULL,            -- SEC-USR-PWD PIC X(08) -> hashed
    user_type     VARCHAR(1) NOT NULL DEFAULT 'U',  -- SEC-USR-TYPE PIC X(01) A=Admin, U=User
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Customers table (from CVCUS01Y.cpy / CUSTOMER-RECORD)
-- Original: VSAM KSDS keyed on CUST-ID (9 digits)
CREATE TABLE IF NOT EXISTS customers (
    cust_id              SERIAL PRIMARY KEY,                -- CUST-ID PIC 9(09)
    first_name           VARCHAR(25) NOT NULL DEFAULT '',   -- CUST-FIRST-NAME PIC X(25)
    middle_name          VARCHAR(25) DEFAULT '',            -- CUST-MIDDLE-NAME PIC X(25)
    last_name            VARCHAR(25) NOT NULL DEFAULT '',   -- CUST-LAST-NAME PIC X(25)
    addr_line_1          VARCHAR(50) DEFAULT '',            -- CUST-ADDR-LINE-1 PIC X(50)
    addr_line_2          VARCHAR(50) DEFAULT '',            -- CUST-ADDR-LINE-2 PIC X(50)
    addr_line_3          VARCHAR(50) DEFAULT '',            -- CUST-ADDR-LINE-3 PIC X(50)
    addr_state_cd        VARCHAR(2) DEFAULT '',             -- CUST-ADDR-STATE-CD PIC X(02)
    addr_country_cd      VARCHAR(3) DEFAULT '',             -- CUST-ADDR-COUNTRY-CD PIC X(03)
    addr_zip             VARCHAR(10) DEFAULT '',            -- CUST-ADDR-ZIP PIC X(10)
    phone_num_1          VARCHAR(15) DEFAULT '',            -- CUST-PHONE-NUM-1 PIC X(15)
    phone_num_2          VARCHAR(15) DEFAULT '',            -- CUST-PHONE-NUM-2 PIC X(15)
    ssn                  VARCHAR(9) DEFAULT '',             -- CUST-SSN PIC 9(09)
    govt_issued_id       VARCHAR(20) DEFAULT '',            -- CUST-GOVT-ISSUED-ID PIC X(20)
    dob                  DATE,                              -- CUST-DOB-YYYY-MM-DD PIC X(10)
    eft_account_id       VARCHAR(10) DEFAULT '',            -- CUST-EFT-ACCOUNT-ID PIC X(10)
    pri_card_holder_ind  VARCHAR(1) DEFAULT 'Y',            -- CUST-PRI-CARD-HOLDER-IND PIC X(01)
    fico_credit_score    INTEGER DEFAULT 0,                 -- CUST-FICO-CREDIT-SCORE PIC 9(03)
    created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Accounts table (from CVACT01Y.cpy / ACCOUNT-RECORD)
-- Original: VSAM KSDS keyed on ACCT-ID (11 digits)
CREATE TABLE IF NOT EXISTS accounts (
    acct_id              BIGINT PRIMARY KEY,                -- ACCT-ID PIC 9(11)
    active_status        VARCHAR(1) DEFAULT 'Y',            -- ACCT-ACTIVE-STATUS PIC X(01)
    curr_bal             DECIMAL(12,2) DEFAULT 0.00,        -- ACCT-CURR-BAL PIC S9(10)V99
    credit_limit         DECIMAL(12,2) DEFAULT 0.00,        -- ACCT-CREDIT-LIMIT PIC S9(10)V99
    cash_credit_limit    DECIMAL(12,2) DEFAULT 0.00,        -- ACCT-CASH-CREDIT-LIMIT PIC S9(10)V99
    open_date            DATE,                              -- ACCT-OPEN-DATE PIC X(10)
    expiration_date      DATE,                              -- ACCT-EXPIRAION-DATE PIC X(10)
    reissue_date         DATE,                              -- ACCT-REISSUE-DATE PIC X(10)
    curr_cyc_credit      DECIMAL(12,2) DEFAULT 0.00,        -- ACCT-CURR-CYC-CREDIT PIC S9(10)V99
    curr_cyc_debit       DECIMAL(12,2) DEFAULT 0.00,        -- ACCT-CURR-CYC-DEBIT PIC S9(10)V99
    addr_zip             VARCHAR(10) DEFAULT '',            -- ACCT-ADDR-ZIP PIC X(10)
    group_id             VARCHAR(10) DEFAULT '',            -- ACCT-GROUP-ID PIC X(10)
    created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Cards table (from CVACT02Y.cpy / CARD-RECORD)
-- Original: VSAM KSDS keyed on CARD-NUM (16 bytes)
CREATE TABLE IF NOT EXISTS cards (
    card_num             VARCHAR(16) PRIMARY KEY,           -- CARD-NUM PIC X(16)
    acct_id              BIGINT REFERENCES accounts(acct_id),-- CARD-ACCT-ID PIC 9(11)
    cvv_cd               VARCHAR(3) DEFAULT '',             -- CARD-CVV-CD PIC 9(03)
    embossed_name        VARCHAR(50) DEFAULT '',            -- CARD-EMBOSSED-NAME PIC X(50)
    expiration_date      DATE,                              -- CARD-EXPIRAION-DATE PIC X(10)
    active_status        VARCHAR(1) DEFAULT 'Y',            -- CARD-ACTIVE-STATUS PIC X(01)
    created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Card Cross Reference table (from CVACT03Y.cpy / CARD-XREF-RECORD)
-- Original: VSAM KSDS with alternate index paths
CREATE TABLE IF NOT EXISTS card_xref (
    xref_card_num        VARCHAR(16) PRIMARY KEY,           -- XREF-CARD-NUM PIC X(16)
    xref_cust_id         INTEGER REFERENCES customers(cust_id), -- XREF-CUST-ID PIC 9(09)
    xref_acct_id         BIGINT REFERENCES accounts(acct_id),   -- XREF-ACCT-ID PIC 9(11)
    created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transactions table (from CVTRA05Y.cpy / TRAN-RECORD)
-- Original: VSAM KSDS keyed on TRAN-ID (16 bytes)
CREATE TABLE IF NOT EXISTS transactions (
    tran_id              VARCHAR(16) PRIMARY KEY,           -- TRAN-ID PIC X(16)
    tran_type_cd         VARCHAR(2) DEFAULT '',             -- TRAN-TYPE-CD PIC X(02)
    tran_cat_cd          INTEGER DEFAULT 0,                 -- TRAN-CAT-CD PIC 9(04)
    tran_source          VARCHAR(10) DEFAULT '',            -- TRAN-SOURCE PIC X(10)
    tran_desc            VARCHAR(100) DEFAULT '',           -- TRAN-DESC PIC X(100)
    tran_amt             DECIMAL(11,2) DEFAULT 0.00,        -- TRAN-AMT PIC S9(09)V99
    merchant_id          INTEGER DEFAULT 0,                 -- TRAN-MERCHANT-ID PIC 9(09)
    merchant_name        VARCHAR(50) DEFAULT '',            -- TRAN-MERCHANT-NAME PIC X(50)
    merchant_city        VARCHAR(50) DEFAULT '',            -- TRAN-MERCHANT-CITY PIC X(50)
    merchant_zip         VARCHAR(10) DEFAULT '',            -- TRAN-MERCHANT-ZIP PIC X(10)
    card_num             VARCHAR(16),                       -- TRAN-CARD-NUM PIC X(16)
    orig_ts              TIMESTAMP,                         -- TRAN-ORIG-TS PIC X(26)
    proc_ts              TIMESTAMP,                         -- TRAN-PROC-TS PIC X(26)
    created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transaction Types (from CVTRA03Y.cpy)
CREATE TABLE IF NOT EXISTS transaction_types (
    tran_type_cd         VARCHAR(2) PRIMARY KEY,
    tran_type_desc       VARCHAR(50) DEFAULT '',
    created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transaction Categories (from CVTRA04Y.cpy)
CREATE TABLE IF NOT EXISTS transaction_categories (
    tran_cat_cd          INTEGER PRIMARY KEY,
    tran_cat_desc        VARCHAR(50) DEFAULT '',
    created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes (replacing VSAM alternate index paths)
CREATE INDEX IF NOT EXISTS idx_cards_acct_id ON cards(acct_id);
CREATE INDEX IF NOT EXISTS idx_card_xref_cust_id ON card_xref(xref_cust_id);
CREATE INDEX IF NOT EXISTS idx_card_xref_acct_id ON card_xref(xref_acct_id);
CREATE INDEX IF NOT EXISTS idx_transactions_card_num ON transactions(card_num);
CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(tran_type_cd);
CREATE INDEX IF NOT EXISTS idx_transactions_orig_ts ON transactions(orig_ts);
CREATE INDEX IF NOT EXISTS idx_accounts_active ON accounts(active_status);
