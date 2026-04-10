from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware

PUBLIC = {"/login", "/logout"}
ADMIN_PREFIX = "/admin"

# set to True during development to skip login requirement
AUTH_DISABLED = True


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # always pass through static files and login/logout
        if path.startswith("/static") or path in PUBLIC:
            return await call_next(request)

        if AUTH_DISABLED:
            # block admin routes even in dev mode
            if path.startswith(ADMIN_PREFIX):
                return RedirectResponse(url="/login", status_code=302)
            return await call_next(request)

        role = request.session.get("role")

        if role is None:
            return RedirectResponse(url="/login", status_code=302)

        if path.startswith(ADMIN_PREFIX) and role != "admin":
            return RedirectResponse(url="/login", status_code=302)

        return await call_next(request)