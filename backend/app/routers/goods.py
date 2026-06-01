from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services import goods_service
from app.utils.response import success

router = APIRouter(prefix="/api/goods", tags=["goods"])


@router.get("/price/history")
async def get_price_history(
    goods_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
):
    result = await goods_service.get_goods_price_history(db, goods_id)
    return success(data=result)
