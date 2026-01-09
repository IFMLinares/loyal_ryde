FROM python:3.10-slim
ENV PYTHONUNBUFFERED=1

WORKDIR /code

# Instala dependencias del sistema para GDAL
RUN apt-get update && \
    apt-get install -y binutils libproj-dev gdal-bin libgdal-dev && \
    apt-get clean
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

COPY requirements.txt .

RUN python -m pip install --upgrade pip 
RUN python -m pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "settings.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--log-level", "debug"]