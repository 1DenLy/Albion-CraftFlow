import os
import sys
import pytest


sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("DB_USER", "test_user")
os.environ.setdefault("DB_PASS", "test_password")
os.environ.setdefault("DB_NAME", "test_db")
os.environ.setdefault("ECHO_SQL", "False")  # Если есть в конфиге

@pytest.fixture(scope="session")
def event_loop():
    """
    Create an event loop instance for asynchronous tests.
    Required for pytest-asyncio.
    """
    import asyncio
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()