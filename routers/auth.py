from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from config import verify_password, USER_PASSWORD_HASH, ADMIN_PASSWORD_HASH, ADMIN_LOGIN
from pathlib import Path

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    # if already logged in — skip login page
    if request.session.get("role"):
        return RedirectResponse(url="/acts", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@router.post("/login", response_class=HTMLResponse)
async def login_submit(request: Request):
    form = await request.form()
    login    = form.get("login", "").strip()
    password = form.get("password", "").strip()

    # admin login: requires both login and password
    if login:
        if login == ADMIN_LOGIN and verify_password(password, ADMIN_PASSWORD_HASH):
            request.session["role"] = "admin"
            return RedirectResponse(url="/admin", status_code=302)
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Неверный логин или пароль"},
            status_code=401,
        )

    # user login: password only
    if verify_password(password, USER_PASSWORD_HASH):
        request.session["role"] = "user"
        return RedirectResponse(url="/acts", status_code=302)

    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": "Неверный пароль"},
        status_code=401,
    )


@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=302)