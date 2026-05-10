# CardDemo Baseline Test Harness

> Phase 0 – Golden reference specification for regression testing after migration.

---

## 1. Online Transaction Tests (CICS)

Each test describes the input sequence on a 3270 terminal and the expected output to capture as the golden reference.

### 1.1 CC00 — Sign-On

| Step | Action | Expected Output |
|:-----|:-------|:----------------|
| 1 | Clear screen, type `CC00` and press Enter | Sign-on screen displayed (COSGN00 map) |
| 2 | Enter `ADMIN001` / `PASSWORD`, press Enter | Admin menu (COADM01 map) displayed |
| 3 | Repeat sign-on with `USER0001` / `PASSWORD` | Main menu (COMEN01 map) displayed |
| 4 | Enter invalid credentials | Error message: "Invalid userid or password" |

### 1.2 CM00 — Main Menu

| Step | Action | Expected Output |
|:-----|:-------|:----------------|
| 1 | Sign on as USER0001 | Main menu with options 1–9 |
| 2 | Enter option `1` (Account View) | CAVW transaction starts |
| 3 | Press PF3 from sub-screen | Returns to main menu |
| 4 | Enter invalid option `99` | Error message displayed |

### 1.3 CAVW — Account View

| Step | Action | Expected Output |
|:-----|:-------|:----------------|
| 1 | Navigate from menu option 1 | Account view screen (COACTVW map) |
| 2 | Enter account ID `00000000001` | Account details displayed: balance, credit limit, dates, card info |
| 3 | Enter non-existent account `99999999999` | "Account not found" message |
| 4 | Capture: balance, credit limit, open date, expiration date, customer name | Golden reference record |

### 1.4 CAUP — Account Update

| Step | Action | Expected Output |
|:-----|:-------|:----------------|
| 1 | Navigate from menu option 2 | Account update screen (COACTUP map) |
| 2 | Enter account ID `00000000001` | Account fields populated, editable |
| 3 | Modify credit limit from current to `25000.00`, press Enter | "Update successful" confirmation |
| 4 | Re-read account to verify | Credit limit shows `25000.00` |
| 5 | Attempt invalid update (alpha in numeric field) | Validation error message |

### 1.5 CCLI — Credit Card List

| Step | Action | Expected Output |
|:-----|:-------|:----------------|
| 1 | Navigate from menu option 3 | Card list screen (COCRDLI map) |
| 2 | Browse forward (PF8) | Next page of cards displayed |
| 3 | Browse backward (PF7) | Previous page of cards |
| 4 | Select a card from the list | Navigates to CCDL (card detail) |
| 5 | Capture: card numbers, account IDs, statuses for first page | Golden reference |

### 1.6 CCDL — Credit Card View

| Step | Action | Expected Output |
|:-----|:-------|:----------------|
| 1 | Select card from CCLI list | Card detail screen (COCRDSL map) |
| 2 | Verify card number, embossed name, CVV, expiry, status | All fields match seed data |
| 3 | Capture all displayed fields | Golden reference record |

### 1.7 CCUP — Credit Card Update

| Step | Action | Expected Output |
|:-----|:-------|:----------------|
| 1 | Navigate from CCLI → select card → edit | Card update screen (COCRDUP map) |
| 2 | Modify embossed name, press Enter | "Update successful" confirmation |
| 3 | Re-read card to verify change | Updated name displayed |

### 1.8 CT00 — Transaction List

| Step | Action | Expected Output |
|:-----|:-------|:----------------|
| 1 | Navigate from menu option 4 | Transaction list screen (COTRN00 map) |
| 2 | Browse forward (PF8) | Next page of transactions |
| 3 | Browse backward (PF7) | Previous page |
| 4 | Select a transaction | Navigates to CT01 (detail) |
| 5 | Capture: transaction IDs, amounts, dates for first page | Golden reference |

### 1.9 CT01 — Transaction View

| Step | Action | Expected Output |
|:-----|:-------|:----------------|
| 1 | Select transaction from CT00 list | Transaction detail screen (COTRN01 map) |
| 2 | Verify all fields: ID, type, amount, merchant, timestamps | Match seed data |
| 3 | Capture all displayed fields | Golden reference record |

### 1.10 CT02 — Transaction Add

| Step | Action | Expected Output |
|:-----|:-------|:----------------|
| 1 | Navigate from menu option 4, select "Add" | Transaction add screen (COTRN02 map) |
| 2 | Enter: type=`01`, category=`0001`, amount=`100.50`, card number, merchant info | Fields accepted |
| 3 | Press Enter to submit | "Transaction added" confirmation |
| 4 | Verify via CT00/CT01 | New transaction appears in list |

