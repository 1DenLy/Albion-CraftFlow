import datetime
from typing import Optional

from sqlalchemy import (
    String,
    Integer,
    SmallInteger,
    BigInteger,
    ForeignKey,
    DateTime,
    Index,
    Computed,
    func,
    text,
    Boolean,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.database import Base


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    api_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    def __repr__(self):
        return f"<Location(id={self.id}, name='{self.api_name}')>"


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    unique_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    base_name: Mapped[str] = mapped_column(String(50), nullable=False)
    tier: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    enchantment_level: Mapped[int] = mapped_column(SmallInteger, default=0)


    effective_tier: Mapped[int] = mapped_column(
        SmallInteger,
        Computed("tier + enchantment_level", persisted=True)
    )

    display_name: Mapped[Optional[str]] = mapped_column(String(255))

    __table_args__ = (
        Index(
            "idx_items_high_tier",
            "base_name", "tier", "enchantment_level",
            postgresql_where=text("tier >= 4")
        ),
        Index("idx_items_lookup", "base_name", "tier", "enchantment_level"),
    )

    def __repr__(self):
        return f"<Item(id={self.id}, unique='{self.unique_name}')>"



class MarketPrice(Base):
    __tablename__ = "market_prices"

    item_id: Mapped[int] = mapped_column(ForeignKey("items.id", ondelete="CASCADE"), primary_key=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id", ondelete="CASCADE"), primary_key=True)
    quality_level: Mapped[int] = mapped_column(SmallInteger, primary_key=True, default=1)

    sell_price_min: Mapped[Optional[int]] = mapped_column(BigInteger)
    sell_price_min_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))
    sell_price_max: Mapped[Optional[int]] = mapped_column(BigInteger)
    sell_price_max_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))

    buy_price_min: Mapped[Optional[int]] = mapped_column(BigInteger)
    buy_price_min_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))
    buy_price_max: Mapped[Optional[int]] = mapped_column(BigInteger)
    buy_price_max_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))

    last_updated: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    item: Mapped["Item"] = relationship()
    location: Mapped["Location"] = relationship()



class MarketHistory(Base):
    __tablename__ = "market_history"

    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), primary_key=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"), primary_key=True)
    quality_level: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), primary_key=True)

    item_count: Mapped[int] = mapped_column(BigInteger, default=0)
    average_price: Mapped[int] = mapped_column(BigInteger)

    __table_args__ = (
        Index("idx_history_item_time", "item_id", "location_id", "timestamp"),
    )


class TrackedItem(Base):
    """
    Таблица для Воркера.
    Определяет КОНКРЕТНУЮ связку Предмет + Город, которую надо обновлять.
    """
    __tablename__ = "tracked_items"

    # первичный ключ составной: (Предмет + Город).
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id", ondelete="CASCADE"), primary_key=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id", ondelete="CASCADE"), primary_key=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    priority: Mapped[int] = mapped_column(SmallInteger, default=1, nullable=False)

    last_check: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))

    item: Mapped["Item"] = relationship()
    location: Mapped["Location"] = relationship()

    def __repr__(self):
        return f"<TrackedItem(item={self.item_id}, loc={self.location_id})>"