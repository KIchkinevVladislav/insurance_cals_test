import json
from typing import List

from fastapi import (APIRouter, Depends, UploadFile, File, HTTPException, status,)
from sqlalchemy.orm import Session

from database.session import get_db
from database.schemas import StatusResponse, TariffDateSchema, TariffRequestSchema
from database.models import TariffDate
from app.crud.tariffs import create_tariffs, get_tarrif_date, remove_tariff
from app.utils.exceptions import TariffNotFound


tariff_routers = APIRouter()


@tariff_routers.post("/upload", status_code=status.HTTP_201_CREATED, response_model=StatusResponse)
def upload_tarrifs(
    tariffs: dict,
    db: Session = Depends(get_db)
):
    """
    Принимаем тарифы словарем
    """
    if not tariffs:
        raise HTTPException(status_code=400, detail="Вы передали пустой словарь")
    
    try: 
        create_tariffs(db, tariffs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при загрузки тарифа {e = }")

    return StatusResponse(status="success", message="Тарифы успешно загружены.")


@tariff_routers.post("/upload_with_file", status_code=status.HTTP_201_CREATED, response_model=StatusResponse)
def upload_tarrifs_with_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Загружает тарифы из JSON файла.
    """
    if file:
        if file.content_type != "application/json":
            raise HTTPException(status_code=400, detail="Файл должен быть формата JSON.")

        contents = file.file.read()
        try:
            contents_str = contents.decode()
            try:
                tariffs = json.loads(contents_str)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Ошибка при парсинге JSON из файла.")
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="Ошибка при декодировании файла. Файл не является текстовым.")
    
    try: 
        create_tariffs(db, tariffs)
    except Exception:
        raise HTTPException(status_code=500, detail=f"Ошибка при загрузки тарифа")

    return StatusResponse(status="success", message="Тарифы успешно загружены.")


@tariff_routers.get("/list", response_model=List[TariffDateSchema])
def get_list_tariffs(db: Session = Depends(get_db)):
    tariff_dates = db.query(TariffDate).all()

    return tariff_dates


@tariff_routers.delete("/", response_model=StatusResponse)
def delete_tariff(request: TariffRequestSchema, db: Session = Depends(get_db)):
    tariff_date = get_tarrif_date(db, request.date)

    if not tariff_date:
        raise HTTPException(status_code=404, detail="На указанную дату тарифов не существует")
    
    try:
        remove_tariff(db, tariff_date, request.cargo_type)
    except TariffNotFound:
        raise HTTPException(status_code=404, detail=f"Тариф c cargo_type = {request.cargo_type} на данную дату не найден")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при удалении тарифа {e = }")
    
    return StatusResponse(status="success", message="Тариф успешно удален.")
