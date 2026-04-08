from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware

# routes that don't require any auth
PUBLIC_ROUTES = {"/login", "/logout"}

# routes that require admin session
ADMIN_ROUTES_PREFIX = "/admin"


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # always allow static files and public routes
        if path.startswith("/static") or path in PUBLIC_ROUTES:
            return await call_next(request)

        session = request.session
        role = session.get("role")  # None | "user" | "admin"

        # not logged in at all — redirect to login
        if role is None:
            return RedirectResponse(url="/login", status_code=302)

        # user trying to access admin routes — redirect to login
        if path.startswith(ADMIN_ROUTES_PREFIX) and role != "admin":
            return RedirectResponse(url="/login", status_code=302)

        return await call_next(request)