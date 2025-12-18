from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict


class AlbionPriceDTO(BaseModel):
    item_id: str = Field(alias="itemTypeId")
    city: str = Field(alias="city")
    quality: int = Field(alias="qualityLevel")

    # Sell Prices
    sell_price_min: Optional[int] = Field(alias="sellPriceMin", default=0)
    sell_price_min_date: Optional[datetime] = Field(alias="sellPriceMinDate", default=None)

    sell_price_max: Optional[int] = Field(alias="sellPriceMax", default=0)
    sell_price_max_date: Optional[datetime] = Field(alias="sellPriceMaxDate", default=None)

    # Buy Prices
    buy_price_min: Optional[int] = Field(alias="buyPriceMin", default=0)
    buy_price_min_date: Optional[datetime] = Field(alias="buyPriceMinDate", default=None)

    buy_price_max: Optional[int] = Field(alias="buyPriceMax", default=0)
    buy_price_max_date: Optional[datetime] = Field(alias="buyPriceMaxDate", default=None)

    model_config = ConfigDict(populate_by_name=True)

    @field_validator(
        'sell_price_min', 'sell_price_max',
        'buy_price_min', 'buy_price_max',
        mode='before'
    )
    @classmethod
    def non_negative_prices(cls, v):
        if v is None:
            return 0
        if v < 0:
            raise ValueError("Price cannot be negative")
        return v