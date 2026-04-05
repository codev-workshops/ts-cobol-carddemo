"""
Transaction Service - Microservice replacement for COTRN00C/01C/02C.cbl
=========================================================================
Original COBOL:
  - COTRN00C.cbl - CICS transaction CT00 - Transaction List
    Browses TRANSACT VSAM file with STARTBR/READNEXT/READPREV
    Supports PF7 (page back), PF8 (page forward), selection
  - COTRN01C.cbl - CICS transaction CT01 - Transaction View
    Reads TRANSACT VSAM by TRAN-ID to display details
  - COTRN02C.cbl - CICS transaction CT02 - Transaction Add
    Writes new record to TRANSACT VSAM file
  - CORPT00C.cbl - CICS transaction CR00 - Transaction Reports
    Generates report based on date range / account filter

Batch programs also migrated:
  - CBTRN01C.cbl - Post transactions (batch processing)
  - CBTRN02C.cbl - Interest calculations
  - CBTRN03C.cbl - Transaction category balance updates

Microservice equivalent:
  - GET    /transactions          -> list (paginated, replaces CT00)
  - GET    /transactions/{id}     -> view detail (replaces CT01)
  - POST   /transactions          -> add transaction (replaces CT02)
  - GET    /transactions/report   -> generate report (replaces CR00)
  - POST   /transactions/process  -> batch process (replaces CBTRN01C)
"""
import os
import datetime
from typing import Optional

import psycopg2
import psycopg2.extras
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(
    title="CardDemo Transaction Service",
    description="Replaces COTRN00C/01C/02C (CT00/CT01/CT02) and batch jobs",
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

class TransactionCreate(BaseModel):
    """
    Maps to COTRN02C.cbl screen input fields for adding a transaction.
    Original: CT02 transaction writes to TRANSACT VSAM.
    """
    tran_type_cd: str
    tran_cat_cd: int = 0
    tran_source: str = ""
    tran_desc: str = ""
    tran_amt: float
    merchant_id: int = 0
    merchant_name: str = ""
    merchant_city: str = ""
    merchant_zip: str = ""
    card_num: str


class ReportRequest(BaseModel):
    """Maps to CORPT00C.cbl report filter fields."""
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    card_num: Optional[str] = None
    tran_type_cd: Optional[str] = None


# --- Endpoints ---

@app.get("/health")
def health():
    return {"status": "healthy", "service": "transaction-service"}


@app.get("/transactions")
def list_transactions(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    card_num: Optional[str] = Query(None),
    tran_type_cd: Optional[str] = Query(None),
):
    """
    Replaces COTRN00C.cbl - paginated transaction list.

    Original COBOL flow:
      1. STARTBR DATASET('TRANSACT') RIDFLD(TRAN-ID)
      2. READNEXT loop for 10 records (page size)
      3. Store first/last TRAN-ID for PF7/PF8 navigation
      4. Selection 'S' -> XCTL to COTRN01C for detail view
    """
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        offset = (page - 1) * page_size

        conditions = []
        params = []
        if card_num:
            conditions.append("card_num = %s")
            params.append(card_num)
        if tran_type_cd:
            conditions.append("tran_type_cd = %s")
            params.append(tran_type_cd)

        where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

        cur.execute(f"SELECT COUNT(*) as total FROM transactions {where}", params)
        total = cur.fetchone()["total"]

        cur.execute(
            f"""SELECT t.*, tt.tran_type_desc
                FROM transactions t
                LEFT JOIN transaction_types tt ON t.tran_type_cd = tt.tran_type_cd
                {where}
                ORDER BY t.tran_id
                LIMIT %s OFFSET %s""",
            params + [page_size, offset],
        )
        transactions = cur.fetchall()

        return {
            "transactions": [dict(t) for t in transactions],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }
    finally:
        conn.close()


@app.get("/transactions/report")
def transaction_report(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    card_num: Optional[str] = Query(None),
    tran_type_cd: Optional[str] = Query(None),
):
    """
    Replaces CORPT00C.cbl - Transaction Report (CR00).
    Generates summary statistics for filtered transactions.

    Original: CORPT00C reads TRANSACT VSAM, generates report to print queue.
    """
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        conditions = []
        params = []
        if start_date:
            conditions.append("orig_ts >= %s")
            params.append(start_date)
        if end_date:
            conditions.append("orig_ts <= %s")
            params.append(end_date)
        if card_num:
            conditions.append("card_num = %s")
            params.append(card_num)
        if tran_type_cd:
            conditions.append("tran_type_cd = %s")
            params.append(tran_type_cd)

        where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

        # Summary by type
        cur.execute(
            f"""SELECT t.tran_type_cd, tt.tran_type_desc,
                       COUNT(*) as count,
                       SUM(t.tran_amt) as total_amount,
                       AVG(t.tran_amt) as avg_amount,
                       MIN(t.tran_amt) as min_amount,
                       MAX(t.tran_amt) as max_amount
                FROM transactions t
                LEFT JOIN transaction_types tt ON t.tran_type_cd = tt.tran_type_cd
                {where}
                GROUP BY t.tran_type_cd, tt.tran_type_desc
                ORDER BY t.tran_type_cd""",
            params,
        )
        by_type = cur.fetchall()

        # Overall totals
        cur.execute(
            f"""SELECT COUNT(*) as total_count,
                       COALESCE(SUM(tran_amt), 0) as total_amount,
                       COALESCE(AVG(tran_amt), 0) as avg_amount
                FROM transactions {where}""",
            params,
        )
        totals = cur.fetchone()

        return {
            "report": {
                "filters": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "card_num": card_num,
                    "tran_type_cd": tran_type_cd,
                },
                "summary_by_type": [dict(r) for r in by_type],
                "totals": dict(totals),
                "generated_at": datetime.datetime.utcnow().isoformat(),
            }
        }
    finally:
        conn.close()


