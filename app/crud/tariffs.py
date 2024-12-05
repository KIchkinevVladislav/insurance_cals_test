from datetime import date
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import select, delete

from database.models import TariffDate, Tariff
from app.utils.exceptions import TariffNotFound


def get_tarrif_date(db: Session, date: date | str) -> Optional[TariffDate]:
    result = db.execute(select(TariffDate).where(TariffDate.date == date))
    tariff_date = result.scalar()

    return tariff_date


def create_tariffs(db: Session, tariffs: dict):
    for date_str, tariffs_list in tariffs.items():
        tariff_date = get_tarrif_date(db, date_str)

        if not tariff_date:
            tariff_date = TariffDate(date=date_str)
            db.add(tariff_date)
            db.flush()

        for tariff in tariffs_list:
            existing_tariff = db.execute(
                select(Tariff).where(
                    Tariff.date_id == tariff_date.id,
                    Tariff.cargo_type == tariff["cargo_type"]
                )
            ).scalar()

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
    result = db.execute(
        select(Tariff).where(
            Tariff.date_id == tariff_date.id,
            Tariff.cargo_type == cargo_type
        )
    )
    tariff = result.scalar()

    if not tariff:
        raise TariffNotFound

    db.execute(delete(Tariff).where(Tariff.id == tariff.id))
    db.commit()
