from functools import wraps
from typing import Callable

from fastapi import HTTPException

from app.utils.exceptions import (TariffDateNotFound,
                                  TariffForCalculateNotFound, TariffNotFound)


def handle_tariff_exceptions(func: Callable):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except TariffDateNotFound:
            raise HTTPException(
                status_code=404,
                detail="На указанную дату тарифов не существует."
            )
        except TariffNotFound:
            raise HTTPException(
                status_code=404,
                detail=f"Тариф с указанным cargo_type на данную дату не найден."
            )
        except TariffForCalculateNotFound:
            raise HTTPException(
                status_code=500,
                detail=f"Тариф для расчета не найден. Обратитесь в тех. поддержку."
            )
        except Exception:
            raise HTTPException(
                status_code=500,
                detail="Произошла ошибка при выполнении операции с тарифом"
            )
    return wrapper
