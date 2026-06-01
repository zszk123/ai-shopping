from typing import Any


def success(data: Any = None, msg: str = "ok") -> dict:
    return {"code": 200, "msg": msg, "data": data}


def fail(msg: str = "error", code: int = 400) -> dict:
    return {"code": code, "msg": msg, "data": None}
