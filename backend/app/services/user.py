"""用户服务（仅系统管理员）。"""
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models import User
from app.schemas import UserIn
from app.serializers import user_to_dict
from app.utils import gen_id, now


def list_users(db: Session) -> list:
    return [user_to_dict(u) for u in db.query(User).order_by(User.id).all()]


def _is_last_enabled_admin(db: Session, exclude_user_id: str) -> bool:
    return (
        db.query(User)
        .filter(User.role == "admin", User.enabled.is_(True), User.id != exclude_user_id)
        .count()
        == 0
    )


def create_user(db: Session, data: UserIn) -> dict:
    username = (data.username or "").strip()
    if not username:
        raise HTTPException(status_code=400, detail="用户名不能为空")
    if not data.password:
        raise HTTPException(status_code=400, detail="密码不能为空")
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    u = User(
        id=gen_id("u-"),
        username=username,
        password_hash=hash_password(data.password),
        display_name=data.displayName or "",
        role=data.role or "student",
        email=data.email,
        phone=data.phone,
        enabled=data.enabled if data.enabled is not None else True,
        created_at=now(),
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return user_to_dict(u)


def update_user(db: Session, user_id: str, data: UserIn, current_user: User) -> dict:
    u = db.get(User, user_id)
    if u is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    updates = data.model_dump(exclude_unset=True)
    if "username" in updates and updates["username"] != u.username:
        new_name = (updates["username"] or "").strip()
        if not new_name:
            raise HTTPException(status_code=400, detail="用户名不能为空")
        if db.query(User).filter(User.username == new_name).first():
            raise HTTPException(status_code=400, detail="用户名已存在")
        u.username = new_name
    if "displayName" in updates:
        u.display_name = updates["displayName"]
    if "role" in updates and updates["role"] != u.role:
        if user_id == current_user.id and updates["role"] != "admin":
            raise HTTPException(status_code=403, detail="禁止降低当前登录账号的权限")
        if u.role == "admin" and updates["role"] != "admin" and _is_last_enabled_admin(db, u.id):
            raise HTTPException(status_code=403, detail="禁止降级最后一个启用的管理员")
        u.role = updates["role"]
    if "email" in updates:
        u.email = updates["email"]
    if "phone" in updates:
        u.phone = updates["phone"]
    if "enabled" in updates:
        if user_id == current_user.id and not updates["enabled"]:
            raise HTTPException(status_code=403, detail="禁止禁用当前登录账号")
        if u.role == "admin" and not updates["enabled"] and _is_last_enabled_admin(db, u.id):
            raise HTTPException(status_code=403, detail="禁止禁用最后一个启用的管理员")
        u.enabled = updates["enabled"]
    if updates.get("password"):
        u.password_hash = hash_password(updates["password"])
    db.commit()
    db.refresh(u)
    return user_to_dict(u)


def delete_user(db: Session, user_id: str, current_user: User) -> None:
    u = db.get(User, user_id)
    if u is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    if u.id == current_user.id:
        raise HTTPException(status_code=403, detail="禁止删除当前登录账号")
    if u.role == "admin" and _is_last_enabled_admin(db, u.id):
        raise HTTPException(status_code=403, detail="禁止删除最后一个启用的管理员")
    db.delete(u)
    db.commit()