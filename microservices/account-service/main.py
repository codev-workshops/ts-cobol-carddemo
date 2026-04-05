"""
Account Service - Microservice replacement for COACTVWC.cbl and COACTUPC.cbl
==============================================================================
Original COBOL:
  - COACTVWC.cbl - CICS transaction CAVW - Account View
    Reads ACCTDAT, CUSTDAT, CARDDAT VSAM files to display account details
  - COACTUPC.cbl - CICS transaction CAUP - Account Update
    Updates ACCTDAT VSAM file with modified account data

Microservice equivalent:
  - GET  /accounts          -> list accounts (paginated)
  - GET  /accounts/{id}     -> view account details (replaces CAVW)
  - PUT  /accounts/{id}     -> update account (replaces CAUP)
  - GET  /accounts/{id}/cards -> list cards for account
"""
import os
from typing import Optional

import psycopg2
import psycopg2.extras
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(
    title="CardDemo Account Service",
    description="Replaces COACTVWC.cbl (CAVW) and COACTUPC.cbl (CAUP)",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "postgres"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "carddemo"),
    "user": os.getenv("DB_USER", "carddemo"),
    "password": os.getenv("DB_PASSWORD", "carddemo"),
}


def get_conn():
    return psycopg2.connect(**DB_CONFIG)


# --- Models ---

class AccountOut(BaseModel):
    acct_id: int
    active_status: str
    curr_bal: float
    credit_limit: float
    cash_credit_limit: float
    open_date: Optional[str] = None
    expiration_date: Optional[str] = None
    reissue_date: Optional[str] = None
    curr_cyc_credit: float
    curr_cyc_debit: float
    addr_zip: str
    group_id: str


class AccountUpdate(BaseModel):
    """
    Maps to COACTUPC.cbl screen fields that can be modified.
    Original: CAUP transaction updates ACCTDAT VSAM record via REWRITE.
    """
    active_status: Optional[str] = None
    credit_limit: Optional[float] = None
    cash_credit_limit: Optional[float] = None
    expiration_date: Optional[str] = None
    reissue_date: Optional[str] = None
    addr_zip: Optional[str] = None
    group_id: Optional[str] = None


class AccountDetail(BaseModel):
    account: AccountOut
    customer: Optional[dict] = None
    cards: list = []


# --- Endpoints ---

@app.get("/health")
def health():
    return {"status": "healthy", "service": "account-service"}


@app.get("/accounts")
def list_accounts(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    active_only: bool = Query(False),
):
    """
    List accounts with pagination.
    Replaces the account browsing that was done via CICS STARTBR/READNEXT on ACCTDAT.
    """
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        offset = (page - 1) * page_size

        where = "WHERE active_status = 'Y'" if active_only else ""

        cur.execute(f"SELECT COUNT(*) as total FROM accounts {where}")
        total = cur.fetchone()["total"]

        cur.execute(
            f"SELECT * FROM accounts {where} ORDER BY acct_id LIMIT %s OFFSET %s",
            (page_size, offset),
        )
        accounts = cur.fetchall()

        return {
            "accounts": [dict(a) for a in accounts],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }
    finally:
        conn.close()


@app.get("/accounts/{acct_id}")
def get_account(acct_id: int):
    """
    Replaces COACTVWC.cbl paragraphs:
      - 9000-READ-ACCT: READ DATASET('ACCTDAT') for account
      - 9100-READ-CUST: READ DATASET('CUSTDAT') for customer
      - Also reads CARDAIX (card alternate index by account)

    Original COBOL flow:
      1. READ ACCTDAT by ACCT-ID -> ACCOUNT-RECORD
      2. READ CXACAIX (xref by acct) -> get XREF-CUST-ID
      3. READ CUSTDAT by CUST-ID -> CUSTOMER-RECORD
      4. STARTBR CARDAIX -> list cards for this account
    """
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Read account (EXEC CICS READ DATASET('ACCTDAT'))
        cur.execute("SELECT * FROM accounts WHERE acct_id = %s", (acct_id,))
        account = cur.fetchone()
        if not account:
            raise HTTPException(
                status_code=404,
                detail="Did not find this account in account master file",
            )

        # Read customer via xref (EXEC CICS READ DATASET('CXACAIX'))
        cur.execute(
            """SELECT c.* FROM customers c
               JOIN card_xref x ON x.xref_cust_id = c.cust_id
               WHERE x.xref_acct_id = %s LIMIT 1""",
            (acct_id,),
        )
        customer = cur.fetchone()

        # Read cards for account (EXEC CICS STARTBR DATASET('CARDAIX'))
        cur.execute("SELECT * FROM cards WHERE acct_id = %s ORDER BY card_num", (acct_id,))
        cards = cur.fetchall()

        return {
            "account": dict(account),
            "customer": dict(customer) if customer else None,
            "cards": [dict(c) for c in cards],
        }
    finally:
        conn.close()


@app.put("/accounts/{acct_id}")
def update_account(acct_id: int, update: AccountUpdate):
    """
    Replaces COACTUPC.cbl PROCESS-UPDATE paragraph:
      EXEC CICS READ DATASET('ACCTDAT') UPDATE -> modify -> REWRITE
    """
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Verify account exists
        cur.execute("SELECT * FROM accounts WHERE acct_id = %s", (acct_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Account not found")

        # Build dynamic update
        fields = []
        values = []
        update_data = update.model_dump(exclude_none=True)

        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")

        for key, val in update_data.items():
            fields.append(f"{key} = %s")
            values.append(val)

        fields.append("updated_at = CURRENT_TIMESTAMP")
        values.append(acct_id)

        cur.execute(
            f"UPDATE accounts SET {', '.join(fields)} WHERE acct_id = %s RETURNING *",
            values,
        )
        updated = cur.fetchone()
        conn.commit()

        return {"account": dict(updated), "message": "Account updated successfully"}
    finally:
        conn.close()


@app.get("/accounts/{acct_id}/cards")
def list_account_cards(acct_id: int):
    """List all cards for an account (replaces CARDAIX alternate index browse)."""
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM cards WHERE acct_id = %s ORDER BY card_num", (acct_id,))
        cards = cur.fetchall()
        return {"cards": [dict(c) for c in cards], "count": len(cards)}
    finally:
        conn.close()
