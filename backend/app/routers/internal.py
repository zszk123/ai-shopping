from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import require_internal_token
from app.services import ai_service, spider_service, vector_service
from app.utils.response import fail, success

router = APIRouter(prefix="/api/internal", tags=["internal"], dependencies=[Depends(require_internal_token)])


@router.post("/spider/add-goods")
async def spider_add_goods(goods_data: dict, db: AsyncSession = Depends(get_db)):
    try:
        result = await spider_service.add_goods_from_spider(db, goods_data)
        return success(data=result)
    except Exception as e:
        return fail(msg=f"Insert goods failed: {str(e)}", code=500)


@router.post("/vector/insert")
async def vec_insert(goods_id: int, vector: list[float], brand: str = "", platform: str = ""):
    try:
        ok = await vector_service.insert_vector(goods_id, vector, brand, platform)
        return success(data={"ok": ok})
    except Exception as e:
        return fail(msg=f"Insert vector failed: {str(e)}", code=500)


@router.post("/vector/search")
async def vec_search(query_text: str = Query(...), top_k: int = Query(default=50, ge=1, le=100)):
    try:
        query_vector = await ai_service.generate_query_vector(query_text)
        goods_ids = await vector_service.search_similar_goods(query_vector, top_k)
        return success(data={"goods_ids": goods_ids})
    except Exception as e:
        return fail(msg=f"Vector search failed: {str(e)}", code=500)
