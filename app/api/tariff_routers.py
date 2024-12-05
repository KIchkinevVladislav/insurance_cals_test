import json
from typing import List

from fastapi import (APIRouter, Depends, UploadFile, File, HTTPException, status, Query)
from sqlalchemy.orm import Session

from database.session import get_db
from app.api.schemas import StatusResponse, TariffDateSchema, TariffRequestSchema, TariffRequestUpdateSchema
from database.models import TariffDate
from app.crud.tariffs import create_tariffs, get_tariff_date_or_error, remove_tariff, update_tariff_in_db
from app.utils.handle_tariff_exceptions import handle_tariff_exceptions
    

tariff_routers = APIRouter()


@tariff_routers.post("/upload", status_code=status.HTTP_201_CREATED, response_model=StatusResponse)
def upload_tariffs(
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
def upload_tariffs_with_file(
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
def get_list_tariffs(
    db: Session = Depends(get_db),
    page: int=Query(1, ge=1, description="Номер страницы."),
    size: int=Query(10, le=100, description="Количество записей на странице"),
    sort_desc: bool=Query(False, description="Сортировка в обратном порядке")
):
    query = db.query(TariffDate)

    if not sort_desc:
        query = query.order_by(TariffDate.date.asc())
    else:
        query = query.order_by(TariffDate.date.desc())

    offset = (page - 1) * size
    tariff_dates = query.offset(offset).limit(size).all()

    return tariff_dates


@tariff_routers.delete("/", response_model=StatusResponse)
@handle_tariff_exceptions
def delete_tariff(request: TariffRequestSchema, db: Session = Depends(get_db)):
    tariff_date = get_tariff_date_or_error(db, request.date)
    remove_tariff(db, tariff_date, request.cargo_type)
    
    return StatusResponse(status="success", message="Тариф успешно удален.")


@tariff_routers.put("/", response_model=StatusResponse)
@handle_tariff_exceptions
def update_tariff(request: TariffRequestUpdateSchema, db: Session = Depends(get_db)):
    tariff_date = get_tariff_date_or_error(db, request.date)
    update_tariff_in_db(db, tariff_date, request.cargo_type, request.rate)
    
    return StatusResponse(status="success", message="Тариф успешно обновлен.")
