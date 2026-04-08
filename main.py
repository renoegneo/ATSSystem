from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from pathlib import Path

from database import init_db
from exceptions import register_exception_handlers
from middleware.auth import AuthMiddleware
from routers import acts, auth, admin
from config import SESSION_SECRET, SESSION_MAX_AGE, HOST, PORT

import uvicorn



import os
DEV_MODE = os.getenv("DEV", "0") == "1"

app = FastAPI(
    title="Автосервис",
    docs_url="/docs" if DEV_MODE else None,
    redoc_url=None,
)

# --- middleware (order matters: sessions must come before auth) ------------
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET, max_age=SESSION_MAX_AGE)
app.add_middleware(AuthMiddleware)

# --- static files ---------------------------------------------------------
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")

# --- routers --------------------------------------------------------------
app.include_router(auth.router)
app.include_router(acts.router)
app.include_router(admin.router)

# --- exception handlers ---------------------------------------------------
register_exception_handlers(app)

# --- startup --------------------------------------------------------------
@app.on_event("startup")
async def startup():
    init_db()


# --- root redirect --------------------------------------------------------
from fastapi.responses import RedirectResponse

@app.get("/")
async def root():
    return RedirectResponse(url="/acts", status_code=302)


# --- run ------------------------------------------------------------------
if __name__ == "__main__":
    
    uvicorn.run("main:app", host=HOST, port=PORT, reload=False)