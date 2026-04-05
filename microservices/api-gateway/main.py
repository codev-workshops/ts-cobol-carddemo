"""
API Gateway - Unified entry point for CardDemo Microservices
==============================================================
Replaces the CICS Transaction Routing that was handled by the mainframe:
  - CC00 -> Auth Service (sign-on)
  - CAVW/CAUP -> Account Service
  - CCLI/CCDL/CCUP -> Card Service
  - CT00/CT01/CT02/CR00 -> Transaction Service
  - CU00/CU01/CU02/CU03 -> User Admin Service

The gateway proxies requests to the appropriate microservice,
similar to how CICS routed transactions to programs.
"""
import os

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(
    title="CardDemo API Gateway",
    description="Unified gateway - replaces CICS transaction routing",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service URLs (Docker Compose service names)
SERVICES = {
    "auth": os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001"),
    "accounts": os.getenv("ACCOUNT_SERVICE_URL", "http://account-service:8002"),
    "cards": os.getenv("CARD_SERVICE_URL", "http://card-service:8003"),
    "transactions": os.getenv("TRANSACTION_SERVICE_URL", "http://transaction-service:8004"),
    "users": os.getenv("USER_ADMIN_SERVICE_URL", "http://user-admin-service:8005"),
}

# Route mapping (CICS transaction -> microservice)
ROUTE_MAP = {
    "/api/auth": "auth",
    "/api/accounts": "accounts",
    "/api/cards": "cards",
    "/api/transactions": "transactions",
    "/api/transaction-types": "transactions",
    "/api/users": "users",
}


async def proxy_request(service_key: str, path: str, request: Request) -> Response:
    """Forward request to the appropriate microservice."""
    base_url = SERVICES[service_key]
    url = f"{base_url}{path}"

    headers = dict(request.headers)
    headers.pop("host", None)

    body = await request.body()

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.request(
            method=request.method,
            url=url,
            headers=headers,
            content=body,
            params=dict(request.query_params),
        )

    return Response(
        content=resp.content,
        status_code=resp.status_code,
        headers=dict(resp.headers),
    )


# --- Health Check ---

@app.get("/health")
async def health():
    """Check health of all services."""
    statuses = {}
    async with httpx.AsyncClient(timeout=5.0) as client:
        for name, url in SERVICES.items():
            try:
                resp = await client.get(f"{url}/health")
                statuses[name] = resp.json()
            except Exception as e:
                statuses[name] = {"status": "unhealthy", "error": str(e)}

    all_healthy = all(
        s.get("status") == "healthy" for s in statuses.values()
    )
    return {
        "status": "healthy" if all_healthy else "degraded",
        "services": statuses,
    }


# --- Proxy Routes ---

@app.api_route("/api/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def auth_proxy(path: str, request: Request):
    return await proxy_request("auth", f"/auth/{path}", request)


@app.api_route("/api/accounts/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def accounts_proxy(path: str, request: Request):
    return await proxy_request("accounts", f"/accounts/{path}", request)


@app.api_route("/api/accounts", methods=["GET"])
async def accounts_list_proxy(request: Request):
    return await proxy_request("accounts", "/accounts", request)


@app.api_route("/api/cards/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def cards_proxy(path: str, request: Request):
    return await proxy_request("cards", f"/cards/{path}", request)


@app.api_route("/api/cards", methods=["GET", "POST"])
async def cards_list_proxy(request: Request):
    return await proxy_request("cards", "/cards", request)


@app.api_route(
    "/api/transactions/{path:path}", methods=["GET", "POST", "PUT", "DELETE"]
)
async def transactions_proxy(path: str, request: Request):
    return await proxy_request("transactions", f"/transactions/{path}", request)


@app.api_route("/api/transactions", methods=["GET", "POST"])
async def transactions_list_proxy(request: Request):
    return await proxy_request("transactions", "/transactions", request)


@app.api_route("/api/transaction-types", methods=["GET"])
async def transaction_types_proxy(request: Request):
    return await proxy_request("transactions", "/transaction-types", request)


@app.api_route("/api/users/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def users_proxy(path: str, request: Request):
    return await proxy_request("users", f"/users/{path}", request)


@app.api_route("/api/users", methods=["GET", "POST"])
async def users_list_proxy(request: Request):
    return await proxy_request("users", "/users", request)


# --- Static Frontend ---

# Mount frontend files
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="frontend")

    @app.get("/")
    async def serve_frontend():
        return FileResponse(os.path.join(frontend_dir, "index.html"))
