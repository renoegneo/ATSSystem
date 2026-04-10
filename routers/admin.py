from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from models import ChangePasswordIn
from exceptions import NotFoundError
from config import verify_password, hash_password, get_user_password_hash
from database import set_setting
import crud

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")


# --- pages ----------------------------------------------------------------

@router.get("", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    stats = crud.get_stats("month")
    return templates.TemplateResponse(request, "admin/dashboard.html", {"stats": stats})


@router.get("/acts", response_class=HTMLResponse)
async def admin_acts(request: Request, q: str = ""):
    acts = crud.search_acts(q) if q else crud.get_all_acts(limit=500)
    return templates.TemplateResponse(request, "admin/acts.html", {
        "acts": acts,
        "query": q,
    })


@router.get("/stats", response_class=HTMLResponse)
async def admin_stats(request: Request, period: str = "month"):
    stats = crud.get_stats(period)
    return templates.TemplateResponse(request, "admin/stats.html", {
        "stats": stats,
        "period": period,
    })


@router.get("/audit", response_class=HTMLResponse)
async def admin_audit(request: Request):
    log = crud.get_audit_log()
    return templates.TemplateResponse(request, "admin/audit.html", {"log": log})


@router.get("/settings", response_class=HTMLResponse)
async def admin_settings(request: Request):
    return templates.TemplateResponse(request, "admin/settings.html", {
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
    if not verify_password(data.old_password, get_user_password_hash()):
        return JSONResponse(
            status_code=400,
            content={"ok": False, "errors": [{"field": "Старый пароль", "message": "Неверный пароль"}]},
        )
    # write new hash to DB — persists across server restarts
    set_setting("user_password_hash", hash_password(data.new_password))
    return {"ok": True, "message": "Пароль успешно изменён"}