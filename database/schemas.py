from typing import List
from datetime import date

from pydantic import BaseModel


class TariffSchema(BaseModel):
    cargo_type: str
    rate: float

    class Config:
        orm_mode = True


class TariffDateSchema(BaseModel):
    date: date
    tariffs: List[TariffSchema]

    class Config:
        orm_mode = True


class StatusResponse(BaseModel):
    status: str
    message: str
