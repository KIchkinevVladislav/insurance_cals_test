from sqlalchemy import Column, Date, DateTime, ForeignKey, String, Float, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base


class TariffDate(Base):
    __tablename__ = "tariff_dates"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, nullable=False)

    tariffs = relationship("Tariff", back_populates="tariff_date", cascade="all, delete-orphan")


class Tariff(Base):
    __tablename__ = "tariffs"

    id = Column(Integer, primary_key=True, index=True)
    cargo_type = Column(String, nullable=False)
    rate = Column(Float, nullable=False)
    date_id = Column(Integer, ForeignKey("tariff_dates.id", ondelete="CASCADE"), nullable=False)

    tariff_date = relationship("TariffDate", back_populates="tariffs")


class CalculationResult(Base):
    __tablename__ = "calculation_results"

    id = Column(Integer, primary_key=True, index=True)
    date_calculation = Column(DateTime, nullable=False, default=func.now())
    cargo_type = Column(String, nullable=False)
    initial_cost = Column(Float, nullable=False)
    rate = Column(Float, nullable=False)
    calculated_cost = Column(Float, nullable=False)
