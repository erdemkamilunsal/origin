FROM python:3.11-slim

COPY .env .env


ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# Migrate & collectstatic (isteğe bağlı ama önerilir)
RUN python manage.py collectstatic --noinput
# RUN python manage.py migrate

ENV PORT=8080
CMD ["gunicorn", "project.wsgi:application", "--bind", "0.0.0.0:8080"]

