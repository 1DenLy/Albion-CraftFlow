from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_db
from src import crud, schemas

router = APIRouter(
    prefix="/items",
    tags=["References"]
)

@router.get("", response_model=list[schemas.ItemRead])
async def search_items(
    q: str = Query(..., min_length=2, description="Поиск по имени (напр. 'BAG')"),
    limit: int = Query(20, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Поиск предметов по имени."""
    return await crud.search_items_by_name(db, q, limit)