import os
import sys
import pytest

# 1. Хак для путей (чтобы видеть src)
# Добавляем текущую директорию в sys.path, чтобы импорты src.x работали корректно
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# 2. Устанавливаем фейковые переменные окружения
# ВАЖНО: Делаем это на уровне модуля, до объявления фикстур,
# чтобы они применились до того, как Pytest начнет импортировать твои файлы тестов.
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("DB_USER", "test_user")
os.environ.setdefault("DB_PASS", "test_password")
os.environ.setdefault("DB_NAME", "test_db")
os.environ.setdefault("ECHO_SQL", "False")  # Если есть в конфиге

@pytest.fixture(scope="session")
def event_loop():
    """
    Создаем экземпляр event loop для асинхронных тестов.
    Нужно для pytest-asyncio.
    """
    import asyncio
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()