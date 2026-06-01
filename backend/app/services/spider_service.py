"""
爬虫服务 —— 处理后台爬虫入库

商品特征文本拼接规则：
goods_name + brand + model + spec_param
用于生成向量存入Milvus
"""
import hashlib
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.goods import Goods
from app.models.goods_price_history import GoodsPriceHistory
from app.services.ai_service import generate_query_vector
from app.services.vector_service import insert_vector


async def add_goods_from_spider(db: AsyncSession, goods_data: dict) -> dict:
    """
    爬虫入库。
    新增商品 → 插入MySQL → 获取自增ID → 生成向量 → 存入Milvus。
    已有商品更新价格 → 检测价格变动 → 写入goods_price_history。
    """
    goods_url = goods_data.get("goods_url", "")
    goods_url_hash = hashlib.sha256(goods_url.encode("utf-8")).hexdigest()
    platform = goods_data.get("platform", "")
    real_price = Decimal(str(goods_data.get("real_price", 0)))

    feature_text = f"{goods_data.get('goods_name', '')} {goods_data.get('brand', '')} {goods_data.get('model', '')} {goods_data.get('spec_param', '')}"

    # 检查是否已存在（同平台同URL）
    result = await db.execute(
        select(Goods).where(Goods.goods_url == goods_url, Goods.platform == platform)
    )
    existing = result.scalar_one_or_none()

    if existing is not None:
        old_price = existing.real_price
        if old_price != real_price:
            # 价格变动，写入历史价格表
            from datetime import date
            price_record = GoodsPriceHistory(
                goods_id=existing.id,
                price=real_price,
                record_date=date.today(),
            )
            db.add(price_record)
            existing.real_price = real_price
            existing.last_update_time = None  # trigger onupdate

        # 更新其他字段
        existing.goods_name = goods_data.get("goods_name", existing.goods_name)
        existing.original_price = Decimal(str(goods_data.get("original_price", existing.original_price)))
        existing.coupon_desc = goods_data.get("coupon_desc", existing.coupon_desc)
        existing.goods_img = goods_data.get("goods_img", existing.goods_img)
        existing.goods_url_hash = goods_url_hash
        existing.sales_num = goods_data.get("sales_num", existing.sales_num)
        existing.score = Decimal(str(goods_data.get("score", existing.score)))
        existing.feature_content = feature_text
        existing.sale_status = goods_data.get("sale_status", 1)
        await db.flush()
        return {"ok": True, "goods_id": existing.id, "action": "updated"}

    # 新增商品
    goods = Goods(
        goods_name=goods_data.get("goods_name", ""),
        brand=goods_data.get("brand", ""),
        model=goods_data.get("model", ""),
        spec_param=goods_data.get("spec_param", ""),
        platform=platform,
        shop_name=goods_data.get("shop_name", ""),
        original_price=Decimal(str(goods_data.get("original_price", 0))),
        real_price=real_price,
        coupon_desc=goods_data.get("coupon_desc", ""),
        goods_img=goods_data.get("goods_img", ""),
        goods_url=goods_url,
        goods_url_hash=goods_url_hash,
        sales_num=goods_data.get("sales_num", 0),
        score=Decimal(str(goods_data.get("score", 0))),
        feature_content=feature_text,
        sale_status=goods_data.get("sale_status", 1),
    )
    db.add(goods)
    await db.flush()

    # 生成向量并存入Milvus
    vector = await generate_query_vector(feature_text)
    await insert_vector(
        goods_id=goods.id,
        vector=vector,
        brand=goods.brand,
        platform=goods.platform,
    )

    return {"ok": True, "goods_id": goods.id, "action": "created"}
