# Auto Repair Telegram Bot

Готовый к продакшену бэкенд для автосервисов, позволяющий механикам отправлять голосовые или текстовые заметки Telegram-боту, который автоматически:
1. Распознает речь (Whisper)
2. Извлекает структурированную информацию (GPT-4o Structured Outputs)
3. Сопоставляет работы и запчасти с базой данных сервиса
4. Рассчитывает стоимость работ и наценку на запчасти
5. Формирует PDF-смету (WeasyPrint) и отправляет обратно в чат для подтверждения

## Настройка проекта

1. **Клонирование и установка зависимостей**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Переменные окружения**
   Скопируйте `.env.example` в `.env` и заполните ваши доступы (PostgreSQL, Telegram Bot Token, OpenAI API Key).

3. **База данных**
   Убедитесь, что у вас установлен и запущен локальный сервер PostgreSQL. После настройки `DATABASE_URL` в `.env`, вы можете заполнить базу начальными данными:
   ```bash
   python docker/seed.py
   ```
   *(Не забудьте поменять `telegram_id` в seed-скрипте на свой реальный Telegram ID)*

## Запуск

### Локально
```bash
uvicorn app.main:app --reload
```
Далее необходимо настроить Webhook в Telegram на ваш локальный URL (например, через `ngrok`).

### Развертывание (Google Cloud Run)
Проект содержит готовый `Dockerfile` с установленными зависимостями для генерации PDF (WeasyPrint).
```bash
# Билд и деплой
gcloud builds submit --tag gcr.io/YOUR_PROJECT/auto_repair_bot
gcloud run deploy auto-repair-bot --image gcr.io/YOUR_PROJECT/auto_repair_bot --platform managed
```
После успешного деплоя, зарегистрируйте Webhook в Telegram, указав ваш Cloud Run URL:
`https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook?url=https://<CLOUD_RUN_URL>/webhook/<YOUR_TOKEN>`

## Структура проекта
- `app/api/endpoints/` — контроллеры (Webhook и Admin REST API).
- `app/services/` — стержневая логика (ИИ экстракция, ценообразование, нормализация, генерация PDF, отправка в Telegram).
- `app/models/` — ORM схемы SQLAlchemy.
- `app/schemas/` — Pydantic модели.
- `app/templates/` — HTML шаблоны для PDF.
