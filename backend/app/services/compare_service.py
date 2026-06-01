import asyncio
import hashlib
import json
import uuid
from datetime import date, timedelta
from urllib.parse import urlparse

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.goods import Goods
from app.models.goods_price_history import GoodsPriceHistory
from app.models.user_compare_record import UserCompareRecord
from app.services.ai_service import (
    extract_goods_info_from_url,
    extract_goods_json_from_image,
    generate_price_analysis,
    generate_query_vector,
    rerank_similar_goods,
)
from app.services.vector_service import search_similar_goods
from app.utils.redis_client import redis_client


async def compare_by_url(db: AsyncSession, goods_url: str, user_id: int | None) -> dict:
    if not _is_supported_url(goods_url):
        raise ValueError("请输入有效的商品链接，当前建议使用淘宝、京东、拼多多或抖音商品链接。")

    goods_text = await extract_goods_info_from_url(goods_url)
    result = await _do_compare(db, goods_text)

    if user_id is not None:
        await _save_compare_record(db, user_id, goods_url, compare_type=2)

    return result


async def compare_by_keyword(db: AsyncSession, keyword: str, user_id: int | None) -> dict:
    goods_text = keyword.strip()
    if not goods_text:
        raise ValueError("请输入商品名称、品牌或型号。")

    result_cache_key = f"compare:keyword:{hashlib.md5(goods_text.encode()).hexdigest()}"
    cached_result = await redis_client.get(result_cache_key)
    if cached_result is not None:
        return cached_result

    result = await _do_compare(db, goods_text)
    await redis_client.set(result_cache_key, result, ttl=settings.COMPARE_RESULT_CACHE_TTL)

    if user_id is not None:
        await _save_compare_record(db, user_id, goods_text, compare_type=3)

    return result


async def compare_by_upload(db: AsyncSession, file_bytes: bytes, user_id: int | None) -> dict:
    """Upload image to OSS, recognize product info, then run the compare pipeline."""
    from app.utils.oss_client import oss_client

    object_key = f"goods-images/{uuid.uuid4().hex}.jpg"
    try:
        oss_url = oss_client.upload_image(file_bytes, object_key)
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"图片上传 OSS 失败: {str(e)}") from e

    try:
        goods_json = await extract_goods_json_from_image(oss_url)
    except Exception as e:
        raise RuntimeError(f"AI 识别失败: {str(e)}") from e

    query_text = _build_query_text(goods_json)
    if not query_text.strip():
        raise RuntimeError("AI 未能识别到有效商品信息，请重新上传更清晰的商品图片。")

    result = await _do_compare(db, query_text)
    result["extracted_info"] = goods_json
    result["oss_url"] = oss_url

    if user_id is not None:
        await _save_compare_record(db, user_id, query_text, compare_type=4)

    return result


def _build_query_text(goods_json: dict) -> str:
    parts = []
    for key in ("goods_name", "brand", "model", "specs"):
        val = goods_json.get(key, "")
        if val:
            parts.append(str(val))
    return " ".join(parts)


async def _do_compare(db: AsyncSession, query_text: str) -> dict:
    candidate_ids = []
    try:
        query_vector = await generate_query_vector(query_text)
        cache_key = f"vec:{hashlib.md5(query_text.encode()).hexdigest()}"
        candidate_ids = await redis_client.get(cache_key)
        if candidate_ids is None:
            candidate_ids = await search_similar_goods(query_vector, top_k=50)
            await redis_client.set(cache_key, candidate_ids, ttl=settings.VECTOR_CACHE_TTL)
        else:
            candidate_ids = [int(x) for x in candidate_ids]
    except Exception:
        candidate_ids = []

    if not candidate_ids:
        goods_list = await _query_goods_by_keyword(db, query_text)
    else:
        goods_list = await _batch_query_goods(db, candidate_ids)

    if not goods_list:
        return _empty_compare_result(query_text)

    try:
        ranked_goods = await asyncio.wait_for(
            rerank_similar_goods(query_text, goods_list),
            timeout=settings.RERANK_TIMEOUT_SECONDS,
        )
    except Exception:
        ranked_goods = _fallback_rank(goods_list, top_n=20)

    ranked_goods = [_attach_quality_scores(g) for g in ranked_goods]
    history_ids = candidate_ids[:10] if candidate_ids else [g["id"] for g in ranked_goods[:10]]
    price_history = await _query_price_history(db, history_ids)
    ai_analysis = await _get_price_analysis(query_text, ranked_goods, price_history)

    compare_list = []
    for g in ranked_goods:
        compare_list.append(
            {
                "goods_id": g["id"],
                "goods_name": g["goods_name"],
                "brand": g.get("brand", ""),
                "model": g.get("model", ""),
                "spec_param": g.get("spec_param", ""),
                "platform": g["platform"],
                "shop_name": g.get("shop_name", ""),
                "original_price": float(g["original_price"]),
                "real_price": float(g["real_price"]),
                "coupon_desc": g.get("coupon_desc", ""),
                "goods_img": g.get("goods_img", ""),
                "goods_url": g["goods_url"],
                "sales_num": g.get("sales_num", 0),
                "score": float(g.get("score", 0)),
                "sale_status": g["sale_status"],
                "match_score": float(g.get("match_score", 0)),
                "trust_score": float(g.get("trust_score", 0)),
            }
        )

    return {
        "goods_info": query_text,
        "ai_analysis": ai_analysis,
        "price_history": price_history,
        "compare_list": sorted(compare_list, key=lambda x: (x["real_price"], -x["trust_score"])),
    }


