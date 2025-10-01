from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./tasas.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

class Base(DeclarativeBase):
    pass

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def init_db():
    """init_db / Inicializar base de datos

    Crea todas las tablas definidas en los modelos si no existen.
    Creates all tables defined in models if they do not exist.

    Returns:
        None
    """
    Base.metadata.create_all(bind=engine)

def get_db():
    """get_db / Obtener sesión de base de datos

    Generador que retorna una sesión de base de datos y la cierra al finalizar.
    Generator that yields a database session and closes it after use.

    Returns:
        SessionLocal: Sesión de base de datos / Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
