from typing import List, Dict, Any
from datetime import datetime, timezone
from src.ingesting.schemas import AlbionPriceDTO


class PriceProcessor:
    def process(self, raw_data: List[AlbionPriceDTO]) -> List[Dict[str, Any]]:
        """
        Готовит словари для сохранения в таблицу MarketPrice.
        Возвращает: prices_for_upsert
        """
        prices_to_save = []
        now = datetime.now(timezone.utc)

        for dto in raw_data:
            # Если все цены по нулям — запись бесполезна, пропускаем
            if (dto.sell_price_min == 0 and dto.sell_price_max == 0 and
                    dto.buy_price_min == 0 and dto.buy_price_max == 0):
                continue

            # Подготовка данных для MarketPrice
            price_entry = {
                "item_id": dto.item_id,  # (str) T4_BAG -> будет преобразовано в int в Repo
                "location_id": dto.city,  # (str) Location Name -> будет заменено на ID
                "quality_level": dto.quality,

                # Sell Data
                "sell_price_min": dto.sell_price_min,
                "sell_price_min_date": dto.sell_price_min_date,
                "sell_price_max": dto.sell_price_max,
                "sell_price_max_date": dto.sell_price_max_date,

                # Buy Data
                "buy_price_min": dto.buy_price_min,
                "buy_price_min_date": dto.buy_price_min_date,
                "buy_price_max": dto.buy_price_max,
                "buy_price_max_date": dto.buy_price_max_date,

                "last_updated": now
            }
            prices_to_save.append(price_entry)

        return prices_to_save