from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from models import ActIn
from exceptions import NotFoundError
import crud

router = APIRouter(prefix="/acts")
templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")


# --- pages ----------------------------------------------------------------

@router.get("", response_class=HTMLResponse)
async def acts_list(request: Request, q: str = ""):
    acts = crud.search_acts(q) if q else crud.get_all_acts()
    return templates.TemplateResponse(request, "acts/list.html", {
        "acts": acts,
        "query": q,
    })


@router.get("/new", response_class=HTMLResponse)
async def act_new_page(request: Request):
    return templates.TemplateResponse(request, "acts/new.html", {})


@router.get("/{act_id}", response_class=HTMLResponse)
async def act_detail(request: Request, act_id: int):
    act = crud.get_act(act_id)
    if act is None:
        raise NotFoundError("Акт не найден")
    return templates.TemplateResponse(request, "acts/detail.html", {"act": act})


@router.get("/{act_id}/edit", response_class=HTMLResponse)
async def act_edit_page(request: Request, act_id: int):
    act = crud.get_act(act_id)
    if act is None:
        raise NotFoundError("Акт не найден")
    # serialize to dicts so tojson filter works in template
    return templates.TemplateResponse(request, "acts/edit.html", {
        "act": act,
        "parts_json": [p.model_dump() for p in act.parts],
        "works_json": [w.model_dump() for w in act.works],
    })


# --- export placeholder (v2) ----------------------------------------------

@router.get("/{act_id}/export")
async def act_export(act_id: int):
    # TODO v2: export act to PDF or DOCX for printing
    # candidates: WeasyPrint (PDF), python-docx (DOCX)
    from fastapi import HTTPException
    raise HTTPException(status_code=501, detail="Функция экспорта в разработке")


# --- API endpoints (called by JS on the page) -----------------------------

@router.post("/api", response_class=JSONResponse)
async def act_create(data: ActIn):
    act = crud.create_act(data)
    return {"ok": True, "id": act.id}


@router.get("/api/{act_id}", response_class=JSONResponse)
async def act_get(act_id: int):
    act = crud.get_act(act_id)
    if act is None:
        raise NotFoundError("Акт не найден")
    return act.model_dump()


@router.put("/api/{act_id}", response_class=JSONResponse)
async def act_update(act_id: int, data: ActIn):
    act = crud.update_act(act_id, data)
    if act is None:
        raise NotFoundError("Акт не найден")
    return {"ok": True, "id": act.id}