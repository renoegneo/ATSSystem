from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError


# --- custom exceptions ----------------------------------------------------

class NotFoundError(Exception):
    def __init__(self, message: str):
        self.message = message


class ForbiddenError(Exception):
    def __init__(self, message: str = "Доступ запрещён"):
        self.message = message


# --- field name translations ----------------------------------------------

FIELD_NAMES = {
    "act_date":     "Дата акта",
    "car_info":     "Марка и номер машины",
    "driver_phone": "Телефон водителя",
    "boss_phone":   "Телефон шефа",
    "driver_name":  "ФИО водителя",
    "parts":        "Запчасти",
    "works":        "Работы",
    "name":         "Название",
    "price":        "Цена",
    "quantity":     "Кол-во",
    "amount":       "Сумма",
    "password":     "Пароль",
    "old_password": "Старый пароль",
    "new_password": "Новый пароль",
    "confirm":      "Подтверждение пароля",
}


ERROR_MESSAGES = {
    "missing"                   : "Обязательное поле не было заполнено!",
    "string_too_short"          : "Слишком короткое значение",
    "string_too_long"           : "Слишком длинное значение",
    "greater_than"              : "Значение должно быть больше нуля!",
    "float_parsing"             : "Введите число",
    "int_parsing"               : "Введите целое число",
    "date_from_datetime_inexact": "Неверный формат даты",
    "date_parsing"              : "Неверный формат даты",
}


def _format_validation_errors(errors: list) -> list[dict]:
    result = []
    for err in errors:
        # loc is a tuple like ("body", "parts", 0, "price")
        # we take the last meaningful part as field name
        loc = [str(l) for l in err["loc"] if l not in ("body", "query", "path")]
        raw_field = loc[-1] if loc else ""
        field = FIELD_NAMES.get(raw_field, raw_field) if raw_field else ""

        # row number for table errors: loc looks like ["parts", "0", "price"]
        row_hint = ""
        if len(loc) >= 2 and loc[-2].isdigit():
            row_hint = f" (строка {int(loc[-2]) + 1})"

        msg = ERROR_MESSAGES.get(err["type"], err["msg"])

        # validator_value errors carry a custom message we set ourselves
        if err["type"] == "value_error":
            msg = err["msg"].replace("Value error, ", "")

        result.append({"field": f"{field}{row_hint}", "message": msg})
    return result


# --- register all handlers ------------------------------------------------

def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        # triggered when pydantic rejects incoming request data
        errors = _format_validation_errors(exc.errors())
        return JSONResponse(
            status_code=422,
            content={"ok": False, "errors": errors},
        )

    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError):
        return JSONResponse(
            status_code=404, 
            content={"ok": False, "errors": [{"field": "", "message": exc.message}]},
        )

    @app.exception_handler(ForbiddenError)
    async def forbidden_handler(request: Request, exc: ForbiddenError):
        return JSONResponse(
            status_code=403,
            content={"ok": False, "errors": [{"field": "", "message": exc.message}]},
        )

    @app.exception_handler(Exception)
    async def generic_handler(request: Request, exc: Exception):
        # catch-all: something unexpected broke — don't expose internals to user
        return JSONResponse(
            status_code=500,
            content={"ok": False, "errors": [{"field": "", "message": "Внутренняя ошибка сервера. Обратитесь к администратору."}]},
        )