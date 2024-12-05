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


class TariffRequestSchema(BaseModel):
    date: date
    cargo_type: str


class TariffRequestUpdateSchema(TariffRequestSchema):
    date: date
    cargo_type: str
    rate: float


class InsuranceRequestSchema(TariffRequestSchema):
    cost: float


class StatusResponse(BaseModel):
    status: str
    message: str
