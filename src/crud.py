from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from typing import Optional, List

from src.db.models import Location, Item, TrackedItem, MarketPrice
# Сюда можно импортировать схемы, если нужно типизировать входные данные для create/update
from src.schemas import TrackedItemCreate

# --- Locations ---
async def get_all_locations(db: AsyncSession) -> list[Location]:
    result = await db.execute(select(Location))
    return result.scalars().all()

async def get_location_by_api_name(db: AsyncSession, api_name: str) -> Optional[Location]:
    query = select(Location).where(Location.api_name == api_name)
    result = await db.execute(query)
    return result.scalar_one_or_none()

# --- Items ---
async def search_items_by_name(db: AsyncSession, q: str, limit: int = 20) -> list[Item]:
    # Безопасный поиск через ORM
    query = select(Item).where(
        Item.unique_name.ilike(f"%{q}%") | Item.display_name.ilike(f"%{q}%")
    ).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_item_by_unique_name(db: AsyncSession, unique_name: str) -> Optional[Item]:
    query = select(Item).where(Item.unique_name == unique_name)
    result = await db.execute(query)
    return result.scalar_one_or_none()

# --- Tracking ---
async def get_tracked_item(db: AsyncSession, item_id: int, location_id: int) -> Optional[TrackedItem]:
    query = select(TrackedItem).where(
        TrackedItem.item_id == item_id,
        TrackedItem.location_id == location_id
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def create_tracked_item(db: AsyncSession, item: Item, location: Location) -> TrackedItem:
    new_track = TrackedItem(item_id=item.id, location_id=location.id, is_active=True)
    db.add(new_track)
    await db.commit()
    await db.refresh(new_track)
    # Ручная подвязка для возврата в Pydantic (решение проблемы Lazy Load)
    new_track.item = item
    new_track.location = location
    return new_track

async def get_all_tracked_items(db: AsyncSession) -> list[TrackedItem]:
    # Используем joinedload для оптимизации (Eager Loading)
    query = select(TrackedItem).options(
        joinedload(TrackedItem.item),
        joinedload(TrackedItem.location)
    )
    result = await db.execute(query)
    return result.scalars().all()

# --- Prices ---
async def get_prices_by_item_id(db: AsyncSession, item_id: int) -> list[MarketPrice]:
    query = select(MarketPrice).where(MarketPrice.item_id == item_id)
    result = await db.execute(query)
    return result.scalars().all()