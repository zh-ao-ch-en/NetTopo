"""通用工具：ID 生成、时间。"""
import uuid
from datetime import date, datetime, timedelta, timezone


def gen_id(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex}"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def today() -> str:
    return date.today().isoformat()


def offset_date(days: int) -> str:
    return (date.today() + timedelta(days=days)).isoformat()