def _empty_compare_result(query_text: str) -> dict:
    return {
        "goods_info": query_text,
        "ai_analysis": {
            "price_level": "暂无数据",
            "buy_advice": "暂未找到足够相似的在售商品，建议更换关键词或上传更清晰的商品图片。",
            "price_prediction": "暂无可用趋势。",
        },
        "price_history": [],
        "compare_list": [],
    }


async def _get_price_analysis(query_text: str, ranked_goods: list[dict], price_history: list[dict]) -> dict:
    signature = {
        "query": query_text,
        "goods": [
            {
                "id": g.get("id"),
                "price": float(g.get("real_price") or 0),
                "trust": float(g.get("trust_score") or 0),
            }
            for g in ranked_goods[:10]
        ],
        "history_count": len(price_history),
    }
    cache_key = f"analysis:{hashlib.md5(json.dumps(signature, sort_keys=True).encode()).hexdigest()}"
    cached = await redis_client.get(cache_key)
    if cached is not None:
        return cached

    fallback = _rule_based_price_analysis(ranked_goods, price_history)
    if not settings.ENABLE_AI_PRICE_ANALYSIS:
        await redis_client.set(cache_key, fallback, ttl=settings.AI_ANALYSIS_CACHE_TTL)
        return fallback

    try:
        analysis = await asyncio.wait_for(
            generate_price_analysis(query_text, ranked_goods, price_history),
            timeout=settings.AI_PRICE_ANALYSIS_TIMEOUT_SECONDS,
        )
    except Exception:
        analysis = fallback

    await redis_client.set(cache_key, analysis, ttl=settings.AI_ANALYSIS_CACHE_TTL)
    return analysis


def _rule_based_price_analysis(goods_list: list[dict], price_history: list[dict]) -> dict:
    prices = [float(g.get("real_price") or 0) for g in goods_list if float(g.get("real_price") or 0) > 0]
    if not prices:
        return {
            "price_level": "暂无数据",
            "buy_advice": "候选商品缺少有效价格，建议更换关键词或稍后重试。",
            "price_prediction": "暂无可用价格趋势。",
        }

    min_price = min(prices)
    max_price = max(prices)
    avg_price = sum(prices) / len(prices)
    trusted_count = sum(1 for g in goods_list if float(g.get("trust_score") or 0) >= 70)
    cheapest = min(goods_list, key=lambda g: float(g.get("real_price") or 10**12))
    cheapest_price = float(cheapest.get("real_price") or min_price)

    if cheapest_price <= avg_price * 0.9:
        price_level = "偏低"
    elif cheapest_price >= avg_price * 1.1:
        price_level = "偏高"
    else:
        price_level = "适中"

    advice = (
        f"当前同款价格约 ¥{min_price:.2f}-¥{max_price:.2f}，最低价 ¥{cheapest_price:.2f}。"
        "建议优先选择可信度高、价格接近低位的店铺。"
    )
    if trusted_count == 0:
        advice = f"当前同款价格约 ¥{min_price:.2f}-¥{max_price:.2f}，但高可信候选较少，建议谨慎下单。"

    trend = "近 30 天价格记录较少，建议关注后续价格变化。"
    if len(price_history) >= 2:
        first = float(price_history[0].get("price") or 0)
        last = float(price_history[-1].get("price") or 0)
        if first > 0 and last < first * 0.98:
            trend = "近期价格有下降迹象，可以继续观察或设置降价提醒。"
        elif first > 0 and last > first * 1.02:
            trend = "近期价格有上升迹象，刚需可优先选择可信低价店铺。"
        else:
            trend = "近期价格整体较平稳，可结合优惠券和店铺可信度选择。"

    return {
        "price_level": price_level,
        "buy_advice": advice,
        "price_prediction": trend,
    }


