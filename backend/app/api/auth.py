"""认证路由。"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.config import (
    LOGIN_ADMIN_LOCK_MINUTES,
    LOGIN_ADMIN_MAX_FAILS,
    LOGIN_IP_MAX_FAILS,
    LOGIN_LOCK_MINUTES,
    LOGIN_USER_MAX_FAILS,
)
from app.core.deps import get_current_user
from app.core.ratelimit import LoginRateLimiter, client_ip
from app.database import get_db
from app.models import User
from app.response import ok
from app.schemas import LoginIn
from app.serializers import user_to_dict
from app.services import auth as auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])

_login_limiter = LoginRateLimiter(
    ip_max_fails=LOGIN_IP_MAX_FAILS,
    user_max_fails=LOGIN_USER_MAX_FAILS,
    admin_max_fails=LOGIN_ADMIN_MAX_FAILS,
    lock_seconds=LOGIN_LOCK_MINUTES * 60,
    admin_lock_seconds=LOGIN_ADMIN_LOCK_MINUTES * 60,
)


def _remaining(db: Session, identity: dict) -> int:
    """IP 与账号任一处于锁定，即返回更大的剩余秒数。"""
    remaining = 0
    for key_type, key_value in identity.items():
        remaining = max(remaining, _login_limiter.remaining_lock(db, key_type, key_value))
    return remaining


@router.post("/login")
def login(payload: LoginIn, request: Request, db: Session = Depends(get_db)):
    ip = client_ip(request)
    remaining = _remaining(db, {"ip": ip, "user": payload.username})
    if remaining > 0:
        raise HTTPException(
            status_code=429,
            detail=f"登录失败次数过多，请 {remaining} 秒后再试",
            headers={"Retry-After": str(remaining)},
        )
    try:
        result = auth_service.login(db, payload.username, payload.password)
    except HTTPException as exc:
        if exc.status_code == 401:
            # 密码错误属爆破信号，IP 与账号都要计数
            _login_limiter.record_failure(db, "ip", ip)
            _login_limiter.record_failure(db, "user", payload.username)
        elif exc.status_code == 403:
            # 账号被禁用：仅针对该账号自身状态，非爆破信号，不消耗共享 IP 限流
            _login_limiter.record_failure(db, "user", payload.username)
        raise
    _login_limiter.reset(db, "ip", ip)
    _login_limiter.reset(db, "user", payload.username)
    return ok(result)


@router.get("/profile")
def profile(user: User = Depends(get_current_user)):
    return ok(user_to_dict(user))


@router.post("/logout")
def logout(user: User = Depends(get_current_user)):
    return ok()