### 1.11 CR00 — Transaction Reports

| Step | Action | Expected Output |
|:-----|:-------|:----------------|
| 1 | Navigate from menu option 5 | Report screen (CORPT00 map) |
| 2 | Select report type, press Enter | Report queued to TD queue |
| 3 | Capture: report output format and content | Golden reference |

### 1.12 CB00 — Bill Payment

| Step | Action | Expected Output |
|:-----|:-------|:----------------|
| 1 | Navigate from menu option 6 | Bill payment screen (COBIL00 map) |
| 2 | Enter account ID `00000000001`, payment amount `500.00` | Payment fields populated |
| 3 | Confirm payment | "Payment processed" message |
| 4 | Verify account balance decreased | Balance = previous − 500.00 |
| 5 | Verify transaction record created | New transaction in TRANSACT file |

### 1.13 CA00 — Admin Menu

| Step | Action | Expected Output |
|:-----|:-------|:----------------|
| 1 | Sign on as ADMIN001 | Admin menu (COADM01 map) |
| 2 | Select user management option | Navigates to CU00 |

### 1.14 CU00 — List Users

| Step | Action | Expected Output |
|:-----|:-------|:----------------|
| 1 | Navigate from admin menu | User list screen (COUSR00 map) |
| 2 | Browse forward/backward | Pages of user records |
| 3 | Capture: user IDs, names, types | Golden reference |

### 1.15 CU01 — Add User

| Step | Action | Expected Output |
|:-----|:-------|:----------------|
| 1 | Select "Add" from user list | Add user screen (COUSR01 map) |
| 2 | Enter: ID=`TESTUSER`, fname=`Test`, lname=`User`, pwd=`TESTPWD1`, type=`U` | Fields accepted |
| 3 | Press Enter | "User added" confirmation |
| 4 | Verify in CU00 list | New user appears |

### 1.16 CU02 — Update User

| Step | Action | Expected Output |
|:-----|:-------|:----------------|
| 1 | Select user from CU00 list | Update user screen (COUSR02 map) |
| 2 | Modify last name, press Enter | "User updated" confirmation |
| 3 | Re-read user to verify | Updated name displayed |

### 1.17 CU03 — Delete User

| Step | Action | Expected Output |
|:-----|:-------|:----------------|
| 1 | Select user from CU00 list | Delete user screen (COUSR03 map) |
| 2 | Confirm deletion | "User deleted" confirmation |
| 3 | Verify in CU00 list | User no longer appears |

### 1.18 CDV1 — Developer Transaction

| Step | Action | Expected Output |
|:-----|:-------|:----------------|
| 1 | Enter `CDV1` from clear screen | Developer card search (COCRDSEC) invoked |
| 2 | Enter search criteria | Search results displayed |

---

## 2. Batch Job Tests

Execute the full batch cycle per README lines 209–233. For each job, capture return code, output file contents, and record counts.

### 2.1 Batch Job Sequence

| Job | Program | Expected RC | Output Verification |
|:----|:--------|:-----------:|:--------------------|
| CLOSEFIL | IEFBR14 | 0 | VSAM files closed; CICS can no longer access them |
| ACCTFILE | IDCAMS | 0 | ACCTDATA.VSAM.KSDS loaded; `REPRO` count = 50 records |
| CARDFILE | IDCAMS | 0 | CARDDATA.VSAM.KSDS loaded; `REPRO` count = 50 records |
| XREFFILE | IDCAMS | 0 | CARDXREF.VSAM.KSDS loaded; `REPRO` count = 50 records |
| CUSTFILE | IDCAMS | 0 | CUSTDATA.VSAM.KSDS loaded; `REPRO` count = 50 records |
| TRANBKP | IDCAMS | 0 | TRANSACT.VSAM.KSDS refreshed from combined source |
| TRANEXTR | DSNTIAUL | 0 | *(optional — Db2 module)* Extract transaction types from Db2 |
| TRANCATG | IDCAMS | 0 | TRANCATG.VSAM.KSDS loaded; `REPRO` count = 18 records |
| TRANTYPE | IDCAMS | 0 | TRANTYPE.VSAM.KSDS loaded; `REPRO` count = 7 records |
| DISCGRP | IDCAMS | 0 | DISCGRP.VSAM.KSDS loaded; `REPRO` count = 51 records |
| TCATBALF | IDCAMS | 0 | TCATBALF.VSAM.KSDS loaded |
| DUSRSECJ | IEBGENER | 0 | USRSEC.VSAM.KSDS loaded; 5 user records |
| POSTTRAN | CBTRN02C | 0 | Transactions posted; DALYREJS GDG created if rejects exist |
| INTCALC | *(custom)* | 0 | Interest calculations written to account records |
| TRANBKP | IDCAMS | 0 | Transaction backup GDG generation created |
| COMBTRAN | *(custom)* | 0 | System + daily transactions combined |
| CREASTMT | *(custom)* | 0 | Statement file produced |
| TRANIDX | IDCAMS | 0 | AIX on TRANSACT defined and built |
| OPENFIL | IEFBR14 | 0 | VSAM files reopened to CICS |
| WAITSTEP | *(custom)* | 0 | Timer wait completed |

