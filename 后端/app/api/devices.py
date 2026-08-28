"""设备路由。"""
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_edit
from app.database import get_db
from app.models import User
from app.response import ok
from app.schemas import DeviceIn
from app.services import device as device_service

router = APIRouter(prefix="/api/devices", tags=["devices"])


@router.get("")
def list_devices(
    keyword: Optional[str] = None,
    type: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    pageSize: int = 10,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return ok(device_service.list_devices(db, keyword, type, status, page, pageSize))


@router.get("/all")
def list_all(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return ok(device_service.list_all(db))


@router.get("/{device_id}")
def get_device(
    device_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return ok(device_service.get_device(db, device_id))


@router.post("")
def create_device(
    data: DeviceIn,
    db: Session = Depends(get_db),
    user: User = Depends(require_edit),
):
    return ok(device_service.create_device(db, data))


@router.put("/{device_id}")
def update_device(
    device_id: str,
    data: DeviceIn,
    db: Session = Depends(get_db),
    user: User = Depends(require_edit),
):
    return ok(device_service.update_device(db, device_id, data))


@router.delete("/{device_id}")
def delete_device(
    device_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_edit),
):
    device_service.delete_device(db, device_id)
    return ok()