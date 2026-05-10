# CardDemo Application Dependency Map

> Auto-generated from source analysis of `app/cbl/`, `app/cpy/`, `app/csd/`, and `app/catlg/` — Phase 0

---

## 1. Program Call Graph

Transfer-of-control relationships extracted from `EXEC CICS XCTL`, `EXEC CICS LINK`, and `EXEC CICS START` statements.

| Caller Program | Statement | Target | Notes |
|:---------------|:----------|:-------|:------|
| COSGN00C | XCTL | COADM01C | Admin user sign-on → Admin menu |
| COSGN00C | XCTL | COMEN01C | Regular user sign-on → Main menu |
| COMEN01C | XCTL | *(dynamic)* | `CDEMO-MENU-OPT-PGMNAME(WS-OPTION)` — menu option drives program name |
| COACTVWC | XCTL | *(dynamic)* | `CDEMO-TO-PROGRAM` — navigates to next screen |
| COACTUPC | XCTL | *(dynamic)* | `CDEMO-TO-PROGRAM` — navigates to next screen |
| COCRDLIC | XCTL | *(LIT-MENUPGM)* | Return to main menu |
| COCRDLIC | XCTL | *(dynamic)* | `CCARD-NEXT-PROG` — card detail / update (×2 sites) |
| COCRDSLC | XCTL | *(dynamic)* | `CDEMO-TO-PROGRAM` — navigates to next screen |
| COCRDUPC | XCTL | *(dynamic)* | `CDEMO-TO-PROGRAM` — navigates to next screen |

### Logical Flow (Online)

```
CC00 → COSGN00C ─┬─(admin)──→ COADM01C (CA00)
                  │              └──→ COUSR00C (CU00) → COUSR01C/02C/03C
                  │
                  └─(user)───→ COMEN01C (CM00)
                                 ├──→ COACTVWC (CAVW)
                                 ├──→ COACTUPC (CAUP)
                                 ├──→ COCRDLIC (CCLI) → COCRDSLC (CCDL) → COCRDUPC (CCUP)
                                 ├──→ COTRN00C (CT00) → COTRN01C (CT01) / COTRN02C (CT02)
                                 ├──→ CORPT00C (CR00)
                                 └──→ COBIL00C (CB00)
```

---

## 2. VSAM File Access Map

Each program and the VSAM files (CSD names) it reads, writes, or browses.

### Online Programs (CICS)

| Program | VSAM Files Accessed | Operations |
|:--------|:-------------------|:-----------|
| COSGN00C | USRSEC | READ |
| COMEN01C | *(none — menu-only)* | — |
| COADM01C | *(none — menu-only)* | — |
| COACTVWC | ACCTDAT, CARDDAT, CCXREF, CUSTDAT | READ |
| COACTUPC | ACCTDAT, CUSTDAT | READ, REWRITE |
| COCRDLIC | CARDDAT (via CARDAIX) | STARTBR, READNEXT, READPREV, ENDBR |
| COCRDSLC | CARDDAT, ACCTDAT, CCXREF, CUSTDAT | READ |
| COCRDUPC | CARDDAT | READ, REWRITE |
| COTRN00C | TRANSACT | STARTBR, READNEXT, READPREV |
| COTRN01C | TRANSACT | READ |
| COTRN02C | TRANSACT, ACCTDAT, CCXREF | READ, STARTBR, READPREV, WRITE |
| CORPT00C | TRANSACT | WRITEQ TD |
| COBIL00C | ACCTDAT, CCXREF, TRANSACT | READ, REWRITE, STARTBR, READPREV, WRITE |
| COUSR00C | USRSEC | STARTBR, READNEXT, READPREV, ENDBR |
| COUSR01C | USRSEC | WRITE |
| COUSR02C | USRSEC | READ, REWRITE |
| COUSR03C | USRSEC | READ, DELETE |

### Batch Programs

