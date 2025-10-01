# ===============================================
# STAGE 1: BUILDER - Instalación de dependencias
# Usa una imagen base con herramientas de compilación
# ===============================================
FROM python:3.11-slim as builder

# Define el directorio de trabajo dentro del contenedor
WORKDIR /app

# Establece variables de entorno para optimizar pip
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Copia solo el archivo de requerimientos para aprovechar el caché
# Esto solo se ejecuta si requirements.txt cambia, acelerando builds
COPY requirements.txt .

# Instala las dependencias
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# ===============================================
# STAGE 2: FINAL - Imagen de Producción Ligera
# Usa una imagen base mínima sin herramientas de compilación
# ===============================================
FROM python:3.11-slim

# Define el directorio de trabajo
WORKDIR /app

# Copia las dependencias instaladas del stage 'builder'
# Esto evita tener que instalar dependencias de nuevo, ahorrando tiempo y espacio
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copia el código de la aplicación (incluyendo main.py, templates y static)
# Esta debe ser la última capa que se invalida
COPY . .

# Expone el puerto por defecto de uvicorn
EXPOSE 8000

# Comando de inicio para ejecutar la aplicación con Uvicorn.
# Usamos el modo de producción (--host 0.0.0.0 y sin --reload)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]