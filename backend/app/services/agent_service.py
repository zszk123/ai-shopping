"""Lightweight customer-service agent orchestration."""
from __future__ import annotations

import re

from sqlalchemy.ext.asyncio import AsyncSession

from app.services import compare_service, record_service

HISTORY_WORDS = ("历史", "记录", "上次", "之前", "查过")
COMPARE_WORDS = ("比价", "多少钱", "价格", "推荐", "值得", "便宜", "贵", "搜索", "找")
HELP_WORDS = ("怎么", "如何", "失败", "报错", "无法", "不能", "没显示", "连接")


async def chat(db: AsyncSession, message: str, user_id: int | None) -> dict:
    text = message.strip()
    intent = _detect_intent(text)
    tool_results = []

    if intent == "history":
        if user_id is None:
            return {
                "reply": "你需要先登录，我才能帮你查看比价历史记录。",
                "intent": intent,
                "tool_results": [],
                "need_login": True,
            }
        records = await record_service.get_compare_records(db, user_id)
        recent = records[:5]
        tool_results.append(
            {
                "tool": "get_user_compare_history",
                "summary": f"查询到最近 {len(recent)} 条比价记录。",
                "data": recent,
            }
        )
        return {
            "reply": _format_history_reply(recent),
            "intent": intent,
            "tool_results": tool_results,
            "need_login": False,
        }

    if intent == "compare":
        keyword = _extract_keyword(text)
        try:
            result = await compare_service.compare_by_keyword(db, keyword, user_id=None)
        except Exception as exc:
            return {
                "reply": f"我理解你想比价“{keyword}”，但当前比价工具调用失败：{exc}",
                "intent": intent,
                "tool_results": [
                    {
                        "tool": "compare_by_keyword",
                        "summary": "关键词比价失败。",
                        "data": {"keyword": keyword},
                    }
                ],
                "need_login": False,
            }

        compare_list = result.get("compare_list", [])
        tool_results.append(
            {
                "tool": "compare_by_keyword",
                "summary": f"按关键词“{keyword}”找到 {len(compare_list)} 个候选商品。",
                "data": {
                    "keyword": keyword,
                    "top_goods": compare_list[:3],
                    "ai_analysis": result.get("ai_analysis", {}),
                },
            }
        )
        return {
            "reply": _format_compare_reply(keyword, result),
            "intent": intent,
            "tool_results": tool_results,
            "need_login": False,
        }

    if intent == "troubleshooting":
        return {
            "reply": _format_troubleshooting_reply(text),
            "intent": intent,
            "tool_results": [
                {
                    "tool": "diagnose_runtime_error",
                    "summary": "根据常见运行问题生成排查建议。",
                    "data": None,
                }
            ],
            "need_login": False,
        }

    return {
        "reply": (
            "我可以帮你做三类事情：商品比价、解释购买建议、查看比价历史。"
            "你可以直接说“帮我比价 iPhone 16 256G”，或者“查看我的历史记录”。"
        ),
        "intent": "general",
        "tool_results": [],
        "need_login": False,
    }


async def chat_with_image(db: AsyncSession, file_bytes: bytes, user_id: int | None, message: str = "") -> dict:
    try:
        result = await compare_service.compare_by_upload(db, file_bytes, user_id=user_id)
    except Exception as exc:
        return {
            "reply": f"我收到图片了，但图片识别或比价失败：{exc}",
            "intent": "image_compare",
            "tool_results": [
                {
                    "tool": "compare_by_image",
                    "summary": "图片比价失败。",
                    "data": None,
                }
            ],
            "need_login": False,
        }

    compare_list = result.get("compare_list", [])
    extracted = result.get("extracted_info", {})
    query_text = result.get("goods_info") or _build_image_query_summary(extracted)
    prefix = f"我识别到的商品信息是：{query_text}。\n" if query_text else "我已经识别了这张图片。\n"
    if message.strip():
        prefix = f"你补充的问题是：“{message.strip()}”。\n{prefix}"

    return {
        "reply": prefix + _format_compare_reply(query_text or "图片商品", result),
        "intent": "image_compare",
        "tool_results": [
            {
                "tool": "compare_by_image",
                "summary": f"图片识别并比价，找到 {len(compare_list)} 个候选商品。",
                "data": {
                    "extracted_info": extracted,
                    "top_goods": compare_list[:3],
                    "ai_analysis": result.get("ai_analysis", {}),
                },
            }
        ],
        "need_login": False,
    }


