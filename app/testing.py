import sys
from database import init_db, SessionLocal
from models import Tasa, UsdtCache
import bcv_scraper

def test_scraping():
    """Prueba el scraping directo del BCV. / Test direct BCV scraping."""
    print("\n--- Scraping BCV --- / --- BCV Scraping ---")
    tasas = bcv_scraper.obtener_tasas_bcv()
    print("Tasas obtenidas / Rates obtained:", tasas)

def test_usdt():
    """Prueba la obtención del precio USDT/VES. / Test USDT/VES price retrieval."""
    print("\n--- Precio USDT/VES --- / --- USDT/VES Price ---")
    usdt = bcv_scraper.obtener_precio_usdt()
    print("USDT/VES:", usdt)

def test_cache():
    """Prueba la función de caché de tasas. / Test rates cache function."""
    print("\n--- Tasas con caché --- / --- Rates with cache ---")
    tasas = bcv_scraper.obtener_tasas_bcv_cache()
    print("Tasas (con caché) / Rates (with cache):", tasas)

def test_db():
    """Prueba la conexión y muestra los últimos registros de la base de datos. / Test DB connection and show last records."""
    print("\n--- Últimos registros en la base de datos --- / --- Last records in database ---")
    db = SessionLocal()
    tasas = db.query(Tasa).order_by(Tasa.timestamp.desc()).limit(5).all()
    for t in tasas:
        print(f"{t.timestamp} | {t.currency}: {t.value}")
    usdt = db.query(UsdtCache).order_by(UsdtCache.timestamp.desc()).limit(3).all()
    for u in usdt:
        print(f"USDT Cache {u.timestamp}: {u.value}")
    db.close()

def init_database():
    """Inicializa la base de datos. / Initialize the database."""
    print("\n--- Inicializando base de datos --- / --- Initializing database ---")
    init_db()
    print("Base de datos inicializada. / Database initialized.")

def reset_database():
    """Resetea base de datos. / Reset database    """
    db = SessionLocal()
    db.query(Tasa).delete()
    db.query(UsdtCache).delete()
    db.commit()
    db.close()

def menu():
    while True:
        print("\n=== PANEL DE TESTING BCV MANAGER ===")
        print("=== BCV MANAGER TESTING PANEL ===")
        print("1. Probar scraping BCV / Test BCV scraping")
        print("2. Probar precio USDT/VES / Test USDT/VES price")
        print("3. Probar tasas con caché / Test rates with cache")
        print("4. Probar conexión y registros de la base de datos / Test DB connection and records")
        print("5. Inicializar base de datos / Initialize database")
        print("6. Resetear base de datos / Reset database")
        print("0. Salir / Exit")
        opcion = input("Seleccione una opción / Select an option: ").strip()
        if opcion == "1":
            test_scraping()
        elif opcion == "2":
            test_usdt()
        elif opcion == "3":
            test_cache()
        elif opcion == "4":
            test_db()
        elif opcion == "5":
            init_database()
        elif opcion == "6":
            reset_database()
        elif opcion == "0":
            print("Saliendo... / Exiting...")
            sys.exit(0)
        else:
            print("Opción no válida. / Invalid option.")

if __name__ == "__main__":
    menu()
