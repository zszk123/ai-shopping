import asyncio

from app.config import settings
from app.services import ai_service


class _Message:
    content = '{"goods_name":"测试商品","brand":"","model":"","price":"","category":"","specs":""}'


class _Choice:
    message = _Message()


class _Response:
    choices = [_Choice()]


class _Completions:
    def __init__(self):
        self.models = []

    def create(self, model, **kwargs):
        self.models.append(model)
        if model == "bad-model":
            raise RuntimeError("first model failed")
        return _Response()


class _Chat:
    def __init__(self):
        self.completions = _Completions()


class _Client:
    def __init__(self):
        self.chat = _Chat()


def test_vision_model_fallback(monkeypatch):
    client = _Client()
    monkeypatch.setattr(ai_service, "_client", client)
    monkeypatch.setattr(settings, "VISION_MODEL", "bad-model")
    monkeypatch.setattr(settings, "VISION_FALLBACK_MODELS", ["good-model"])

    result = asyncio.run(ai_service.extract_goods_json_from_image("https://example.com/image.jpg"))

    assert result["goods_name"] == "测试商品"
    assert client.chat.completions.models == ["bad-model", "good-model"]
