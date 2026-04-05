"""
Card Service - Microservice replacement for COCRDLIC.cbl, COCRDSLC.cbl, COCRDUPC.cbl
======================================================================================
Original COBOL:
  - COCRDLIC.cbl - CICS transaction CCLI - Credit Card List
    Browses CARDDAT VSAM file, displays paginated list
  - COCRDSLC.cbl - CICS transaction CCDL - Credit Card View/Detail
    Reads CARDDAT by card number
  - COCRDUPC.cbl - CICS transaction CCUP - Credit Card Update
    Reads CARDDAT for UPDATE, rewrites modified record

Microservice equivalent:
  - GET    /cards              -> list cards (paginated, replaces CCLI)
  - GET    /cards/{card_num}   -> view card detail (replaces CCDL)
  - PUT    /cards/{card_num}   -> update card (replaces CCUP)
  - POST   /cards              -> add new card
"""
import os
from typing import Optional

import psycopg2
import psycopg2.extras
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(
    title="CardDemo Card Service",
    description="Replaces COCRDLIC/COCRDSLC/COCRDUPC (CCLI/CCDL/CCUP transactions)",
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

class CardCreate(BaseModel):
    card_num: str
    acct_id: int
    cvv_cd: str = ""
    embossed_name: str = ""
    expiration_date: Optional[str] = None
    active_status: str = "Y"


class CardUpdate(BaseModel):
    """
    Maps to COCRDUPC.cbl update fields.
    Original: CCUP transaction modifies CARDDAT VSAM via REWRITE.
    """
    embossed_name: Optional[str] = None
    expiration_date: Optional[str] = None
    active_status: Optional[str] = None


# --- Endpoints ---

@app.get("/health")
def health():
    return {"status": "healthy", "service": "card-service"}


@app.get("/cards")
def list_cards(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    acct_id: Optional[int] = Query(None),
):
    """
    Replaces COCRDLIC.cbl - paginated card list.
    Original COBOL:
      - STARTBR DATASET('CARDDAT') RIDFLD(card-num)
      - READNEXT loop (10 per page, matching COTRN00C pattern)
      - PF7/PF8 for page backward/forward
    """
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        offset = (page - 1) * page_size

        where_clause = ""
        params = []
        if acct_id is not None:
            where_clause = "WHERE acct_id = %s"
            params.append(acct_id)

        cur.execute(f"SELECT COUNT(*) as total FROM cards {where_clause}", params)
        total = cur.fetchone()["total"]

        cur.execute(
            f"SELECT * FROM cards {where_clause} ORDER BY card_num LIMIT %s OFFSET %s",
            params + [page_size, offset],
        )
        cards = cur.fetchall()

        return {
            "cards": [dict(c) for c in cards],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }
    finally:
        conn.close()


@app.get("/cards/{card_num}")
def get_card(card_num: str):
    """
    Replaces COCRDSLC.cbl - card detail view.
    Original: EXEC CICS READ DATASET('CARDDAT') INTO(CARD-RECORD) RIDFLD(card-num)
    Also joins with account and customer data via xref.
    """
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute("SELECT * FROM cards WHERE card_num = %s", (card_num,))
        card = cur.fetchone()
        if not card:
            raise HTTPException(status_code=404, detail="Card not found")

        # Get account info
        cur.execute("SELECT * FROM accounts WHERE acct_id = %s", (card["acct_id"],))
        account = cur.fetchone()

        # Get customer info via xref
        cur.execute(
            """SELECT c.* FROM customers c
               JOIN card_xref x ON x.xref_cust_id = c.cust_id
               WHERE x.xref_card_num = %s""",
            (card_num,),
        )
        customer = cur.fetchone()

        return {
            "card": dict(card),
            "account": dict(account) if account else None,
            "customer": dict(customer) if customer else None,
        }
    finally:
        conn.close()


@app.post("/cards", status_code=201)
def create_card(card: CardCreate):
    """Add a new card (extends beyond original COBOL which was view/update only)."""
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Verify account exists
        cur.execute("SELECT acct_id FROM accounts WHERE acct_id = %s", (card.acct_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Account not found")

        cur.execute(
            """INSERT INTO cards (card_num, acct_id, cvv_cd, embossed_name, expiration_date, active_status)
               VALUES (%s, %s, %s, %s, %s, %s) RETURNING *""",
            (card.card_num, card.acct_id, card.cvv_cd, card.embossed_name,
             card.expiration_date, card.active_status),
        )
        new_card = cur.fetchone()
        conn.commit()
        return {"card": dict(new_card), "message": "Card created successfully"}
    except psycopg2.errors.UniqueViolation:
        raise HTTPException(status_code=409, detail="Card number already exists")
    finally:
        conn.close()


@app.put("/cards/{card_num}")
def update_card(card_num: str, update: CardUpdate):
    """
    Replaces COCRDUPC.cbl PROCESS-UPDATE:
      EXEC CICS READ DATASET('CARDDAT') UPDATE RIDFLD(card-num) -> modify -> REWRITE
    """
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute("SELECT * FROM cards WHERE card_num = %s", (card_num,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Card not found")

        fields = []
        values = []
        update_data = update.model_dump(exclude_none=True)

        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")

        for key, val in update_data.items():
            fields.append(f"{key} = %s")
            values.append(val)

        fields.append("updated_at = CURRENT_TIMESTAMP")
        values.append(card_num)

        cur.execute(
            f"UPDATE cards SET {', '.join(fields)} WHERE card_num = %s RETURNING *",
            values,
        )
        updated = cur.fetchone()
        conn.commit()

        return {"card": dict(updated), "message": "Card updated successfully"}
    finally:
        conn.close()
