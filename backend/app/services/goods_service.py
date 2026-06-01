from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.goods import Goods
from app.models.goods_price_history import GoodsPriceHistory
from app.utils.redis_client import redis_client


async def get_goods_price_history(db: AsyncSession, goods_id: int) -> dict:
    # 查缓存
    cache_key = f"price_history:{goods_id}"
    cached = await redis_client.get(cache_key)
    if cached is not None:
        return cached

    thirty_days_ago = date.today() - timedelta(days=30)
    result = await db.execute(
        select(GoodsPriceHistory)
        .where(
            GoodsPriceHistory.goods_id == goods_id,
            GoodsPriceHistory.record_date >= thirty_days_ago,
        )
        .order_by(GoodsPriceHistory.record_date.asc())
    )
    rows = result.scalars().all()
    price_history = [
        {"date": r.record_date.strftime("%Y-%m-%d"), "price": float(r.price)}
        for r in rows
    ]
    resp = {"goods_id": goods_id, "price_history": price_history}

    await redis_client.set(cache_key, resp, ttl=settings.GOODS_INFO_CACHE_TTL)
    return resp


async def get_goods_info(db: AsyncSession, goods_id: int) -> dict | None:
    cache_key = f"goods_info:{goods_id}"
    cached = await redis_client.get(cache_key)
    if cached is not None:
        return cached

    result = await db.execute(select(Goods).where(Goods.id == goods_id))
    goods = result.scalar_one_or_none()
    if goods is None:
        return None

    info = {
        "id": goods.id,
        "goods_name": goods.goods_name,
        "brand": goods.brand,
        "model": goods.model,
        "spec_param": goods.spec_param,
        "platform": goods.platform,
        "shop_name": goods.shop_name,
        "original_price": float(goods.original_price),
        "real_price": float(goods.real_price),
        "coupon_desc": goods.coupon_desc,
        "goods_img": goods.goods_img,
        "goods_url": goods.goods_url,
        "sales_num": goods.sales_num,
        "score": float(goods.score),
        "sale_status": goods.sale_status,
    }
    await redis_client.set(cache_key, info, ttl=settings.GOODS_INFO_CACHE_TTL)
    return info
