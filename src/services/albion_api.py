from typing import List, Optional
from enum import Enum


# Используем Enum, чтобы не допускать опечаток в названиях серверов
class AlbionServer(Enum):
    WEST = "West"
    EAST = "East"
    EUROPE = "Europe"


class AlbionUrlBuilder:
    """
    Строитель URL для запросов к Albion Online Data Project.
    Документация API: https://www.albion-online-data.com/api/swagger/index.html
    """

    BASE_URL = "https://west.albion-online-data.com/api/v2/stats/prices"

    def __init__(self, server: AlbionServer = AlbionServer.EUROPE):
        self.server = server
        # Базовый URL может меняться в зависимости от региона,
        # но обычно у них единый эндпоинт, где сервер передается параметром?
        # В текущей версии API v2 часто используют разные домены или просто фильтруют данные.
        # Для надежности будем использовать стандартный v2 endpoint и уточнять, если потребуется.
        # Примечание: У Albion Data API странная маршрутизация, часто используют просто:
        # https://www.albion-online-data.com/api/v2/stats/prices/...
        self._base = "https://www.albion-online-data.com/api/v2/stats/prices"

    def build_prices_url(
            self,
            item_ids: List[str],
            locations: Optional[List[str]] = None,
            qualities: Optional[List[int]] = None
    ) -> str:
        """
        Генерирует URL для получения цен.

        :param item_ids: Список ID предметов ['T4_BAG', 'T5_BAG']
        :param locations: Список городов ['Martlock', 'Caerleon'] (Опционально)
        :param qualities: Список качества [1, 2] (Опционально)
        :return: Готовая строка URL
        """
        if not item_ids:
            raise ValueError("Список item_ids не может быть пустым")

        # 1. Склеиваем предметы через запятую (T4_BAG,T5_BAG)
        # Важно: API не любит пробелы, делаем strip()
        items_str = ",".join([i.strip() for i in item_ids])

        url = f"{self._base}/{items_str}"

        # 2. Собираем Query Parameters
        params = []

        # Добавляем локации
        if locations:
            loc_str = ",".join([l.strip() for l in locations])
            params.append(f"locations={loc_str}")

        # Добавляем качество
        if qualities:
            qual_str = ",".join([str(q) for q in qualities])
            params.append(f"qualities={qual_str}")

        # 3. Финализация строки запроса
        if params:
            url += "?" + "&".join(params)

        return url


# --- ПРИМЕР ИСПОЛЬЗОВАНИЯ (можно запустить и проверить) ---
if __name__ == "__main__":
    builder = AlbionUrlBuilder(server=AlbionServer.EUROPE)

    # Сценарий: Хотим узнать цены на Сумки Т4 и Т5 в Мартлоке, качество Обычное и Отличное
    my_items = ["T4_BAG", "T5_BAG", "T8_HRIDE_HORSE"]
    my_cities = ["Martlock", "Bridgewatch"]
    my_qualities = [1, 2]  # 1=Normal, 2=Good

    try:
        url = builder.build_prices_url(
            item_ids=my_items,
            locations=my_cities,
            qualities=my_qualities
        )
        print(f"Generated URL: {url}")
        # Результат будет:
        # https://www.albion-online-data.com/api/v2/stats/prices/T4_BAG,T5_BAG,T8_HRIDE_HORSE?locations=Martlock,Bridgewatch&qualities=1,2
    except ValueError as e:
        print(f"Error: {e}")