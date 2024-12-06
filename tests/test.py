import json
import logging
import unittest
from datetime import date
from time import sleep

from fastapi.testclient import TestClient
from psycopg2 import connect
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from database.base import Base
from database.config import (DB_TEST_HOST, DB_TEST_NAME, DB_TEST_PASS,
                             DB_TEST_PORT, DB_TEST_USER)
from database.session import get_db
from main import app

DATABASE_URL_TEST = f"postgresql://{DB_TEST_USER}:{DB_TEST_PASS}@{DB_TEST_HOST}:{DB_TEST_PORT}/{DB_TEST_NAME}"

engine_test = create_engine(DATABASE_URL_TEST, poolclass=NullPool)

session_maker = sessionmaker(engine_test, expire_on_commit=False)

def override_get_session():
    with session_maker() as session:
        yield session

app.dependency_overrides[get_db] = override_get_session

def wait_for_db():
    for _ in range(25):
        try:
            conn = connect(DATABASE_URL_TEST)
            conn.close()
            return
        except Exception:
            sleep(1)
    raise RuntimeError("Database connection failed after multiple retries")

def init_db():
    with engine_test.begin() as conn:
        Base.metadata.create_all(bind=conn)

def drop_db():
    with engine_test.begin() as conn:
        Base.metadata.drop_all(bind=conn)


class TestBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        wait_for_db()
        init_db()

        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        drop_db()

    def setUp(self):
        self.tariffs_data = {
            "2024-01-01": [
                {"cargo_type": "Other", "rate": 0.35},
                {"cargo_type": "Glass", "rate": 0.50},
            ]
        }


class TestUploadTariffRouters(TestBase):        
    def test_upload_tariffs(self):
        response = self.client.post("tariffs/upload", json=self.tariffs_data)

        assert response.status_code == 201
        assert response.json() == {"status": "success", "message": "Тарифы успешно загружены."}

    def test_upload_tariffs_empty_dict(self):
        response = self.client.post("tariffs/upload", json={})

        assert response.status_code == 400
        assert response.json()["detail"] == "Вы передали пустой словарь" 
    

    def test_upload_tariffs_with_file(self):
        file_data = json.dumps(self.tariffs_data).encode('utf-8')

        response = self.client.post(
            "tariffs/upload_with_file",
            files={"file": ("tariffs.json", file_data, "application/json")},
        )

        assert response.status_code == 201
        assert response.json() == {"status": "success", "message": "Тарифы успешно загружены."}

    def test_upload_tariffs_with_invalid_file_type(self):
        file_data = "Это не JSON файл".encode('utf-8')

        response = self.client.post(
            "tariffs/upload_with_file",
            files={"file": ("invalid_file.txt", file_data, "text/plain")},
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "Файл должен быть формата JSON."

    def test_upload_tariffs_with_invalid_json(self):
        invalid_json = "{invalid: json}".encode('utf-8')

        response = self.client.post(
            "tariffs/upload_with_file",
            files={"file": ("invalid.json", invalid_json, "application/json")},
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "Ошибка при парсинге JSON из файла."


class TestDeleteTariff(TestBase):
    def setUp(self):
        super().setUp()
        self.client.post("tariffs/upload", json=self.tariffs_data)

    def test_delete_tariff_success(self):
        params = {
            "date": "2024-01-01",
            "cargo_type": "Glass"
        }
        response = self.client.request("DELETE", "tariffs/", json=params)

        assert response.status_code == 200
        assert response.json() == {"status": "success", "message": "Тариф успешно удален."}

        check_response = self.client.get("tariffs/list", params={"date": "2024-01-01"})
        assert check_response.status_code == 200
        assert all(tariff["cargo_type"] != "Glass" for tariff in check_response.json()[0]['tariffs'])


    def test_delete_tariff_not_found(self):
        params = {
            "date": "2024-01-01",
            "cargo_type": "TypeC"
        }

        response = self.client.request("DELETE", "tariffs/", json=params)

        assert response.status_code == 404
        assert response.json() == {"detail": "Тариф с указанным cargo_type на данную дату не найден."}

    def test_delete_tariff_invalid_data(self):
        params = {
            "date": "invalid-date",
            "cargo_type": "TypeA"
        }

        response = self.client.request("DELETE", "tariffs/", json=params)

        assert response.status_code == 422
    

class TestUpdateTariffRouter(TestBase):
    def setUp(self):
        super().setUp()
        self.client.post("tariffs/upload", json=self.tariffs_data)

    def test_update_tariff_success(self):
        update_data = {
            "date": "2024-01-01",
            "cargo_type": "Glass",
            "rate": 1.50
        }
        response = self.client.put("tariffs/", json=update_data)

        assert response.status_code == 200
        assert response.json() == {"status": "success", "message": "Тариф успешно обновлен."}

        updated_check = self.client.get("tariffs/list", params={"date": "2024-01-01"})
        assert updated_check.status_code == 200
        updated_tariffs = updated_check.json()[0]["tariffs"]
        updated_tariff = next(tariff for tariff in updated_tariffs if tariff["cargo_type"] == "Glass")
        assert updated_tariff["rate"] == 1.50

    def test_update_tariff_not_found(self):
        update_data = {
            "date": "2024-01-01",
            "cargo_type": "Cargo",
            "rate": 1.5
        }
        response = self.client.put("tariffs/", json=update_data)

        assert response.status_code == 404
        assert response.json() == {"detail": "Тариф с указанным cargo_type на данную дату не найден."}


    def test_update_tariff_date_not_found(self):
        update_data = {
            "date": "2024-01-02",
            "cargo_type": "Cargo",
            "rate": 1.5
        }
        response = self.client.put("tariffs/", json=update_data)

        assert response.status_code == 404
        assert response.json() == {"detail": "На указанную дату тарифов не существует."}


class TestCalculateTarifRouter(TestBase):
    def setUp(self):
        super().setUp()
        self.client.post("tariffs/upload", json=self.tariffs_data)

    
    def test_success_calculate(self):
        data = {
            "date": "2024-01-02",
            "cargo_type": "Glass",
            "cost": 200
        }

        response = self.client.post("insurance/calculate", json=data)

        assert response.status_code == 200
        assert response.json() == 100.0

    def test_calculate_tariff_date_not_found(self):
        data = {
            "date": "2023-01-02",
            "cargo_type": "Glass",
            "cost": 200
        }
        response = self.client.post("insurance/calculate", json=data)

        assert response.status_code == 404
        assert response.json() == {"detail": "На указанную дату тарифов не существует."}

    def test_calculate_tariff_not_found(self):
        params = {
            "date": "2024-01-01",
            "cargo_type": "Other"
        }
        response = self.client.request("DELETE", "tariffs/", json=params)        
        
        data = {
            "date": "2024-01-02",
            "cargo_type": "wood",
            "cost": 200
        }
        response = self.client.post("insurance/calculate", json=data)

        assert response.status_code == 500
        assert response.json() == {"detail": "Тариф для расчета не найден. Обратитесь в тех. поддержку."}
