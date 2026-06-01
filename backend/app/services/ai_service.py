"""
AI service wrappers for product recognition, embedding, reranking, and price analysis.

The OpenAI-compatible calls are synchronous in the SDK, so they run in a worker
thread to avoid blocking FastAPI's event loop.
"""
import asyncio
import json
import logging
import time

import aiohttp
import dashscope
from openai import APIError, OpenAI

from app.config import settings

logger = logging.getLogger(__name__)
dashscope.api_key = settings.DASHSCOPE_API_KEY

_client = OpenAI(
    api_key=settings.DASHSCOPE_API_KEY,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)


def _strip_json_markdown(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
    return text


async def extract_goods_json_from_image(oss_url: str) -> dict:
    """Recognize product information from an uploaded image and return JSON."""

    def _call():
        models = [settings.VISION_MODEL, *settings.VISION_FALLBACK_MODELS]
        models = list(dict.fromkeys(models))
        last_error: Exception | None = None
        response = None

        for model in models:
            start = time.perf_counter()
            try:
                response = _client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image_url",
                                    "image_url": {"url": oss_url},
                                },
                                {
                                    "type": "text",
                                    "text": (
                                        "请识别图片中的商品信息，只返回严格 JSON，不要返回 markdown 或额外解释。\n"
                                        "如果某个字段无法识别，请使用空字符串。\n"
                                        "{\n"
                                        '  "goods_name": "商品名称",\n'
                                        '  "brand": "品牌",\n'
                                        '  "model": "型号",\n'
                                        '  "price": "图片中出现的价格",\n'
                                        '  "category": "类目",\n'
                                        '  "specs": "规格参数"\n'
                                        "}"
                                    )
                                },
                            ],
                        }
                    ],
                    temperature=0.1,
                )
                logger.info("vision_model_call_ok model=%s cost_ms=%.2f", model, (time.perf_counter() - start) * 1000)
                break
            except APIError as exc:
                last_error = exc
                logger.warning(
                    "vision_model_call_failed model=%s status=%s cost_ms=%.2f",
                    model,
                    getattr(exc, "status_code", None),
                    (time.perf_counter() - start) * 1000,
                )
                if getattr(exc, "status_code", None) not in {403, 404, 429, 500, 502, 503, 504}:
                    raise
            except Exception as exc:
                last_error = exc
                logger.warning(
                    "vision_model_call_failed model=%s error=%s cost_ms=%.2f",
                    model,
                    type(exc).__name__,
                    (time.perf_counter() - start) * 1000,
                )

        if response is None:
            if last_error is not None and getattr(last_error, "status_code", None) == 403:
                raise RuntimeError("DashScope 视觉模型无访问权限，请检查 API Key、业务空间和模型开通状态。") from last_error
            raise RuntimeError(f"AI 识图服务调用失败: {last_error}") from last_error

        text = response.choices[0].message.content or ""

        text = _strip_json_markdown(text)
        if not text:
            raise RuntimeError("AI 未返回识别结果，请换一张更清晰、包含完整商品主体的图片。")

        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"AI 返回内容不是合法 JSON: {text[:200]}") from exc

    return await asyncio.to_thread(_call)


async def extract_goods_info_from_url(goods_url: str) -> str:
    """Extract a searchable product description from a product URL."""

    def _call():
        start = time.perf_counter()
        response = _client.chat.completions.create(
            model="qwen-plus",
            messages=[
                {
                    "role": "user",
                    "content": (
                        "请根据下面的商品链接，提取可用于全网比价的关键词。"
                        "如果无法访问链接，只从链接文本中提取平台、商品名、品牌、型号或 SKU 线索，"
                        "不要编造不存在的信息。\n"
                        f"商品链接：{goods_url}"
                    ),
                }
            ],
            temperature=0.2,
        )
        logger.info("url_extract_call_ok model=qwen-plus cost_ms=%.2f", (time.perf_counter() - start) * 1000)
        return response.choices[0].message.content.strip()

    return await asyncio.to_thread(_call)


async def generate_query_vector(text: str) -> list[float]:
    """Generate a text embedding for product search."""

    def _call():
        start = time.perf_counter()
        resp = _client.embeddings.create(
            model=settings.EMBEDDING_MODEL,
            input=text,
            dimensions=1024,
        )
        logger.info("embedding_call_ok model=%s cost_ms=%.2f", settings.EMBEDDING_MODEL, (time.perf_counter() - start) * 1000)
        return resp.data[0].embedding

    return await asyncio.to_thread(_call)


