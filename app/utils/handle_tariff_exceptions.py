from functools import wraps
from typing import Callable

from fastapi import HTTPException

from app.utils.exceptions import TariffDateNotFound, TariffNotFound


def handle_tariff_exceptions(func: Callable):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except TariffDateNotFound:
            raise HTTPException(
                status_code=404,
                detail="На указанную дату тарифов не существует. Вы можете создать новый тариф"
            )
        except TariffNotFound as e:
            raise HTTPException(
                status_code=404,
                detail=f"Тариф с указанным cargo_type на данную дату не найден."
            )
        except Exception:
            raise HTTPException(
                status_code=500,
                detail="Произошла ошибка при выполнении операции с тарифом"
            )
    return wrapper
