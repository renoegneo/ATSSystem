from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from contextlib import asynccontextmanager
from pathlib import Path
import os

from database import init_db
from exceptions import register_exception_handlers
from middleware.auth import AuthMiddleware
from routers import acts, auth, admin
from config import SESSION_SECRET, SESSION_MAX_AGE, HOST, PORT

DEV_MODE = os.getenv("DEV", "0") == "1"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Автосервис",
    docs_url="/docs" if DEV_MODE else None,
    redoc_url=None,
    lifespan=lifespan,
)

# SessionMiddleware must be added LAST so it runs FIRST in the stack
# Starlette applies middleware in reverse order of add_middleware calls
app.add_middleware(AuthMiddleware)
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET, max_age=SESSION_MAX_AGE)

# --- static files ---------------------------------------------------------
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")

# --- routers --------------------------------------------------------------
app.include_router(auth.router)
app.include_router(acts.router)
app.include_router(admin.router)

# --- exception handlers ---------------------------------------------------
register_exception_handlers(app)


@app.get("/")
async def root():
    return RedirectResponse(url="/acts", status_code=302)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=HOST, port=PORT, reload=False)