async def rerank_similar_goods(query_text: str, goods_list: list[dict], top_n: int = 20) -> list[dict]:
    """Rerank candidate products and attach a normalized match_score."""
    if not goods_list:
        return []

    documents = [
        g.get("feature_content")
        or " ".join(
            str(x)
            for x in [g.get("goods_name"), g.get("brand"), g.get("model"), g.get("spec_param")]
            if x
        )
        for g in goods_list
    ]

    url = "https://dashscope.aliyuncs.com/api/v1/services/rerank/text-rerank/text-rerank"
    headers = {
        "Authorization": f"Bearer {settings.DASHSCOPE_API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "model": settings.RERANK_MODEL,
        "input": {"query": query_text, "documents": documents},
        "parameters": {"top_n": top_n, "return_documents": False},
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                headers=headers,
                json=body,
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                if resp.status != 200:
                    return _fallback_rank(goods_list, top_n)
                result = await resp.json()
    except (TimeoutError, aiohttp.ClientError, ValueError):
        return _fallback_rank(goods_list, top_n)

    if result.get("code") and isinstance(result.get("code"), str):
        return _fallback_rank(goods_list, top_n)

    ranked = []
    for item in result.get("output", {}).get("results", []):
        index = item.get("index")
        if not isinstance(index, int) or index >= len(goods_list):
            continue
        goods = dict(goods_list[index])
        goods["match_score"] = round(float(item.get("relevance_score", 0)) * 100, 1)
        ranked.append(goods)

    return ranked or _fallback_rank(goods_list, top_n)


def _fallback_rank(goods_list: list[dict], top_n: int) -> list[dict]:
    ranked = []
    for index, goods in enumerate(goods_list[:top_n]):
        item = dict(goods)
        item["match_score"] = max(60.0, 85.0 - index * 2)
        ranked.append(item)
    return ranked


async def generate_price_analysis(
    query_text: str, goods_list: list[dict], price_history: list[dict]
) -> dict:
    """Generate a concise price-level analysis and purchase suggestion."""
    if not goods_list:
        return {
            "price_level": "暂无数据",
            "buy_advice": "暂未找到足够相似的在售商品，建议换一张更清晰的图片或补充品牌型号。",
            "price_prediction": "暂无可用价格趋势。",
        }

    prices = [float(g["real_price"]) for g in goods_list if float(g.get("real_price", 0)) > 0]
    if not prices:
        return {
            "price_level": "暂无数据",
            "buy_advice": "候选商品缺少有效价格，建议稍后重试或更换搜索关键词。",
            "price_prediction": "暂无可用价格趋势。",
        }

    min_price = min(prices)
    max_price = max(prices)
    avg_price = sum(prices) / len(prices)
    trusted_count = sum(1 for g in goods_list if float(g.get("trust_score", 0)) >= 70)

    analysis_prompt = f"""
你是一个谨慎的商品比价分析师。请基于真实价格数据给出建议，不要夸大降价概率。
商品描述：{query_text}
候选同款数：{len(goods_list)}
可信候选数：{trusted_count}
最低到手价：¥{min_price:.2f}
最高到手价：¥{max_price:.2f}
平均到手价：¥{avg_price:.2f}
近 30 天价格记录数：{len(price_history)}

请只返回 JSON：
{{
  "price_level": "偏低/适中/偏高/暂无数据",
  "buy_advice": "80字以内，说明是否值得入手以及需要注意的风险",
  "price_prediction": "60字以内，说明未来7天价格趋势判断"
}}
"""

    def _call():
        resp = _client.chat.completions.create(
            model=settings.MATH_MODEL,
            messages=[{"role": "user", "content": analysis_prompt}],
            temperature=0.3,
        )
        return resp.choices[0].message.content.strip()

    content = _strip_json_markdown(await asyncio.to_thread(_call))
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {
            "price_level": "适中",
            "buy_advice": f"同款价格区间 ¥{min_price:.2f}-¥{max_price:.2f}，建议优先选择可信度高且价格接近低位的店铺。",
            "price_prediction": "目前价格走势信息有限，建议开启降价提醒后再观察。",
        }
