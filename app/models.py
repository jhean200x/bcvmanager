from sqlalchemy import Column, Integer, String, DateTime, Numeric
from database import Base  
import datetime

class Tasa(Base):
    """Tasa / Exchange Rate

    Modelo para almacenar tasas de cambio.
    Model to store exchange rates.
    """
    __tablename__ = "tasas"
    id = Column(Integer, primary_key=True, index=True)
    currency = Column(String, index=True)
    value = Column(Numeric(20, 8))  # Ahora Numeric para máxima precisión
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class UsdtCache(Base):
    """UsdtCache / USDT Cache

    Modelo para almacenar el valor de USDT en caché.
    Model to store cached USDT value.
    """
    __tablename__ = "usdt_cache"
    id = Column(Integer, primary_key=True, index=True)
    value = Column(Numeric(20, 8))  # Ahora Numeric para máxima precisión
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
