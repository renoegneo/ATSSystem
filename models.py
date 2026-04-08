from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import date
from typing import Annotated


# --- общие типы -----------------------------------------------------------
# common types for validation

PositiveFloat = Annotated[float, Field(gt=0)]
NonEmptyStr   = Annotated[str,   Field(min_length=1, max_length=500)]


# --- строки таблиц --------------------------------------------------------
# request models for tables

class PartItemIn(BaseModel):
    """Request for the parts table"""
    name:     NonEmptyStr
    price:    PositiveFloat
    quantity: Annotated[float, Field(gt=0, default=1.0)] = 1.0


class WorkItemIn(BaseModel):
    """Request for the works table"""
    name:     NonEmptyStr
    price:    PositiveFloat
    quantity: Annotated[float, Field(gt=0, default=1.0)] = 1.0


# --- акт ------------------------------------------------------------------
# all about acts

class ActIn(BaseModel):
    """Request of act creation or update."""
    act_date:     date
    car_info:     Annotated[str, Field(min_length=2, max_length=100)]
    driver_phone: str | None = None
    boss_phone:   str | None = None
    driver_name:  str | None = None
    parts:        list[PartItemIn] = []
    works:        list[WorkItemIn] = []

    @field_validator("act_date")
    @classmethod
    def date_not_in_future(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("Дата не может быть в будущем")
        return v

    @model_validator(mode="after")
    def at_least_one_row(self) -> "ActIn":
        if not self.parts and not self.works:
            raise ValueError("Акт должен содержать хотя бы одну запчасть или работу")
        return self


# --- ответы сервера -------------------------------------------------------
# server responses 

class PartItemOut(BaseModel):
    id:       int
    position: int
    name:     str
    price:    float
    quantity: float
    amount:   float


class WorkItemOut(BaseModel):
    id:       int
    position: int
    name:     str
    price:    float
    quantity: float
    amount:   float


class ActOut(BaseModel):
    id:           int
    act_date:     str
    car_info:     str
    driver_phone: str | None
    boss_phone:   str | None
    driver_name:  str | None
    total_amount: float
    created_at:   str
    updated_at:   str
    parts:        list[PartItemOut] = []
    works:        list[WorkItemOut] = []


class ActShort(BaseModel):
    """Short version of act model"""
    id          : int
    act_date    : str
    car_info    : str
    driver_name : str | None
    total_amount: float
    created_at  : str


# --- авторизация ----------------------------------------------------------
# authorization models

class LoginIn(BaseModel):
    password: Annotated[str, Field(min_length=1)]
    login:    str | None = None  # только для админа


# --- смена пароля ---------------------------------------------------------
# password change models

class ChangePasswordIn(BaseModel):
    old_password: Annotated[str, Field(min_length=1)]
    new_password: Annotated[str, Field(min_length=4)]
    confirm:      Annotated[str, Field(min_length=4)]

    @model_validator(mode="after")
    def passwords_match(self) -> "ChangePasswordIn":
        if self.new_password != self.confirm:
            raise ValueError("Новый пароль и подтверждение не совпадают")
        return self