### 2.2 Batch Output Capture Checklist

For each batch run, capture:

- [ ] SYSOUT / job log (all steps)
- [ ] Return codes for every step
- [ ] `IDCAMS LISTCAT` after each REPRO to confirm record counts
- [ ] GDG generation numbers (DALYREJS, SYSTRAN, TRANSACT.DALY)
- [ ] CBTRN02C DALYREJS output: number of rejected transactions
- [ ] CBTRN03C statement report output
- [ ] Account balances before and after INTCALC

---

## 3. Data Comparison Queries (Aurora vs VSAM)

After migrating data to Aurora PostgreSQL, run these validation queries to confirm parity with VSAM file exports.

### 3.1 Row Count Comparison

```sql
-- Run after ETL load; compare against IDCAMS LISTCAT REC-TOTAL values
SELECT 'acctdat'  AS table_name, COUNT(*) AS row_count, 50  AS expected FROM acctdat
UNION ALL
SELECT 'carddat',  COUNT(*), 50  FROM carddat
UNION ALL
SELECT 'cardxref', COUNT(*), 50  FROM cardxref
UNION ALL
SELECT 'custdat',  COUNT(*), 50  FROM custdat
UNION ALL
SELECT 'transact', COUNT(*), 311 FROM transact
UNION ALL
SELECT 'trantype', COUNT(*), 7   FROM trantype
UNION ALL
SELECT 'trancatg', COUNT(*), 18  FROM trancatg
UNION ALL
SELECT 'discgrp',  COUNT(*), 51  FROM discgrp
UNION ALL
SELECT 'tcatbalf', COUNT(*), 100 FROM tcatbalf
UNION ALL
SELECT 'usrsec',   COUNT(*), 5   FROM usrsec;
```

### 3.2 Key-Based Spot Checks

```sql
-- Account balance check for known accounts
SELECT acct_id, acct_curr_bal, acct_credit_limit
FROM acctdat
WHERE acct_id IN (1, 2, 3)
ORDER BY acct_id;

-- Customer name check
SELECT cust_id, cust_first_name, cust_last_name
FROM custdat
WHERE cust_id IN (1, 2, 3)
ORDER BY cust_id;

-- Card-to-account linkage
SELECT x.xref_card_num, x.xref_acct_id, c.card_acct_id
FROM cardxref x
JOIN carddat c ON c.card_num = x.xref_card_num
WHERE x.xref_acct_id IN (1, 2, 3);
```

### 3.3 Aggregate Checksums

```sql
-- Sum of all account balances (compare with COBOL batch total)
SELECT SUM(acct_curr_bal) AS total_balance,
       SUM(acct_credit_limit) AS total_credit_limit
FROM acctdat;

-- Transaction amount totals by type
SELECT tran_type_cd, COUNT(*) AS txn_count, SUM(tran_amt) AS total_amt
FROM transact
GROUP BY tran_type_cd
ORDER BY tran_type_cd;

-- Category balance totals (should match TCATBALF after posting)
SELECT trancat_type_cd, SUM(tran_cat_bal) AS total_bal
FROM tcatbalf
GROUP BY trancat_type_cd
ORDER BY trancat_type_cd;
```

### 3.4 Referential Integrity Checks

```sql
-- Cards without matching accounts
SELECT card_num, card_acct_id
FROM carddat
WHERE card_acct_id NOT IN (SELECT acct_id FROM acctdat);

-- Cross-references without matching customers
SELECT xref_card_num, xref_cust_id
FROM cardxref
WHERE xref_cust_id NOT IN (SELECT cust_id FROM custdat);

-- Transactions referencing non-existent cards
SELECT tran_id, tran_card_num
FROM transact
WHERE tran_card_num NOT IN (SELECT card_num FROM carddat);

-- Disclosure groups referencing invalid transaction types
SELECT dis_acct_group_id, dis_tran_type_cd
FROM discgrp
WHERE dis_tran_type_cd NOT IN (SELECT tran_type FROM trantype);
```
