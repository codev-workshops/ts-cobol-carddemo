"""
User Admin Service - Microservice replacement for COUSR00C-03C.cbl
===================================================================
Original COBOL:
  - COUSR00C.cbl - CICS transaction CU00 - List Users
    Browses USRSEC VSAM file with STARTBR/READNEXT
  - COUSR01C.cbl - CICS transaction CU01 - Add User
    Writes new record to USRSEC VSAM
  - COUSR02C.cbl - CICS transaction CU02 - Update User
    Reads USRSEC for UPDATE, rewrites modified record
  - COUSR03C.cbl - CICS transaction CU03 - Delete User
    Deletes record from USRSEC VSAM

Note: In original mainframe, these are admin-only functions
      accessible from COADM01C (Admin Menu - transaction CA00).

Microservice equivalent:
  - GET    /users          -> list users (replaces CU00)
  - POST   /users          -> add user (replaces CU01)
  - GET    /users/{id}     -> get user detail
  - PUT    /users/{id}     -> update user (replaces CU02)
  - DELETE /users/{id}     -> delete user (replaces CU03)
"""
import os
from typing import Optional

import psycopg2
import psycopg2.extras
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(
    title="CardDemo User Admin Service",
    description="Replaces COUSR00C-03C (CU00-CU03 transactions) - Admin functions",
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

class UserCreate(BaseModel):
    """
    Maps to COUSR01C.cbl input fields for adding a user.
    Original: CU01 writes to USRSEC VSAM.
    """
    user_id: str
    first_name: str
    last_name: str
    password: str
    user_type: str = "U"


class UserUpdate(BaseModel):
    """
    Maps to COUSR02C.cbl update fields.
    Original: CU02 reads USRSEC for UPDATE, then REWRITE.
    """
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None
    user_type: Optional[str] = None


class UserOut(BaseModel):
    user_id: str
    first_name: str
    last_name: str
    user_type: str


# --- Endpoints ---

@app.get("/health")
def health():
    return {"status": "healthy", "service": "user-admin-service"}


@app.get("/users")
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
):
    """
    Replaces COUSR00C.cbl - User list (CU00).
    Original: STARTBR DATASET('USRSEC'), READNEXT loop for paginated display.
    """
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        offset = (page - 1) * page_size

        cur.execute("SELECT COUNT(*) as total FROM users")
        total = cur.fetchone()["total"]

        cur.execute(
            """SELECT user_id, first_name, last_name, user_type, created_at, updated_at
               FROM users ORDER BY user_id LIMIT %s OFFSET %s""",
            (page_size, offset),
        )
        users = cur.fetchall()

        return {
            "users": [dict(u) for u in users],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }
    finally:
        conn.close()


@app.get("/users/{user_id}")
def get_user(user_id: str):
    """Get user details by ID."""
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(
            "SELECT user_id, first_name, last_name, user_type, created_at, updated_at FROM users WHERE user_id = %s",
            (user_id.upper(),),
        )
        user = cur.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {"user": dict(user)}
    finally:
        conn.close()


@app.post("/users", status_code=201)
def create_user(user: UserCreate):
    """
    Replaces COUSR01C.cbl - Add user (CU01).
    Original: EXEC CICS WRITE DATASET('USRSEC') FROM(SEC-USER-DATA)
    """
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        user_id = user.user_id.upper().strip()
        if not user_id or len(user_id) > 8:
            raise HTTPException(status_code=400, detail="User ID must be 1-8 characters")

        # Check if user already exists
        cur.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
        if cur.fetchone():
            raise HTTPException(status_code=409, detail="User ID already exists")

        cur.execute(
            """INSERT INTO users (user_id, first_name, last_name, password, user_type)
               VALUES (%s, %s, %s, %s, %s)
               RETURNING user_id, first_name, last_name, user_type, created_at""",
            (user_id, user.first_name, user.last_name, user.password,
             user.user_type.upper()),
        )
        new_user = cur.fetchone()
        conn.commit()

        return {"user": dict(new_user), "message": "User created successfully"}
    finally:
        conn.close()


@app.put("/users/{user_id}")
def update_user(user_id: str, update: UserUpdate):
    """
    Replaces COUSR02C.cbl - Update user (CU02).
    Original: EXEC CICS READ DATASET('USRSEC') UPDATE -> modify -> REWRITE
    """
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        uid = user_id.upper()
        cur.execute("SELECT * FROM users WHERE user_id = %s", (uid,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="User not found")

        fields = []
        values = []
        update_data = update.model_dump(exclude_none=True)

        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")

        for key, val in update_data.items():
            fields.append(f"{key} = %s")
            values.append(val)

        fields.append("updated_at = CURRENT_TIMESTAMP")
        values.append(uid)

        cur.execute(
            f"""UPDATE users SET {', '.join(fields)} WHERE user_id = %s
                RETURNING user_id, first_name, last_name, user_type, updated_at""",
            values,
        )
        updated = cur.fetchone()
        conn.commit()

        return {"user": dict(updated), "message": "User updated successfully"}
    finally:
        conn.close()


@app.delete("/users/{user_id}")
def delete_user(user_id: str):
    """
    Replaces COUSR03C.cbl - Delete user (CU03).
    Original: EXEC CICS DELETE DATASET('USRSEC') RIDFLD(SEC-USR-ID)
    """
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        uid = user_id.upper()
        cur.execute("SELECT user_id FROM users WHERE user_id = %s", (uid,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="User not found")

        cur.execute("DELETE FROM users WHERE user_id = %s", (uid,))
        conn.commit()

        return {"message": f"User {uid} deleted successfully"}
    finally:
        conn.close()
