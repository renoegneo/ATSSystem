from fastapi import Request, Depends
from fastapi.responses import RedirectResponse

# routes that don't require any auth
PUBLIC_ROUTES = {"/login", "/logout"}

# prefix that requires admin role
ADMIN_PREFIX = "/admin"


def get_role(request: Request) -> str | None:
    return request.session.get("role")


def require_user(request: Request):
    # used as a dependency on routers — redirects to login if not authenticated
    if request.url.path in PUBLIC_ROUTES:
        return
    role = request.session.get("role")
    if role is None:
        return RedirectResponse(url="/login", status_code=302)
    return role


def require_admin(request: Request):
    role = request.session.get("role")
    if role != "admin":
        return RedirectResponse(url="/login", status_code=302)
    return role

# def require_user(request: Request):
#     return "user"  # temporarily bypassing auth for development

# def require_admin(request: Request):
#     return "admin"  # temporarily bypassing auth for development