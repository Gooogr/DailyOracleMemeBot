FROM python:3.10-slim

# Ensure output is immediately flushed to the terminal
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

COPY ./docker/telegram_bot/requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY ../.. .

CMD ["python", "app/main.py"]