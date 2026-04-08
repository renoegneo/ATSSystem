from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from models import ChangePasswordIn
from exceptions import NotFoundError, ForbiddenError
from config import verify_password, hash_password, USER_PASSWORD_HASH
import crud
import config

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")


# --- pages ----------------------------------------------------------------

@router.get("", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    stats = crud.get_stats("month")
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "stats": stats,
    })


@router.get("/acts", response_class=HTMLResponse)
async def admin_acts(request: Request, q: str = ""):
    acts = crud.search_acts(q) if q else crud.get_all_acts(limit=500)
    return templates.TemplateResponse("admin/acts.html", {
        "request": request,
        "acts": acts,
        "query": q,
    })


@router.get("/stats", response_class=HTMLResponse)
async def admin_stats(request: Request, period: str = "month"):
    stats = crud.get_stats(period)
    return templates.TemplateResponse("admin/stats.html", {
        "request": request,
        "stats": stats,
        "period": period,
    })


@router.get("/audit", response_class=HTMLResponse)
async def admin_audit(request: Request):
    log = crud.get_audit_log()
    return templates.TemplateResponse("admin/audit.html", {
        "request": request,
        "log": log,
    })


@router.get("/settings", response_class=HTMLResponse)
async def admin_settings(request: Request):
    return templates.TemplateResponse("admin/settings.html", {
        "request": request,
        "success": None,
        "error": None,
    })


# --- API endpoints --------------------------------------------------------

@router.delete("/api/acts/{act_id}", response_class=JSONResponse)
async def admin_delete_act(act_id: int):
    deleted = crud.delete_act(act_id)
    if not deleted:
        raise NotFoundError("Акт не найден")
    return {"ok": True}


@router.get("/api/stats", response_class=JSONResponse)
async def admin_stats_api(period: str = "month"):
    return crud.get_stats(period)


@router.post("/api/change-password", response_class=JSONResponse)
async def admin_change_user_password(data: ChangePasswordIn):
    # verify current user password before changing
    if not verify_password(data.old_password, config.USER_PASSWORD_HASH):
        return JSONResponse(
            status_code=400,
            content={"ok": False, "errors": [{"field": "Старый пароль", "message": "Неверный пароль"}]},
        )

    # update the hash in memory (persists until server restart)
    # for permanent change — update USER_PASSWORD_HASH in config.py manually
    config.USER_PASSWORD_HASH = hash_password(data.new_password)
    return {"ok": True, "message": "Пароль успешно изменён"}