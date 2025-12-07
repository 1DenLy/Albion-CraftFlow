FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /app

WORKDIR /app

# Створюємо системного користувача 'appuser'
RUN adduser --system --no-create-home appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Змінюємо власника файлів (щоб appuser міг читати/писати якщо треба)
RUN chown -R appuser:nogroup /app

# Перемикаємось на користувача
USER appuser

CMD ["python", "src/main.py"]