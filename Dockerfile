# Usamos una versión moderna (3.10 o 3.11)
FROM python:3.10-slim

# Directorio de trabajo
WORKDIR /app

# Optimizaciones de Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# --- PASO CRITICO: Instalar dependencias para Postgres ---
# Sin esto, es probable que la instalación falle
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiamos primero requirements para aprovechar la caché de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código
COPY . .

# Exponemos el puerto
EXPOSE 8000

# Comando de arranque
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "settings.wsgi:application"]