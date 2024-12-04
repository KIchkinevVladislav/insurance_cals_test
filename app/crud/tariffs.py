from sqlalchemy.orm import Session
from sqlalchemy import select

from database.session import get_db
from database.models import TariffDate, Tariff


def create_tariffs(db: Session, tariffs: dict):
    for date_str, tariffs_list in tariffs.items():
        result = db.execute(select(TariffDate).where(TariffDate.date == date_str))
        tariff_date = result.scalar()

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