| Program | Files Accessed | Operations |
|:--------|:--------------|:-----------|
| CBACT01C | ACCTDATA (PS) | OPEN INPUT, READ; also writes OUT-FILE, ARRY-FILE, VBRC-FILE |
| CBACT02C | CARDDATA (PS) | OPEN INPUT, READ |
| CBACT03C | CARDXREF (PS) | OPEN INPUT, READ |
| CBACT04C | TCATBALF, CCXREF, DISCGRP, ACCTDAT, TRANSACT | OPEN INPUT, READ (all five) |
| CBCUS01C | CUSTDATA (PS) | OPEN INPUT, READ |
| CBTRN01C | DALYTRAN, CUSTDATA, CCXREF, CARDDATA, ACCTDATA, TRANSACT | OPEN INPUT/I-O, READ, WRITE |
| CBTRN02C | DALYTRAN, TRANSACT, CCXREF, DALYREJS, ACCTDATA, TCATBALF | OPEN INPUT/I-O, READ, WRITE |
| CBTRN03C | TRANSACT, CCXREF, TRANTYPE, TRANCATG, REPORT, DATEPARMS | OPEN INPUT/OUTPUT, READ, WRITE |
| CBEXPORT | CUSTDATA, ACCTDATA, CCXREF, TRANSACT, CARDDATA, EXPORT-OUTPUT | OPEN INPUT/OUTPUT, READ, WRITE |
| CBIMPORT | EXPORT-INPUT, CUSTDATA, ACCTDATA, CCXREF, TRANSACT, CARDDATA, ERROR-OUTPUT | OPEN INPUT/OUTPUT, READ, WRITE |

---

## 3. Copybook Inclusion Map

| Program | Copybooks Included |
|:--------|:-------------------|
| COADM01C | COCOM01Y, COADM02Y, COADM01, COTTL01Y, CSDAT01Y, CSMSG01Y, CSUSR01Y, DFHAID, DFHBMSCA |
| COACTVWC | CVCRD01Y, COCOM01Y, DFHBMSCA, DFHAID, COTTL01Y, COACTVW, CSDAT01Y, CSMSG01Y, CSMSG02Y, CSUSR01Y, CVACT01Y, CVACT02Y, CVACT03Y, CVCUS01Y, CSSTRPFY |
| COACTUPC | COCOM01Y, COACTUP, COTTL01Y, CSDAT01Y, CSLKPCDY, CSMSG01Y, CSMSG02Y, CSSETATY, CSSTRPFY, CSUSR01Y, CSUTLDPY, CSUTLDWY, CVACT01Y, CVACT03Y, CVCRD01Y, CVCUS01Y, DFHAID, DFHBMSCA |
| COBIL00C | COCOM01Y, COBIL00, COTTL01Y, CSDAT01Y, CSMSG01Y, CVACT01Y, CVACT03Y, CVTRA05Y, DFHAID, DFHBMSCA |
| COCRDLIC | COCOM01Y, COCRDLI, COTTL01Y, CSDAT01Y, CSMSG01Y, CSSTRPFY, CSUSR01Y, CVACT02Y, CVCRD01Y, DFHAID, DFHBMSCA |
| COCRDSLC | COCOM01Y, COCRDSL, COTTL01Y, CSDAT01Y, CSMSG01Y, CSMSG02Y, CSSTRPFY, CSUSR01Y, CVACT02Y, CVCRD01Y, CVCUS01Y, DFHAID, DFHBMSCA |
| COCRDUPC | COCOM01Y, COCRDUP, COTTL01Y, CSDAT01Y, CSMSG01Y, CSMSG02Y, CSSTRPFY, CSUSR01Y, CVACT02Y, CVCRD01Y, CVCUS01Y, DFHAID, DFHBMSCA |
| COMEN01C | COCOM01Y, COMEN01, COMEN02Y, COTTL01Y, CSDAT01Y, CSMSG01Y, CSUSR01Y, DFHAID, DFHBMSCA |
| CORPT00C | COCOM01Y, CORPT00, COTTL01Y, CSDAT01Y, CSMSG01Y, CVTRA05Y, DFHAID, DFHBMSCA |
| COSGN00C | COCOM01Y, COSGN00, COTTL01Y, CSDAT01Y, CSMSG01Y, CSUSR01Y, DFHAID, DFHBMSCA |
| COTRN00C | COCOM01Y, COTRN00, COTTL01Y, CSDAT01Y, CSMSG01Y, CVTRA05Y, DFHAID, DFHBMSCA |
| COTRN01C | COCOM01Y, COTRN01, COTTL01Y, CSDAT01Y, CSMSG01Y, CVTRA05Y, DFHAID, DFHBMSCA |
| COTRN02C | COCOM01Y, COTRN02, COTTL01Y, CSDAT01Y, CSMSG01Y, CVACT01Y, CVACT03Y, CVTRA05Y, DFHAID, DFHBMSCA |
| COUSR00C | COCOM01Y, COUSR00, COTTL01Y, CSDAT01Y, CSMSG01Y, CSUSR01Y, DFHAID, DFHBMSCA |
| COUSR01C | COCOM01Y, COUSR01, COTTL01Y, CSDAT01Y, CSMSG01Y, CSUSR01Y, DFHAID, DFHBMSCA |
| COUSR02C | COCOM01Y, COUSR02, COTTL01Y, CSDAT01Y, CSMSG01Y, CSUSR01Y, DFHAID, DFHBMSCA |
| COUSR03C | COCOM01Y, COUSR03, COTTL01Y, CSDAT01Y, CSMSG01Y, CSUSR01Y, DFHAID, DFHBMSCA |
| CBACT01C | CVACT01Y, CODATECN |
| CBACT02C | CVACT02Y |
| CBACT03C | CVACT03Y |
| CBACT04C | CVACT01Y, CVACT03Y, CVTRA01Y, CVTRA02Y, CVTRA05Y |
| CBCUS01C | CVCUS01Y |
| CBTRN01C | CVACT01Y, CVACT02Y, CVACT03Y, CVCUS01Y, CVTRA05Y, CVTRA06Y |
| CBTRN02C | CVACT01Y, CVACT03Y, CVTRA01Y, CVTRA05Y, CVTRA06Y |
| CBTRN03C | CVACT03Y, CVTRA03Y, CVTRA04Y, CVTRA05Y, CVTRA07Y |
| CBEXPORT | CVACT01Y, CVACT02Y, CVACT03Y, CVCUS01Y, CVEXPORT, CVTRA05Y |
| CBIMPORT | CVACT01Y, CVACT02Y, CVACT03Y, CVCUS01Y, CVEXPORT, CVTRA05Y |

