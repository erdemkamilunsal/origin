FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /app/

ENV PORT 8080

CMD ["gunicorn", "project.wsgi:application", "--bind", "0.0.0.0:8080"]
