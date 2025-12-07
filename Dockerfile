# Используем легкий официальный образ Python
FROM python:3.12-slim

# Отключаем создание .pyc файлов и буферизацию вывода (чтобы логи шли сразу)
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /app

WORKDIR /app

# Сначала копируем зависимости (для кэширования слоев Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальной код
COPY . .

# Команда по умолчанию (переопределяется в docker-compose)
CMD ["python", "src/main.py"]