@app.get("/transactions/{tran_id}")
def get_transaction(tran_id: str):
    """
    Replaces COTRN01C.cbl - Transaction detail view (CT01).
    Original: EXEC CICS READ DATASET('TRANSACT') INTO(TRAN-RECORD) RIDFLD(TRAN-ID)
    """
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute(
            """SELECT t.*, tt.tran_type_desc
               FROM transactions t
               LEFT JOIN transaction_types tt ON t.tran_type_cd = tt.tran_type_cd
               WHERE t.tran_id = %s""",
            (tran_id,),
        )
        tran = cur.fetchone()
        if not tran:
            raise HTTPException(status_code=404, detail="Transaction not found")

        return {"transaction": dict(tran)}
    finally:
        conn.close()


@app.post("/transactions", status_code=201)
def create_transaction(tran: TransactionCreate):
    """
    Replaces COTRN02C.cbl - Add transaction (CT02).
    Original COBOL: Writes new TRAN-RECORD to TRANSACT VSAM.
    Auto-generates TRAN-ID (was manual entry in COBOL).
    """
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Verify card exists
        cur.execute("SELECT card_num FROM cards WHERE card_num = %s", (tran.card_num,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Card not found")

        # Generate transaction ID (replaces manual COBOL entry)
        cur.execute("SELECT MAX(tran_id) as max_id FROM transactions")
        row = cur.fetchone()
        max_id = row["max_id"] if row["max_id"] else "0000000000000000"
        new_id = str(int(max_id) + 1).zfill(16)

        now = datetime.datetime.utcnow()

        cur.execute(
            """INSERT INTO transactions
               (tran_id, tran_type_cd, tran_cat_cd, tran_source, tran_desc,
                tran_amt, merchant_id, merchant_name, merchant_city, merchant_zip,
                card_num, orig_ts, proc_ts)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
               RETURNING *""",
            (new_id, tran.tran_type_cd, tran.tran_cat_cd, tran.tran_source,
             tran.tran_desc, tran.tran_amt, tran.merchant_id, tran.merchant_name,
             tran.merchant_city, tran.merchant_zip, tran.card_num, now, now),
        )
        new_tran = cur.fetchone()
        conn.commit()

        return {"transaction": dict(new_tran), "message": "Transaction created successfully"}
    finally:
        conn.close()


@app.post("/transactions/process")
def batch_process():
    """
    Replaces CBTRN01C.cbl - Batch transaction processing (POSTTRAN JCL).

    Original batch flow:
      1. Read DALYTRAN (daily transactions) sequentially
      2. For each: validate card, validate account
      3. Update account balances (ACCT-CURR-BAL, ACCT-CURR-CYC-DEBIT/CREDIT)
      4. Write to TRANSACT file
    """
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Get unprocessed transactions (proc_ts is NULL)
        cur.execute(
            "SELECT * FROM transactions WHERE proc_ts IS NULL ORDER BY tran_id"
        )
        unprocessed = cur.fetchall()

        processed = 0
        errors = []

        for tran in unprocessed:
            try:
                # Update account balance
                if tran["card_num"]:
                    cur.execute(
                        "SELECT acct_id FROM cards WHERE card_num = %s",
                        (tran["card_num"],),
                    )
                    card = cur.fetchone()
                    if card:
                        amt = float(tran["tran_amt"])
                        if amt >= 0:
                            cur.execute(
                                """UPDATE accounts
                                   SET curr_bal = curr_bal + %s,
                                       curr_cyc_debit = curr_cyc_debit + %s,
                                       updated_at = CURRENT_TIMESTAMP
                                   WHERE acct_id = %s""",
                                (amt, amt, card["acct_id"]),
                            )
                        else:
                            cur.execute(
                                """UPDATE accounts
                                   SET curr_bal = curr_bal + %s,
                                       curr_cyc_credit = curr_cyc_credit + ABS(%s),
                                       updated_at = CURRENT_TIMESTAMP
                                   WHERE acct_id = %s""",
                                (amt, amt, card["acct_id"]),
                            )

                # Mark as processed
                cur.execute(
                    "UPDATE transactions SET proc_ts = CURRENT_TIMESTAMP WHERE tran_id = %s",
                    (tran["tran_id"],),
                )
                processed += 1

            except Exception as e:
                errors.append({"tran_id": tran["tran_id"], "error": str(e)})

        conn.commit()

        return {
            "processed": processed,
            "errors": errors,
            "message": f"Batch processing complete: {processed} transactions processed",
        }
    finally:
        conn.close()


@app.get("/transaction-types")
def list_transaction_types():
    """List all transaction types (from TRANTYPE VSAM file)."""
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM transaction_types ORDER BY tran_type_cd")
        return {"transaction_types": [dict(t) for t in cur.fetchall()]}
    finally:
        conn.close()
