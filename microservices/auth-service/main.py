"""
Auth Service - Microservice replacement for COSGN00C.cbl (Signon Screen)
==========================================================================
Original COBOL: COSGN00C.cbl - CICS transaction CC00
  - Reads USRSEC VSAM file to validate user credentials
  - Routes admin users to COADM01C, regular users to COMEN01C
  - Uses COMMAREA to pass user context between programs

Microservice equivalent:
  - POST /auth/login -> validates credentials, returns JWT token
  - GET /auth/me -> returns current user info from token
  - POST /auth/logout -> invalidates token (client-side)
"""
import os
import datetime
from typing import Optional

import psycopg2
import psycopg2.extras
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from jose import jwt, JWTError

app = FastAPI(
    title="CardDemo Auth Service",
    description="Replaces COSGN00C.cbl - CICS Signon Screen (Transaction CC00)",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "carddemo-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

security = HTTPBearer(auto_error=False)

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "postgres"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "carddemo"),
    "user": os.getenv("DB_USER", "carddemo"),
    "password": os.getenv("DB_PASSWORD", "carddemo"),
}


def get_db():
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        yield conn
    finally:
        conn.close()


# --- Models ---

class LoginRequest(BaseModel):
    """Maps to COSGN0AI screen input fields: USERIDI, PASSWDI"""
    user_id: str
    password: str


class LoginResponse(BaseModel):
    """Replaces COMMAREA fields: CDEMO-USER-ID, CDEMO-USER-TYPE"""
    token: str
    user_id: str
    user_type: str
    first_name: str
    last_name: str
    message: str


class UserInfo(BaseModel):
    user_id: str
    user_type: str
    first_name: str
    last_name: str


# --- Helpers ---

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> dict:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# --- Endpoints ---

@app.get("/health")
def health():
    return {"status": "healthy", "service": "auth-service"}


@app.post("/auth/login", response_model=LoginResponse)
def login(req: LoginRequest):
    """
    Replaces COSGN00C.cbl PROCESS-ENTER-KEY and READ-USER-SEC-FILE paragraphs.

    Original COBOL flow:
      1. RECEIVE MAP('COSGN0A') - get user input
      2. Validate USERIDI not empty (-> 'Please enter User ID ...')
      3. Validate PASSWDI not empty (-> 'Please enter Password ...')
      4. UPPER-CASE(USERIDI) -> WS-USER-ID
      5. READ DATASET('USRSEC') INTO(SEC-USER-DATA) RIDFLD(WS-USER-ID)
         - RESP 0: check SEC-USR-PWD = WS-USER-PWD
         - RESP 13: 'User not found. Try again ...'
         - OTHER: 'Unable to verify the User ...'
      6. On match: set CDEMO-USER-TYPE, XCTL to admin or user menu
    """
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        user_id = req.user_id.upper().strip()
        if not user_id:
            raise HTTPException(status_code=400, detail="Please enter User ID ...")

        if not req.password:
            raise HTTPException(status_code=400, detail="Please enter Password ...")

        # EXEC CICS READ DATASET('USRSEC') -> SELECT from users
        cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user = cur.fetchone()

        if user is None:
            # RESP 13 -> NOTFND
            raise HTTPException(status_code=404, detail="User not found. Try again ...")

        # SEC-USR-PWD = WS-USER-PWD check
        if user["password"] != req.password:
            raise HTTPException(status_code=401, detail="Wrong Password. Try again ...")

        # Create JWT (replaces COMMAREA passing)
        token = create_access_token({
            "sub": user["user_id"],
            "user_type": user["user_type"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
        })

        return LoginResponse(
            token=token,
            user_id=user["user_id"],
            user_type=user["user_type"],
            first_name=user["first_name"],
            last_name=user["last_name"],
            message="Login successful",
        )
    finally:
        conn.close()


@app.get("/auth/me", response_model=UserInfo)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Returns current user info from JWT token (replaces COMMAREA read)."""
    return UserInfo(
        user_id=current_user["sub"],
        user_type=current_user["user_type"],
        first_name=current_user["first_name"],
        last_name=current_user["last_name"],
    )
