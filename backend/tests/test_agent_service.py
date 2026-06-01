import asyncio

from app.services import agent_service


def test_agent_history_requires_login():
    result = asyncio.run(agent_service.chat(None, "查看我的历史记录", None))

    assert result["intent"] == "history"
    assert result["need_login"] is True


def test_agent_general_reply():
    result = asyncio.run(agent_service.chat(None, "你好", None))

    assert result["intent"] == "general"
    assert "商品比价" in result["reply"]
