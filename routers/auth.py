from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from config import verify_password, get_user_password_hash, get_admin_password_hash, ADMIN_LOGIN
from pathlib import Path

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    if request.session.get("role"):
        return RedirectResponse(url="/acts", status_code=302)
    return templates.TemplateResponse(request, "login.html", {"error": None})


@router.post("/login", response_class=HTMLResponse)
async def login_submit(request: Request):
    form     = await request.form()
    login    = form.get("login", "").strip()
    password = form.get("password", "").strip()

    if login:
        if login == ADMIN_LOGIN and verify_password(password, get_admin_password_hash()):
            request.session["role"] = "admin"
            return RedirectResponse(url="/admin", status_code=302)
        return templates.TemplateResponse(
            request, "login.html",
            {"error": "Неверный логин или пароль"},
            status_code=401,
        )

    if verify_password(password, get_user_password_hash()):
        request.session["role"] = "user"
        return RedirectResponse(url="/acts", status_code=302)

    return templates.TemplateResponse(
        request, "login.html",
        {"error": "Неверный пароль"},
        status_code=401,
    )


@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=302)