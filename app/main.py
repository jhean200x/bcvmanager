from fastapi import FastAPI, HTTPException, status, Request, Depends
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
import bcv_scraper as bcv
from database import init_db, SessionLocal, get_db
from models import Tasa, UsdtCache
from datetime import datetime, timedelta

init_db()

# Inicialización de la aplicación FastAPI
app = FastAPI(
    title="BCV Tasa Scraper API",
    description="API para obtener las tasas de cambio del Banco Central de Venezuela (BCV)."
)

# Montaje de archivos estáticos
# Configura el directorio 'static' para servir archivos como CSS, JS o imágenes.
# Se accede a estos archivos mediante la ruta '/static'.
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configuración del motor de plantillas Jinja2
# Inicializa el motor de plantillas para renderizar archivos HTML.
# Busca archivos de plantilla dentro del directorio 'templates'.
templates = Jinja2Templates(directory="templates")


# ==================================================================
# RUTA 1: RUTA PRINCIPAL (FRONTEND)
# ==================================================================
@app.get(
    "/", 
    response_class=HTMLResponse, 
    status_code=status.HTTP_200_OK,
    summary="Página de inicio que muestra las tasas de cambio.",
    description="Renderiza el archivo 'index.html' e inyecta las tasas de cambio obtenidas del BCV."
)
async def home(request: Request, db: Session = Depends(get_db)):
    """
    Función de vista principal que:
    1. Obtiene las tasas de cambio del BCV usando el módulo 'bcv_scraper'.
    2. Renderiza la plantilla 'index.html' con los datos obtenidos.
    
    Args:
        request (Request): El objeto de solicitud HTTP, requerido por Jinja2.
        db (Session): Sesión de base de datos inyectada por FastAPI.

    Returns:
        TemplateResponse: La página HTML renderizada con las tasas de cambio.
    """
    now = datetime.now()
    tasa_reciente = db.query(Tasa).order_by(Tasa.timestamp.desc()).first()
    usdt = None
    rates = {}
    if tasa_reciente and (now - tasa_reciente.timestamp) < timedelta(minutes=20):
        tasas_db = db.query(Tasa).filter(Tasa.timestamp == tasa_reciente.timestamp).all()
        rates = {t.currency: t.value for t in tasas_db}
        # Buscar USDT en la tabla UsdtCache (no llamar a la función de scraping)
        usdt_cache = db.query(UsdtCache).order_by(UsdtCache.timestamp.desc()).first()
        if usdt_cache and (now - usdt_cache.timestamp) < timedelta(minutes=20):
            rates["USDT"] = usdt_cache.value
        # Siempre intenta obtener el valor de USDT del diccionario rates
        usdt = rates.get("USDT")
        print(f"1 {usdt}")
        if usdt is not None:
            try:
                usdt = float(usdt)
            except Exception:
                usdt = None
        usd = rates.get("USD")
        if usd is not None and usdt is not None:
            rates["PROMEDIO"] = round((float(usd) + float(usdt)) / 2, 2)
    else:
        rates = bcv.obtener_tasas_bcv()
        usdt = bcv.obtener_precio_usdt()
        print(f"2 {usdt}")
        if rates and usdt:
            rates["USDT"] = usdt
            usd = rates.get("USD")
            if usd is not None:
                rates["PROMEDIO"] = round((float(usd) + float(usdt)) / 2, 2)
            timestamp = now
            for k, v in rates.items():
                db.add(Tasa(currency=k, value=v, timestamp=timestamp))
            db.commit()
        else:
            rates = {}
    # Mostrar el precio real de usdt si existe, si no, "cargando..."
    print(rates)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "rates": rates,
            "usdt": usdt
        }
    )

# ------------------------------------------------------------------
# RUTA 2: ENDPOINT API (BACKEND)
# ------------------------------------------------------------------
@app.get(
    "/api/tasas", 
    response_class=JSONResponse, 
    status_code=status.HTTP_200_OK,
    summary="Endpoint API para obtener datos JSON de las tasas y USDT.",
    description="Devuelve las tasas y el valor USDT más reciente desde la base de datos o scraping si es necesario."
)
async def obtener_tasas_y_usdt(db: Session = Depends(get_db)):
    """
    Obtiene las tasas y el valor USDT más reciente desde la base de datos (si es reciente) o hace scraping si es necesario.
    Returns rates and the most recent USDT value from the database or scraping if needed.
    """
    try:
        now = datetime.now()
        tasa_reciente = db.query(Tasa).order_by(Tasa.timestamp.desc()).first()
        tasas = {}
        usdt = None
        if tasa_reciente and (now - tasa_reciente.timestamp) < timedelta(minutes=20):
            tasas_db = db.query(Tasa).filter(Tasa.timestamp == tasa_reciente.timestamp).all()
            tasas = {t.currency: t.value for t in tasas_db}
            usdt_cache = db.query(UsdtCache).order_by(UsdtCache.timestamp.desc()).first()
            if usdt_cache and (now - usdt_cache.timestamp) < timedelta(minutes=20):
                tasas["USDT"] = usdt_cache.value
                usdt = float(usdt_cache.value)
            else:
                usdt = tasas.get("USDT")
                if usdt is not None:
                    usdt = float(usdt)
            usd = tasas.get("USD")
            if usd is not None and usdt is not None:
                tasas["PROMEDIO"] = round((float(usd) + float(usdt)) / 2, 2)
        else:
            tasas = bcv.obtener_tasas_bcv()
            usdt = bcv.obtener_precio_usdt()
            if tasas and usdt:
                tasas["USDT"] = usdt
                usd = tasas.get("USD")
                if usd is not None:
                    tasas["PROMEDIO"] = round((float(usd) + float(usdt)) / 2, 2)
                timestamp = now
                for k, v in tasas.items():
                    db.add(Tasa(currency=k, value=v, timestamp=timestamp))
                db.commit()
            else:
                tasas = {}
            if "USDT" in tasas and tasas["USDT"] is not None:
                try:
                    usdt = float(tasas["USDT"])
                except Exception:
                    usdt = None
            else:
                usdt = None
        # Si no hay valor de usdt, mostrar "cargando..."
        if usdt is None:
            usdt = "cargando..."
        return {"tasas": tasas, "usdt": usdt}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener tasas: {str(e)}"
        )
    finally:
        db.close()

@app.get("/usdt", response_class=JSONResponse)
async def obtener_usdt(db: Session = Depends(get_db)):
    """
    Devuelve el valor más reciente de USDT desde la base de datos.
    Returns the most recent USDT value from the database.
    """
    now = datetime.now()
    usdt_cache = db.query(UsdtCache).order_by(UsdtCache.timestamp.desc()).first()
    if usdt_cache and (now - usdt_cache.timestamp) < timedelta(minutes=20):
        return {"usdt": float(usdt_cache.value)}
    else:
        return {"usdt": "cargando..."}

