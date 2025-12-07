from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_db
from src import crud, schemas

router = APIRouter(
    prefix="/tracked-items",
    tags=["Tracking"]
)

@router.post("", response_model=schemas.TrackedItemRead)
async def add_tracked_item(
    payload: schemas.TrackedItemCreate,
    db: AsyncSession = Depends(get_db)
):
    """Добавить предмет в список отслеживания."""
    # Валидация существования
    item = await crud.get_item_by_unique_name(db, payload.item_unique_name)
    location = await crud.get_location_by_api_name(db, payload.location_api_name)

    if not item or not location:
        raise HTTPException(status_code=404, detail="Item or Location not found")

    # Проверка на дубликаты
    existing = await crud.get_tracked_item(db, item.id, location.id)
    if existing:
        raise HTTPException(status_code=400, detail="Already tracked")

    return await crud.create_tracked_item(db, item, location)

@router.get("", response_model=list[schemas.TrackedItemRead])
async def get_tracked_items(db: AsyncSession = Depends(get_db)):
    """Получить все отслеживаемые предметы."""
    return await crud.get_all_tracked_items(db)