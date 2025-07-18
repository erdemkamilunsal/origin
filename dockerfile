# Temel python imajı
FROM python:3.11-slim

# Çalışma dizinini ayarla
WORKDIR /app

# Gereksinimleri kopyala ve yükle
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Proje dosyalarını kopyala
COPY . .

# Django için gerekli port
ENV PORT 8080

# Uygulamayı çalıştır
CMD ["gunicorn", "project.wsgi:project", "--bind", "0.0.0.0:8080"]
