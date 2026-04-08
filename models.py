from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import date
from typing import Annotated


# --- reusable type aliases ------------------------------------------------

PositiveFloat = Annotated[float, Field(gt=0)]
NonEmptyStr   = Annotated[str,   Field(min_length=1, max_length=200)]


# --- table row schemas ----------------------------------------------------

class PartItemIn(BaseModel):
    name:     NonEmptyStr
    price:    PositiveFloat
    quantity: Annotated[float, Field(gt=0)] = 1.0


class WorkItemIn(BaseModel):
    name:     NonEmptyStr
    price:    PositiveFloat
    quantity: Annotated[float, Field(gt=0)] = 1.0


# --- act input ------------------------------------------------------------

class ActIn(BaseModel):
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
            raise ValueError("date cannot be in the future")
        return v

    @model_validator(mode="after")
    def at_least_one_row(self) -> "ActIn":
        if not self.parts and not self.works:
            raise ValueError("act must contain at least one part or work item")
        return self


# --- act output -----------------------------------------------------------

class PartItemOut(BaseModel):
    id: int
    position: int
    name: str
    price: float
    quantity: float
    amount: float


class WorkItemOut(BaseModel):
    id: int
    position: int
    name: str
    price: float
    quantity: float
    amount: float


class ActOut(BaseModel):
    id: int
    act_date: str
    car_info: str
    driver_phone: str | None
    boss_phone: str | None
    driver_name: str | None
    total_amount: float
    created_at: str
    updated_at: str
    parts: list[PartItemOut] = []
    works: list[WorkItemOut] = []


class ActShort(BaseModel):
    # used in list view — no rows included
    id: int
    act_date: str
    car_info: str
    driver_name: str | None
    total_amount: float
    created_at: str


# --- auth -----------------------------------------------------------------

class LoginIn(BaseModel):
    password: Annotated[str, Field(min_length=1)]
    login: str | None = None  # admin only


# --- password change ------------------------------------------------------

class ChangePasswordIn(BaseModel):
    old_password: Annotated[str, Field(min_length=1)]
    new_password: Annotated[str, Field(min_length=4)]
    confirm:      Annotated[str, Field(min_length=4)]

    @model_validator(mode="after")
    def passwords_match(self) -> "ChangePasswordIn":
        if self.new_password != self.confirm:
            raise ValueError("new password and confirmation do not match")
        return self