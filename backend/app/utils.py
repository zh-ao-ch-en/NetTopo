"""通用工具：ID 生成、时间处理。"""
import uuid
from datetime import date, datetime, timedelta


def gen_id(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex}"


def now() -> datetime:
    """当前本地时间（naive），统一按本地时区存储与展示。"""
    return datetime.now()


def today() -> date:
    return date.today()


def offset_date(days: int) -> date:
    return date.today() + timedelta(days=days)


def offset_datetime(days: int) -> datetime:
    return datetime.now() + timedelta(days=days)


def fmt(value) -> str:
    """date/datetime -> 展示字符串。日期 YYYY-MM-DD，时间 YYYY-MM-DD HH:MM:SS。"""
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def parse_date(value) -> date | None:
    """'YYYY-MM-DD' 或 date -> date；空/非法返回 None。"""
    if value is None or value == "":
        return None
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None