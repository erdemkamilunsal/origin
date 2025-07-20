FROM python:3.11-slim

# Ortam değişkenleri
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Çalışma dizini
WORKDIR /app

# Gereken dosyaları kopyala
COPY . .

# Bağımlılıkları kur
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Gunicorn ile başlat
CMD ["gunicorn", "project.wsgi:application", "--bind", "0.0.0.0:8000"]
