# CardDemo: Mainframe to Microservices Migration

## Overview

This directory contains the **migrated microservices** version of the CardDemo mainframe application. The original application was built with COBOL, CICS, VSAM, and JCL on an IBM mainframe. It has been decomposed into independent Python FastAPI microservices running in Docker containers.

## Architecture Comparison

### Before: Mainframe (COBOL/CICS/VSAM)

```
┌─────────────────────────────────────────────────┐
│                  CICS Region                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │ COSGN00C │ │ COMEN01C │ │ COADM01C         │ │
│  │ (CC00)   │ │ (CM00)   │ │ (CA00)           │ │
│  │ Sign-on  │ │ Menu     │ │ Admin Menu       │ │
│  └──────────┘ └──────────┘ └──────────────────┘ │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │COACTVWC  │ │COCRDLIC  │ │ COTRN00C/01C/02C │ │
│  │(CAVW)    │ │(CCLI)    │ │ (CT00/01/02)     │ │
│  │Account   │ │Card List │ │ Transactions     │ │
│  └──────────┘ └──────────┘ └──────────────────┘ │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │COUSR00-03│ │CORPT00C  │ │ CBTRN01-03C      │ │
│  │(CU00-03) │ │(CR00)    │ │ Batch Jobs       │ │
│  │User Mgmt │ │Reports   │ │                  │ │
│  └──────────┘ └──────────┘ └──────────────────┘ │
│                                                  │
│  ┌─────────────────────────────────────────────┐ │
│  │          VSAM Files (KSDS)                  │ │
│  │  ACCTDAT | CARDDAT | CUSTDAT | USRSEC       │ │
│  │  TRANSACT | CARDXREF | TRANCATG | TRANTYPE  │ │
│  └─────────────────────────────────────────────┘ │
│                                                  │
│  ┌─────────────────────────────────────────────┐ │
│  │          JCL Batch Jobs                     │ │
│  │  POSTTRAN | INTCALC | CREASTMT | COMBTRAN   │ │
│  └─────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

### After: Microservices (Python/FastAPI/PostgreSQL/Docker)

```
┌─────────────────────────────────────────────────────┐
│              API Gateway (:8000)                     │
│         Replaces CICS Transaction Routing            │
└──────────┬──────┬──────┬──────┬──────┬──────────────┘
           │      │      │      │      │
    ┌──────┴─┐ ┌──┴───┐ ┌┴─────┐ ┌───┴──┐ ┌─────────┐
    │Auth    │ │Acct  │ │Card  │ │Trans │ │User     │
    │Service │ │Svc   │ │Svc   │ │Svc   │ │Admin    │
    │:8001   │ │:8002 │ │:8003 │ │:8004 │ │:8005    │
    │CC00    │ │CAVW  │ │CCLI  │ │CT00  │ │CU00-03  │
    │        │ │CAUP  │ │CCDL  │ │CT01  │ │         │
    │        │ │      │ │CCUP  │ │CT02  │ │         │
    │        │ │      │ │      │ │CR00  │ │         │
    └────┬───┘ └──┬───┘ └──┬───┘ └──┬───┘ └────┬────┘
         │        │        │        │           │
    ┌────┴────────┴────────┴────────┴───────────┴────┐
    │            PostgreSQL (:5432)                    │
    │       Replaces VSAM KSDS Files                  │
    │  users | accounts | cards | customers           │
    │  transactions | card_xref | transaction_types   │
    └─────────────────────────────────────────────────┘
