from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_db
from src import crud, schemas

# Создаем отдельный роутер для локаций
router = APIRouter(
    prefix="/locations",
    tags=["References"]
)

@router.get("", response_model=list[schemas.LocationRead])
async def get_locations(db: AsyncSession = Depends(get_db)):
    """Получить список всех городов."""
    return await crud.get_all_locations(db)