---

## 4. CSD Resource Inventory

Parsed from `app/csd/CARDDEMO.CSD`. All resources are in GROUP(CARDDEMO).

### FILE Definitions

| CSD Name | Dataset | Description |
|:---------|:--------|:------------|
| ACCTDAT | AWS.M2.CARDDEMO.ACCTDATA.VSAM.KSDS | Account master |
| CARDAIX | AWS.M2.CARDDEMO.CARDDATA.VSAM.AIX.PATH | Card AIX path (by acct) |
| CARDDAT | AWS.M2.CARDDEMO.CARDDATA.VSAM.KSDS | Card master |
| CCXREF | AWS.M2.CARDDEMO.CARDXREF.VSAM.KSDS | Card-to-account cross-reference |
| CUSTDAT | AWS.M2.CARDDEMO.CUSTDATA.VSAM.KSDS | Customer master |
| CXACAIX | AWS.M2.CARDDEMO.CARDXREF.VSAM.AIX.PATH | CCXREF AIX path (by acct) |
| TRANSACT | AWS.M2.CARDDEMO.TRANSACT.VSAM.KSDS | Transaction master |
| USRSEC | AWS.M2.CARDDEMO.USRSEC.VSAM.KSDS | User security |

### MAPSET Definitions

| Mapset | Description |
|:-------|:------------|
| COACTUP | Credit card account update map |
| COACTVW | View account |
| COADM01 | Admin menu |
| COBIL00 | Bill payment |
| COCRDLI | List cards |
| COCRDSL | Search cards |
| COCRDUP | Credit card update |
| COMEN01 | Main menu |
| CORPT00 | Transaction reports |
| COSGN00 | Sign-on |
| COTRN00 | Transaction list |
| COTRN01 | Transaction view |
| COTRN02 | Transaction add |
| COUSR00 | List users |
| COUSR01 | Add user |
| COUSR02 | Update user |
| COUSR03 | Delete user |

### PROGRAM Definitions

| Program | Language | Trans ID | Description |
|:--------|:---------|:---------|:------------|
| COACTUPC | COBOL | — | Credit card demo account update |
| COACTVWC | COBOL | CAVW | View account |
| COADM01C | COBOL | — | Admin menu |
| COBIL00C | COBOL | — | Bill payment |
| COCRDLIC | COBOL | CC00 | List cards |
| COCRDSEC | COBOL | — | Credit card search |
| COCRDSLC | COBOL | CCDL | View card detail |
| COCRDUPC | COBOL | — | Credit card update screen |
| COMEN01C | COBOL | — | Main menu |
| CORPT00C | COBOL | — | Transaction reports |
| COSGN00C | COBOL | CC00 | Login |
| COTRN00C | COBOL | — | Transaction list |
| COTRN01C | COBOL | — | Transaction view |
| COTRN02C | COBOL | — | Transaction add |
| COUSR00C | COBOL | — | List users |
| COUSR01C | COBOL | — | Add user |
| COUSR02C | COBOL | — | Update user |
| COUSR03C | COBOL | — | Delete user |

