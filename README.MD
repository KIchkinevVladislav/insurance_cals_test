REST API для сервиса по расчёту стоимости страхования в зависимости от типа груза и объявленной стоимости

Реализованы следующие возможности

    Работа с тарифами:
    - POST /tarrifs/upload загрузка тарифов JSON-подобной структурой
    - POST /tarrifs/upload_with_file загрузка файлом JSON

    - GET /tarrifs/list получение списка тарифов
    - PATCH /tarrifs обновление данных тарифа
    - DELETE /tarrifs удаление тарифа

    Расчет стоимости:
    - POST /insurance/calculate

Реализованы unit-тесты для основного функционала.

#### Стек технологий:
- Python3.11
- PostgreSQL - СУБД
- ORM - SQLAlchemy
- FastAPI - API
- Kafka - логирование через батч
- Docker

#### Запуск приложения

- Копируем код приложения в Вашу директорию.

`git clone https://github.com/KIchkinevVladislav/insurance_cals_test`

- Запускаем контейнеры

`docker compose up -d`

- Применяем миграции

`docker compose exec mcals_app alembic upgrade head`

Приложение готово для тестирования:

http://127.0.0.1:8000/docs

#### Запуск тестов

`docker compose exec cals_app python -m unittest`
