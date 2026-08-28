"""统一响应体：{ code, message, data }，code=0 表示成功。"""
from typing import Any


def ok(data: Any = None, message: str = "ok") -> dict:
    return {"code": 0, "message": message, "data": data}


def fail(code: int, message: str) -> dict:
    return {"code": code, "message": message, "data": None}