### TRANSACTION Definitions

| Trans ID | Program | Description |
|:---------|:--------|:------------|
| CA00 | COADM01C | Admin menu |
| CAUP | COACTUPC | Account update |
| CAVW | COACTVWC | Account view |
| CB00 | COBIL00C | Bill payment |
| CC00 | COSGN00C | Sign-on (entry point) |
| CCDL | COCRDSLC | Card view/detail |
| CCLI | COCRDLIC | Card list |
| CCUP | COCRDUPC | Card update |
| CDV1 | COCRDSEC | Developer transaction |
| CM00 | COMEN01C | Main menu |
| CR00 | CORPT00C | Transaction reports |
| CT00 | COTRN00C | Transaction list |
| CT01 | COTRN01C | Transaction view |
| CT02 | COTRN02C | Transaction add |
| CU00 | COUSR00C | User list |
| CU01 | COUSR01C | User add |
| CU02 | COUSR02C | User update |
| CU03 | COUSR03C | User delete |

### LIBRARY Definitions

| Library | Dataset |
|:--------|:--------|
| CARDDLIB | AWS.M2.CARDDEMO.LOADLIB |
| COM2DOLL | AWS.M2.CARDDEMO.LOADLIB (disabled) |

---

## 5. VSAM Catalog Inventory

Extracted from `app/catlg/LISTCAT.txt` (IDCAMS LISTCAT output).

### CLUSTER Entries

| Dataset | KEYLEN | RKP | MAXLRECL | REC-TOTAL |
|:--------|-------:|----:|---------:|----------:|
| AWS.M2.CARDDEMO.ACCTDATA.VSAM.KSDS | 11 | 0 | 300 | 50 |
| AWS.M2.CARDDEMO.CARDDATA.VSAM.KSDS | 16 | 0 | 150 | 50 |
| AWS.M2.CARDDEMO.CARDXREF.VSAM.KSDS | 16 | 0 | 50 | 50 |
| AWS.M2.CARDDEMO.CUSTDATA.VSAM.KSDS | 9 | 0 | 500 | 50 |
| AWS.M2.CARDDEMO.DISCGRP.VSAM.KSDS | 16 | 0 | 50 | 51 |
| AWS.M2.CARDDEMO.TCATBALF.VSAM.KSDS | 17 | 0 | 50 | 100 |
| AWS.M2.CARDDEMO.TRANCATG.VSAM.KSDS | 6 | 0 | 60 | 18 |
| AWS.M2.CARDDEMO.TRANSACT.VSAM.KSDS | 16 | 0 | 350 | 311 |
| AWS.M2.CARDDEMO.TRANTYPE.VSAM.KSDS | 2 | 0 | 60 | 7 |
| AWS.M2.CARDDEMO.USRSEC.VSAM.KSDS | 8 | 0 | 80 | 5 |

### AIX Entries

| AIX Dataset | Base Cluster | KEYLEN | RKP |
|:------------|:-------------|-------:|----:|
| AWS.M2.CARDDEMO.CARDDATA.VSAM.AIX | CARDDATA.VSAM.KSDS | 11 | 16 |
| AWS.M2.CARDDEMO.CARDXREF.VSAM.AIX | CARDXREF.VSAM.KSDS | 11 | 16 |
| AWS.M2.CARDDEMO.TRANSACT.VSAM.AIX | TRANSACT.VSAM.KSDS | 26 | — |

### PATH Entries

| Path Dataset | Target |
|:-------------|:-------|
| AWS.M2.CARDDEMO.CARDDATA.VSAM.AIX.PATH | CARDDATA.VSAM.AIX |
| AWS.M2.CARDDEMO.CARDXREF.VSAM.AIX.PATH | CARDXREF.VSAM.AIX |
| AWS.M2.CARDDEMO.TRANSACT.VSAM.AIX.PATH | TRANSACT.VSAM.AIX |

### GDG BASE Entries

| GDG Base | Current Generations |
|:---------|--------------------:|
| AWS.M2.CARDDEMO.DALYREJS | 5 (G0022–G0026) |
| AWS.M2.CARDDEMO.SYSTRAN | 3 (G0016–G0018) |
| AWS.M2.CARDDEMO.TRANSACT.DALY | 25 (G0001–G0025) |
