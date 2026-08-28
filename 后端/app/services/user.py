"""用户服务（仅系统管理员）。"""
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models import User
from app.schemas import UserIn
from app.serializers import user_to_dict
from app.utils import gen_id, today


def list_users(db: Session) -> list:
    return [user_to_dict(u) for u in db.query(User).order_by(User.id).all()]


def create_user(db: Session, data: UserIn) -> dict:
    username = data.username or ""
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    u = User(
        id=gen_id("u-"),
        username=username,
        password_hash=hash_password(data.password or ""),
        display_name=data.displayName or "",
        role=data.role or "student",
        email=data.email,
        phone=data.phone,
        enabled=data.enabled if data.enabled is not None else True,
        created_at=today(),
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return user_to_dict(u)


def update_user(db: Session, user_id: str, data: UserIn) -> dict:
    u = db.get(User, user_id)
    if u is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    updates = data.model_dump(exclude_unset=True)
    if "username" in updates and updates["username"] != u.username:
        if db.query(User).filter(User.username == updates["username"]).first():
            raise HTTPException(status_code=400, detail="用户名已存在")
        u.username = updates["username"]
    if "displayName" in updates:
        u.display_name = updates["displayName"]
    if "role" in updates:
        u.role = updates["role"]
    if "email" in updates:
        u.email = updates["email"]
    if "phone" in updates:
        u.phone = updates["phone"]
    if "enabled" in updates:
        u.enabled = updates["enabled"]
    if updates.get("password"):
        u.password_hash = hash_password(updates["password"])
    db.commit()
    db.refresh(u)
    return user_to_dict(u)


def delete_user(db: Session, user_id: str) -> None:
    u = db.get(User, user_id)
    if u is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    db.delete(u)
    db.commit()