```

## Migration Mapping

### COBOL Programs → Microservice Endpoints

| COBOL Program | CICS Transaction | Microservice | API Endpoint | Description |
|:--------------|:-----------------|:-------------|:-------------|:------------|
| `COSGN00C.cbl` | CC00 | auth-service | `POST /auth/login` | User sign-on |
| `COSGN00C.cbl` | CC00 | auth-service | `GET /auth/me` | Current user info |
| `COACTVWC.cbl` | CAVW | account-service | `GET /accounts/{id}` | Account view |
| `COACTUPC.cbl` | CAUP | account-service | `PUT /accounts/{id}` | Account update |
| `COCRDLIC.cbl` | CCLI | card-service | `GET /cards` | Card list |
| `COCRDSLC.cbl` | CCDL | card-service | `GET /cards/{num}` | Card detail |
| `COCRDUPC.cbl` | CCUP | card-service | `PUT /cards/{num}` | Card update |
| `COTRN00C.cbl` | CT00 | transaction-service | `GET /transactions` | Transaction list |
| `COTRN01C.cbl` | CT01 | transaction-service | `GET /transactions/{id}` | Transaction view |
| `COTRN02C.cbl` | CT02 | transaction-service | `POST /transactions` | Add transaction |
| `CORPT00C.cbl` | CR00 | transaction-service | `GET /transactions/report` | Transaction report |
| `COUSR00C.cbl` | CU00 | user-admin-service | `GET /users` | List users |
| `COUSR01C.cbl` | CU01 | user-admin-service | `POST /users` | Add user |
| `COUSR02C.cbl` | CU02 | user-admin-service | `PUT /users/{id}` | Update user |
| `COUSR03C.cbl` | CU03 | user-admin-service | `DELETE /users/{id}` | Delete user |

### Batch Jobs → API Endpoints

| JCL Job | COBOL Program | API Endpoint | Description |
|:--------|:--------------|:-------------|:------------|
| POSTTRAN | `CBTRN01C.cbl` | `POST /transactions/process` | Batch transaction posting |
| INTCALC | `CBTRN02C.cbl` | (Future) | Interest calculations |
| CREASTMT | `CBSTM03A.cbl` | (Future) | Statement generation |

### Data Storage Migration

| VSAM File | Copybook | PostgreSQL Table | Key |
|:----------|:---------|:-----------------|:----|
| USRSEC | `CSUSR01Y.cpy` | `users` | `user_id` (VARCHAR 8) |
| ACCTDAT | `CVACT01Y.cpy` | `accounts` | `acct_id` (BIGINT) |
| CARDDAT | `CVACT02Y.cpy` | `cards` | `card_num` (VARCHAR 16) |
| CUSTDAT | `CVCUS01Y.cpy` | `customers` | `cust_id` (SERIAL) |
| CARDXREF | `CVACT03Y.cpy` | `card_xref` | `xref_card_num` (VARCHAR 16) |
| TRANSACT | `CVTRA05Y.cpy` | `transactions` | `tran_id` (VARCHAR 16) |
| TRANTYPE | `CVTRA03Y.cpy` | `transaction_types` | `tran_type_cd` (VARCHAR 2) |
| TRANCATG | `CVTRA04Y.cpy` | `transaction_categories` | `tran_cat_cd` (INTEGER) |

### Technology Mapping

| Mainframe | Microservices | Notes |
|:----------|:--------------|:------|
| COBOL | Python (FastAPI) | Business logic rewritten as REST APIs |
| CICS | API Gateway (FastAPI) | Transaction routing → HTTP routing |
| VSAM KSDS | PostgreSQL | Indexed sequential → relational tables |
| VSAM AIX (Alternate Index) | SQL JOINs + DB indexes | Alternate access paths → SQL queries |
| BMS Maps | HTML/CSS/JS Frontend | 3270 screens → web UI |
| COMMAREA | JWT Tokens + HTTP | Inter-program data passing → API calls |
| JCL Batch | REST API endpoints | Batch jobs → on-demand API calls |
| RACF Security | JWT Authentication | Mainframe security → token-based auth |
| EBCDIC | UTF-8 | Character encoding modernized |

## Quick Start

### Prerequisites
- Docker and Docker Compose installed

### Running the Application

```bash
cd microservices
docker-compose up --build
```

### Accessing the Application
- **Web UI**: http://localhost:8000
- **API Gateway**: http://localhost:8000/api/
- **API Docs**: http://localhost:800{1-5}/docs (per service)

### Default Credentials
- Admin: `ADMIN001` / `PASSWORD`
- User: `USER0001` / `PASSWORD`

## Service Ports

| Service | Port | Replaces |
|:--------|:-----|:---------|
| API Gateway | 8000 | CICS Transaction Routing |
| Auth Service | 8001 | COSGN00C (CC00) |
| Account Service | 8002 | COACTVWC/COACTUPC (CAVW/CAUP) |
| Card Service | 8003 | COCRDLIC/COCRDSLC/COCRDUPC (CCLI/CCDL/CCUP) |
| Transaction Service | 8004 | COTRN00C/01C/02C, CORPT00C (CT00-02, CR00) |
| User Admin Service | 8005 | COUSR00C-03C (CU00-CU03) |
| PostgreSQL | 5432 | VSAM Files |

## Key Migration Decisions

1. **Language**: Python was chosen for readability and fast development; Java/Spring Boot is a common alternative for enterprise migrations.

2. **Database**: PostgreSQL replaces VSAM. Each COBOL copybook (`*Y.cpy`) maps to a table. VSAM key structures become primary keys; alternate indexes become SQL indexes.

3. **Authentication**: JWT tokens replace COMMAREA-based session passing. The original stored user context in CICS COMMAREA fields (`CDEMO-USER-ID`, `CDEMO-USER-TYPE`); now these are JWT claims.

4. **Pagination**: COBOL used STARTBR/READNEXT/READPREV with PF7/PF8 keys. Microservices use SQL LIMIT/OFFSET with page parameters.

5. **Batch Processing**: JCL batch jobs (POSTTRAN, INTCALC) become on-demand REST endpoints. In production, these would typically be scheduled via cron, Kubernetes CronJobs, or event-driven triggers.

6. **Error Handling**: CICS RESP/RESP2 codes map to HTTP status codes (404 for NOTFND, 409 for DUPREC, etc.).
