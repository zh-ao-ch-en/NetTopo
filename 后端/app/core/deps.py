"""FastAPI 依赖：数据库会话、当前用户、角色鉴权。"""
from __future__ import annotations

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.database import get_db
from app.models import User

bearer = HTTPBearer(auto_error=False)


def get_current_user(
    cred: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    if cred is None or not cred.credentials:
        raise HTTPException(status_code=401, detail="未登录或登录已失效")
    try:
        payload = decode_token(cred.credentials)
    except Exception:
        raise HTTPException(status_code=401, detail="登录已过期或无效")
    user = db.get(User, payload.get("sub"))
    if user is None or not user.enabled:
        raise HTTPException(status_code=401, detail="账号不存在或已被禁用")
    return user


def require_edit(user: User = Depends(get_current_user)) -> User:
    """设备/拓扑/告警的写操作权限：admin、lab_admin。"""
    if user.role not in ("admin", "lab_admin"):
        raise HTTPException(status_code=403, detail="无权限")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    """用户管理的权限：仅 admin。"""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="无权限")
    return user