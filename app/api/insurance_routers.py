from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.schemas import InsuranceRequestSchema
from app.crud.tariffs import (get_tariff, get_tariff_date_lte_date,
                              get_tariff_other_or_error)
from app.utils.handle_tariff_exceptions import handle_tariff_exceptions
from database.session import get_db

insurance_routers = APIRouter()


@insurance_routers.post("/calculate", response_model=float)
@handle_tariff_exceptions
def calculate_insurance(
    request: InsuranceRequestSchema, 
    db: Session = Depends(get_db)
):
    tariff_date = get_tariff_date_lte_date(db, request.date)
    tariff = get_tariff(db, tariff_date.id, request.cargo_type)
    
    if not tariff:
        tariff = get_tariff_other_or_error(db, tariff_date.id)

    calculated_price = request.cost * tariff.rate
    
    return calculated_price
