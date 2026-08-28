"""认证路由。"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models import User
from app.response import ok
from app.schemas import LoginIn
from app.serializers import user_to_dict
from app.services import auth as auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login")
def login(payload: LoginIn, db: Session = Depends(get_db)):
    return ok(auth_service.login(db, payload.username, payload.password))


@router.get("/profile")
def profile(user: User = Depends(get_current_user)):
    return ok(user_to_dict(user))


@router.post("/logout")
def logout(user: User = Depends(get_current_user)):
    return ok()