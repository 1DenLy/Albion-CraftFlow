# app/routers/items.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from .. import models, schemas
from ..database import get_db_session # <-- Наша зависимость!

router = APIRouter(prefix="/items", tags=["Items"])

@router.get("/", response_model=list[schemas.Item])
async def get_all_items(db: AsyncSession = Depends(get_db_session)):
    # ... тут логика получения данных из db ...
    pass