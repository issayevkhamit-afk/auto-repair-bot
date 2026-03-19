FROM python:3.10-slim

WORKDIR /app

# Устанавливаем системные зависимости, в том числе для WeasyPrint (PDF генератор)
RUN apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libjpeg-dev \
    libopenjp2-7-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Применяем миграции БД и запускаем сервер
CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT