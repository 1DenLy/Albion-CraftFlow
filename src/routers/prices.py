from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_db
from src import crud, schemas

router = APIRouter(
    prefix="/prices",
    tags=["Market Data"]
)


@router.get("/{item_unique_name}", response_model=list[schemas.MarketPriceRead])
async def get_item_prices(
        item_unique_name: str,
        db: AsyncSession = Depends(get_db)
):
    """Получить цены на конкретный предмет."""
    item = await crud.get_item_by_unique_name(db, item_unique_name)

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return await crud.get_prices_by_item_id(db, item.id)