import uvicorn
from fastapi import FastAPI

from app.api.insurance_routers import insurance_routers
from app.api.tariff_routers import tariff_routers

app = FastAPI()

app.include_router(tariff_routers, prefix="/tariffs", tags=["tariffs"])
app.include_router(insurance_routers, prefix="/insurance", tags=["insurance"])


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
