# Użyj oficjalnego, lekkiego obrazu Python
FROM python:3.11-slim

# Ustaw katalog roboczy wewnątrz kontenera
WORKDIR /app

# Skopiuj plik z zależnościami
COPY ./requirements.txt /app/requirements.txt

# Zainstaluj zależności
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Skopiuj resztę kodu aplikacji do kontenera
COPY ./app /app/app

# Ustaw domyślną komendę
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]