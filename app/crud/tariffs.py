from datetime import date
from typing import Optional

from sqlalchemy import delete, desc, select
from sqlalchemy.orm import Session

from app.utils.exceptions import (TariffDateNotFound,
                                  TariffForCalculateNotFound, TariffNotFound)
from database.models import Tariff, TariffDate


def get_tariff_date(db: Session, date: date | str) -> Optional[TariffDate]:
    result = db.execute(select(TariffDate).where(TariffDate.date == date))
    tariff_date = result.scalar()

    return tariff_date


def get_tariff_date_lte_date(db: Session, date: date | str) -> TariffDate:
    tariff_date = db.execute(
        select(TariffDate)
        .where(TariffDate.date <= date)
        .order_by(desc(TariffDate.date))
    ).scalar()

    if not tariff_date:
        raise TariffDateNotFound
    
    return tariff_date   


def get_tariff_date(db: Session, date: date | str) -> Optional[TariffDate]:
    result = db.execute(select(TariffDate).where(TariffDate.date == date))
    tariff_date = result.scalar()

    return tariff_date


def get_tariff(db: Session, date_id: int, cargo_type: str) -> Optional[Tariff]:
    tariff = db.execute(
                select(Tariff).where(
                    Tariff.date_id == date_id,
                    Tariff.cargo_type == cargo_type
                )
            ).scalar()
    
    return tariff


def create_tariffs(db: Session, tariffs: dict):
    for date_str, tariffs_list in tariffs.items():
        tariff_date = get_tariff_date(db, date_str)

        if not tariff_date:
            tariff_date = TariffDate(date=date_str)
            db.add(tariff_date)
            db.flush()

        for tariff in tariffs_list:
            existing_tariff = get_tariff(db, tariff_date.id, tariff["cargo_type"])

            if existing_tariff:
                existing_tariff.rate = float(tariff["rate"])
            else:
                new_tariff = Tariff(
                    cargo_type=tariff["cargo_type"],
                    rate=float(tariff["rate"]),
                    date_id=tariff_date.id
                )
                db.add(new_tariff)

    db.commit()


def remove_tariff(db: Session, tariff_date: TariffDate, cargo_type: str):
    tariff = get_tariff(db, tariff_date.id, cargo_type)

    if not tariff:
        raise TariffNotFound

    db.execute(delete(Tariff).where(Tariff.id == tariff.id))
    db.commit()


def update_tariff_in_db(db: Session, tariff_date: TariffDate, cargo_type: str, rate: float):
    tariff = get_tariff(db, tariff_date.id, cargo_type)

    if not tariff:
        raise TariffNotFound
    
    tariff.rate = rate

    db.commit()


def get_tariff_date_or_error(db: Session, date: date | str) -> TariffDate:
    tariff_date = get_tariff_date(db, date)
    
    if not tariff_date:
        raise TariffDateNotFound
    
    return tariff_date


def get_tariff_other_or_error(db: Session, date_id: int) -> Tariff:
    tariff = tariff = db.execute(select(Tariff).where(
        Tariff.date_id == date_id, 
        Tariff.cargo_type == "Other")).scalar()

    if not tariff:
        raise TariffForCalculateNotFound
    
    return tariff