def _detect_intent(text: str) -> str:
    if any(word in text for word in HISTORY_WORDS):
        return "history"
    if any(word in text for word in HELP_WORDS):
        return "troubleshooting"
    if any(word in text for word in COMPARE_WORDS) or len(text) >= 4:
        return "compare"
    return "general"


def _extract_keyword(text: str) -> str:
    keyword = text
    keyword = re.sub(r"(帮我|请|一下|看看|查查|搜索|找|比价|推荐|多少钱|价格|值得买吗|贵不贵)", " ", keyword)
    keyword = re.sub(r"\s+", " ", keyword).strip(" ，。,.?")
    return keyword or text.strip()


def _build_image_query_summary(extracted: dict) -> str:
    return " ".join(
        str(extracted.get(key, "")).strip()
        for key in ("goods_name", "brand", "model", "specs")
        if str(extracted.get(key, "")).strip()
    )


def _format_history_reply(records: list[dict]) -> str:
    if not records:
        return "你还没有比价历史。可以先上传图片、粘贴链接，或者输入关键词发起一次比价。"
    lines = ["这是你最近的比价记录："]
    for item in records[:5]:
        source = str(item.get("search_source", ""))
        if len(source) > 28:
            source = source[:28] + "..."
        lines.append(f"- {source}（{_type_label(item.get('compare_type'))}，{item.get('create_time', '')}）")
    return "\n".join(lines)


def _format_compare_reply(keyword: str, result: dict) -> str:
    compare_list = result.get("compare_list", [])
    analysis = result.get("ai_analysis", {})
    if not compare_list:
        return f"我按“{keyword}”查了一下，暂时没有找到足够相似的在售商品。可以补充品牌、型号或规格再试。"

    cheapest = min(compare_list, key=lambda item: float(item.get("real_price") or 10**12))
    trusted = max(compare_list, key=lambda item: float(item.get("trust_score") or 0))
    return (
        f"我按“{keyword}”找到了 {len(compare_list)} 个候选商品。\n"
        f"当前最低价是 ¥{float(cheapest.get('real_price') or 0):.2f}，来自{cheapest.get('platform', '未知平台')}。\n"
        f"可信度较高的是“{trusted.get('goods_name', '未知商品')}”，可信分 {float(trusted.get('trust_score') or 0):.0f}。\n"
        f"购买建议：{analysis.get('buy_advice', '建议优先选择价格合理、店铺信息完整的商品。')}"
    )


def _format_troubleshooting_reply(text: str) -> str:
    if "连接" in text or "后端" in text:
        return "如果页面提示后端连接失败，先访问 http://127.0.0.1:8000/readyz，确认 database、redis、milvus 都是 true。"
    if "图片" in text or "识别" in text:
        return "图片比价失败时，先确认图片是 jpg、png 或 webp，大小不超过 8MB，并且 DashScope 视觉模型和 OSS 配置可用。"
    if "没显示" in text or "空白" in text:
        return "如果结果页空白，通常是前端状态被清空或没有匹配到商品。请重新发起比价；现在页面会显示明确的空结果提示。"
    return "你可以把具体报错发给我，我会按前端、后端、数据库、向量库这几层帮你定位。"


def _type_label(compare_type) -> str:
    return {1: "图片", 2: "链接", 3: "关键词", 4: "图片"}.get(compare_type, "未知")
