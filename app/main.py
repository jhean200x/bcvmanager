from fastapi import FastAPI, HTTPException, status, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
import bcv_scraper as bcv

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
async def home(request: Request):
    """
    Función de vista principal que:
    1. Obtiene las tasas de cambio del BCV usando el módulo 'bcv_scraper'.
    2. Renderiza la plantilla 'index.html' con los datos obtenidos.
    
    Args:
        request (Request): El objeto de solicitud HTTP, requerido por Jinja2.

    Returns:
        TemplateResponse: La página HTML renderizada con las tasas de cambio.
    """
    # Llama a la función del módulo externo para obtener los datos de las divisas.
    currency_rates = bcv.obtener_tasas_bcv()
    
    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={
            "request": request,
            # 'rates' contendrá las tasas (ej: USD, EUR, etc.) para la plantilla.
            "rates": currency_rates 
        }
    )

# ------------------------------------------------------------------
# RUTA 2: ENDPOINT API (BACKEND)
# ------------------------------------------------------------------
@app.get(
    "/api/tasas", 
    response_class=JSONResponse, 
    status_code=status.HTTP_200_OK,
    summary="Endpoint API para obtener solo datos JSON de las tasas.",
    description="Utilizado típicamente por JavaScript (fetch) para actualizar las tasas sin recargar la página completa."
)
async def obtener_tasas_api():
    """
    Función que es llamada por el frontend (ej. con 'fetch' o Axios) para obtener 
    los últimos datos del BCV en formato JSON.
    
    Esto permite actualizar las tasas en la página sin una recarga completa,
    mejorando la experiencia del usuario.

    Returns:
        JSONResponse: Un diccionario con las tasas de cambio y sus valores.
    
    Raises:
        HTTPException: Lanza un error 500 si el scraper falla al obtener los datos.
    """
    try:
        # Llama a la función para obtener los datos del scraper.
        currency_rates = bcv.obtener_tasas_bcv()
        return currency_rates # FastAPI convierte automáticamente el diccionario a JSON.
    except Exception as e:
        # En caso de cualquier error durante el scraping (ej. fallo de red, cambio en la web del BCV)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener tasas: {str(e)}"
        )