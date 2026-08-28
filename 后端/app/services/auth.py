"""认证服务。"""
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.security import create_token, verify_password
from app.models import User
from app.serializers import user_to_dict


def login(db: Session, username: str, password: str) -> dict:
    u = db.query(User).filter(User.username == username).first()
    if u is None or not verify_password(password, u.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if not u.enabled:
        raise HTTPException(status_code=403, detail="账号已被禁用")
    token = create_token(u.id, u.role)
    return {"token": token, "user": user_to_dict(u)}