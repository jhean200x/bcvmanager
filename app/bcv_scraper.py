import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from database import SessionLocal
from models import Tasa, UsdtCache
import warnings
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from decimal import Decimal

warnings.filterwarnings('ignore')

def obtener_tasas_bcv():
    """obtener_tasas_bcv / Get BCV rates

    Scrapea las tasas del BCV y devuelve un diccionario limpio.
    Scrapes BCV rates and returns a clean dictionary.

    Returns:
        dict | None -- Diccionario de tasas o None si falla / Rates dict or None if fails
    """
    try:
        url = "https://www.bcv.org.ve/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        tasas = {}
        
        # Dólar
        dolar_div = soup.find('div', id='dolar')
        if dolar_div:
            dolar_text = dolar_div.find('strong').text.strip()
            tasas['USD'] = float(dolar_text.replace(',', '.'))
        
        # Euro
        euro_div = soup.find('div', id='euro')
        if euro_div:
            euro_text = euro_div.find('strong').text.strip()
            tasas['EUR'] = float(euro_text.replace(',', '.'))
        
        # Yuan
        yuan_div = soup.find('div', id='yuan')
        if yuan_div:
            yuan_text = yuan_div.find('strong').text.strip()
            tasas['CNY'] = float(yuan_text.replace(',', '.'))
        
        # Rublo
        rublo_div = soup.find('div', id='rublo')
        if rublo_div:
            rublo_text = rublo_div.find('strong').text.strip()
            tasas['RUB'] = float(rublo_text.replace(',', '.'))
        
        # Lira
        lira_div = soup.find('div', id='lira')
        if lira_div:
            lira_text = lira_div.find('strong').text.strip()
            tasas['TRY'] = float(lira_text.replace(',', '.'))
        
        return tasas
    except Exception as e:
        print(f"Error: {e}")
        return None

def obtener_precio_usdt():
    """obtener_precio_usdt / Get USDT price

    Obtiene el precio USDT/VES desde Binance P2P con Selenium y caché de 5 minutos en SQLite.
    Gets the USDT/VES price from Binance P2P using Selenium and 5-minute cache in SQLite.

    Returns:
        Decimal | None -- Precio USDT/VES o None si falla / USDT/VES price or None if fails
    """
    db = SessionLocal()
    now = datetime.now()
    cache = db.query(UsdtCache).order_by(UsdtCache.timestamp.desc()).first()

    # Verifica que la caché sea válida (menos de 5 minutos)
    if cache and cache.timestamp and (now - cache.timestamp) < timedelta(minutes=5):
        db.close()
        # Devuelve el valor tal cual está en la base de datos (Decimal)
        return cache.value

    precio = None
    driver = None
    try:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--window-size=1920,1080')
        driver = webdriver.Chrome(options=options)
        url = "https://p2p.binance.com/es/express/buy/USDT/VES"
        driver.get(url)
        driver.implicitly_wait(10)
        elementos = driver.find_elements(By.CSS_SELECTOR, ".noMob\\:text-secondaryText")
        for elemento in elementos:
            texto = elemento.text
            import re
            match = re.search(r'≈\s*([\d.,]+)', texto)
            if match:
                valor = match.group(1)
                # Detecta formato: si tiene punto y coma, o solo coma, o solo punto
                if ',' in valor and '.' in valor:
                    valor = valor.replace('.', '').replace(',', '.')
                elif ',' in valor:
                    valor = valor.replace(',', '.')
                try:
                    precio = Decimal(valor)
                    break
                except Exception:
                    continue
        driver.quit()
    except Exception:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass
        precio = None

    if precio is not None:
        try:
            db.add(UsdtCache(value=precio, timestamp=now))
            db.commit()
        except Exception:
            pass

    db.close()
    # Devuelve el valor como Decimal para máxima precisión
    return precio

def obtener_tasas_bcv_cache():
    """obtener_tasas_bcv_cache / Get BCV rates with cache

    Igual que obtener_tasas_bcv pero con caché de 15 minutos (usando SQLite y guardando el promedio).
    Same as obtener_tasas_bcv but with 15-minute cache (using SQLite and saving the average).

    Returns:
        dict | None -- Diccionario de tasas o None si falla / Rates dict or None if fails
    """
    db = SessionLocal()
    now = datetime.now()
    tasa_reciente = db.query(Tasa).order_by(Tasa.timestamp.desc()).first()
    
    if tasa_reciente and (now - tasa_reciente.timestamp) < timedelta(minutes=15):
        tasas_db = db.query(Tasa).filter(Tasa.timestamp == tasa_reciente.timestamp).all()
        tasas = {t.currency: t.value for t in tasas_db}
        db.close()
        return tasas
    
    tasas = obtener_tasas_bcv()
    usdt = None
    
    try:
        usdt = obtener_precio_usdt()
    except Exception:
        pass
    
    if tasas and usdt:
        promedio = (tasas.get("USD", 0) + usdt) / 2 if tasas.get("USD") and usdt else None
        if promedio:
            tasas["PROMEDIO"] = round(promedio, 2)
        
        timestamp = now
        for k, v in tasas.items():
            db.add(Tasa(currency=k, value=v, timestamp=timestamp))
        db.commit()
    
    db.close()
    return tasas