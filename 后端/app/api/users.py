"""用户管理路由（仅系统管理员）。"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import require_admin
from app.database import get_db
from app.models import User
from app.response import ok
from app.schemas import UserIn
from app.services import user as user_service

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("")
def list_users(
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    return ok(user_service.list_users(db))


@router.post("")
def create_user(
    data: UserIn,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    return ok(user_service.create_user(db, data))


@router.put("/{user_id}")
def update_user(
    user_id: str,
    data: UserIn,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    return ok(user_service.update_user(db, user_id, data))


@router.delete("/{user_id}")
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    user_service.delete_user(db, user_id)
    return ok()