import pytest
import os
import json
from unittest.mock import patch, AsyncMock, MagicMock, mock_open
from sqlalchemy import select

# Импортируем тестируемую функцию
from src.scripts.seed_tracking import seed_tracking_data

# Мок данные для тестов
MOCK_RESOURCES_JSON = '["T4_ORE", "T4_WOOD"]'
MOCK_LOCATIONS_IDS = [1, 2, 3]  # Предположим, у нас 3 города
MOCK_ITEMS_DATA = [
    (101, "T4_ORE"),
    (102, "T4_WOOD")
]


@pytest.mark.asyncio
async def test_seed_tracking_file_not_found():
    """
    Тест 1: Проверка поведения, если файл resources.json отсутствует.
    Ожидание: Лог ошибки и выход из функции без обращений к БД.
    """
    with patch("src.scripts.seed_tracking.os.path.exists", return_value=False) as mock_exists:
        with patch("src.scripts.seed_tracking.logger") as mock_logger:
            await seed_tracking_data()

            mock_exists.assert_called_once()
            mock_logger.error.assert_called_with("File resources.json not found. Run generate_resources_json.py first.")


@pytest.mark.asyncio
async def test_seed_tracking_no_locations_in_db():
    """
    Тест 2: Проверка, если в базе нет локаций (городов).
    Ожидание: Лог ошибки, так как нельзя создать связки без городов.
    """
    # 1. Мокаем существование файла и открытие
    with patch("src.scripts.seed_tracking.os.path.exists", return_value=True), \
            patch("builtins.open", mock_open(read_data=MOCK_RESOURCES_JSON)):
        # 2. Мокаем сессию БД
        mock_session = AsyncMock()
        # Настройка результата для locations: пустой список
        mock_session.execute.return_value.scalars.return_value.all.return_value = []

        with patch("src.scripts.seed_tracking.async_session_maker") as mock_maker:
            mock_maker.return_value.__aenter__.return_value = mock_session
            with patch("src.scripts.seed_tracking.logger") as mock_logger:
                await seed_tracking_data()

                # Проверяем, что пытались получить локации
                assert mock_session.execute.call_count >= 1
                mock_logger.error.assert_called_with("No locations found in DB. Run seed_db.py first!")


@pytest.mark.asyncio
async def test_seed_tracking_items_not_found_in_db():
    """
    Тест 3: JSON есть, локации есть, но указанных в JSON предметов нет в таблице items.
    Ожидание: Лог предупреждения и завершение.
    """
    with patch("src.scripts.seed_tracking.os.path.exists", return_value=True), \
            patch("builtins.open", mock_open(read_data=MOCK_RESOURCES_JSON)):
        mock_session = AsyncMock()
        # 1-й вызов execute (locations) -> возвращает [1, 2, 3]
        # 2-й вызов execute (items) -> возвращает пустой список []
        mock_session.execute.side_effect = [
            MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=MOCK_LOCATIONS_IDS)))),
            MagicMock(all=MagicMock(return_value=[]))
        ]

        with patch("src.scripts.seed_tracking.async_session_maker") as mock_maker:
            mock_maker.return_value.__aenter__.return_value = mock_session
            with patch("src.scripts.seed_tracking.logger") as mock_logger:
                await seed_tracking_data()

                mock_logger.warning.assert_called()
                assert "No matching items found" in mock_logger.warning.call_args[0][0]


@pytest.mark.asyncio
async def test_seed_tracking_success():
    """
    Тест 4: Успешный сценарий.
    Есть файл, есть локации (3 шт), есть предметы (2 шт).
    Ожидание: Должно быть сформировано 6 записей (2 предмета * 3 города) и вызван insert.
    """
    with patch("src.scripts.seed_tracking.os.path.exists", return_value=True), \
            patch("builtins.open", mock_open(read_data=MOCK_RESOURCES_JSON)):
        mock_session = AsyncMock()

        # Настраиваем side_effect для mock_session.execute
        # 1. Запрос локаций
        mock_locations_result = MagicMock()
        mock_locations_result.scalars.return_value.all.return_value = MOCK_LOCATIONS_IDS

        # 2. Запрос предметов
        mock_items_result = MagicMock()
        # .all() возвращает список кортежей (id, unique_name)
        mock_items_result.all.return_value = MOCK_ITEMS_DATA

        # 3. Insert (Result не важен)
        mock_insert_result = MagicMock()

        mock_session.execute.side_effect = [
            mock_locations_result,
            mock_items_result,
            mock_insert_result
        ]

        with patch("src.scripts.seed_tracking.async_session_maker") as mock_maker:
            mock_maker.return_value.__aenter__.return_value = mock_session
            with patch("src.scripts.seed_tracking.logger") as mock_logger:
                await seed_tracking_data()

                # Проверки
                assert mock_session.commit.called
                mock_logger.info.assert_any_call("Tracking seeding completed successfully.")

                # Проверяем логику комбинаторики:
                # 2 предмета * 3 города = 6 записей
                # Мы не можем легко проверить аргументы insert() из-за сложной структуры SQLAlchemy statement,
                # но мы можем проверить лог, где пишется кол-во подготовленных записей.
                mock_logger.info.assert_any_call("Prepared 6 tracking entries (Items * Locations).")