def _fallback_rank(goods_list: list[dict], top_n: int) -> list[dict]:
    ranked = []
    for index, goods in enumerate(goods_list[:top_n]):
        item = dict(goods)
        item["match_score"] = max(60.0, 85.0 - index * 2)
        ranked.append(item)
    return ranked


def _attach_quality_scores(goods: dict) -> dict:
    item = dict(goods)
    sales_num = int(item.get("sales_num") or 0)
    score = float(item.get("score") or 0)
    has_image = bool(item.get("goods_img"))
    has_shop = bool(item.get("shop_name"))

    trust = 45.0
    trust += min(sales_num / 1000, 20)
    trust += min(max(score, 0) * 6, 25)
    trust += 5 if has_image else 0
    trust += 5 if has_shop else 0
    item["trust_score"] = round(min(trust, 100), 1)
    item["match_score"] = round(float(item.get("match_score") or 0), 1)
    return item


def _is_supported_url(goods_url: str) -> bool:
    parsed = urlparse(goods_url.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return False
    host = parsed.netloc.lower()
    return any(
        domain in host
        for domain in (
            "taobao.com",
            "tmall.com",
            "jd.com",
            "yangkeduo.com",
            "pinduoduo.com",
            "douyin.com",
        )
    )


async def _batch_query_goods(db: AsyncSession, goods_ids: list[int]) -> list[dict]:
    result = await db.execute(select(Goods).where(Goods.id.in_(goods_ids), Goods.sale_status == 1))
    goods_rows = result.scalars().all()
    return [
        {
            "id": g.id,
            "goods_name": g.goods_name,
            "brand": g.brand,
            "model": g.model,
            "spec_param": g.spec_param,
            "platform": g.platform,
            "shop_name": g.shop_name,
            "original_price": g.original_price,
            "real_price": g.real_price,
            "coupon_desc": g.coupon_desc,
            "goods_img": g.goods_img,
            "goods_url": g.goods_url,
            "sales_num": g.sales_num,
            "score": g.score,
            "feature_content": g.feature_content,
            "sale_status": g.sale_status,
        }
        for g in goods_rows
    ]


async def _query_goods_by_keyword(db: AsyncSession, query_text: str, limit: int = 50) -> list[dict]:
    terms = [term.strip() for term in query_text.replace("/", " ").replace("-", " ").split() if term.strip()]
    terms = terms[:6] or [query_text.strip()]
    like_clauses = []
    for term in terms:
        pattern = f"%{term}%"
        like_clauses.extend(
            [
                Goods.goods_name.like(pattern),
                Goods.brand.like(pattern),
                Goods.model.like(pattern),
                Goods.spec_param.like(pattern),
                Goods.feature_content.like(pattern),
            ]
        )

    result = await db.execute(
        select(Goods)
        .where(Goods.sale_status == 1, or_(*like_clauses))
        .order_by(Goods.sales_num.desc(), Goods.score.desc(), Goods.real_price.asc())
        .limit(limit)
    )
    goods_rows = result.scalars().all()
    return [
        {
            "id": g.id,
            "goods_name": g.goods_name,
            "brand": g.brand,
            "model": g.model,
            "spec_param": g.spec_param,
            "platform": g.platform,
            "shop_name": g.shop_name,
            "original_price": g.original_price,
            "real_price": g.real_price,
            "coupon_desc": g.coupon_desc,
            "goods_img": g.goods_img,
            "goods_url": g.goods_url,
            "sales_num": g.sales_num,
            "score": g.score,
            "feature_content": g.feature_content,
            "sale_status": g.sale_status,
        }
        for g in goods_rows
    ]


async def _query_price_history(db: AsyncSession, goods_ids: list[int]) -> list[dict]:
    thirty_days_ago = date.today() - timedelta(days=30)
    result = await db.execute(
        select(GoodsPriceHistory)
        .where(
            GoodsPriceHistory.goods_id.in_(goods_ids),
            GoodsPriceHistory.record_date >= thirty_days_ago,
        )
        .order_by(GoodsPriceHistory.record_date.asc())
    )
    rows = result.scalars().all()
    return [{"goods_id": r.goods_id, "date": r.record_date.strftime("%Y-%m-%d"), "price": float(r.price)} for r in rows]


async def _save_compare_record(db: AsyncSession, user_id: int, search_source: str, compare_type: int):
    record = UserCompareRecord(
        user_id=user_id,
        search_source=search_source,
        compare_type=compare_type,
    )
    db.add(record)
