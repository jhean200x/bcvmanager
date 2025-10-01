from pydantic import BaseModel
from datetime import datetime

class TasaBase(BaseModel):
    """TasaBase / Exchange Rate Base

    Esquema base para tasas de cambio.
    Base schema for exchange rates.
    """
    currency: str
    value: float
    timestamp: datetime

class TasaCreate(TasaBase):
    """TasaCreate / Create Exchange Rate

    Esquema para crear una tasa de cambio.
    Schema to create an exchange rate.
    """
    pass

class TasaOut(TasaBase):
    """TasaOut / Output Exchange Rate

    Esquema de salida para tasas de cambio.
    Output schema for exchange rates.
    """
    id: int
    class Config:
        orm_mode = True

class UsdtCacheBase(BaseModel):
    """UsdtCacheBase / USDT Cache Base

    Esquema base para caché de USDT.
    Base schema for USDT cache.
    """
    value: float
    timestamp: datetime

class UsdtCacheOut(UsdtCacheBase):
    """UsdtCacheOut / Output USDT Cache

    Esquema de salida para caché de USDT.
    Output schema for USDT cache.
    """
    id: int
    class Config:
        orm_mode = True

