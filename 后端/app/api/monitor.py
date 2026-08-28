"""监控路由。"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_edit
from app.database import get_db
from app.models import User
from app.response import ok
from app.services import monitor as monitor_service

router = APIRouter(prefix="/api/monitor", tags=["monitor"])


@router.get("/summary")
def summary(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return ok(monitor_service.summary(db))


@router.get("/alerts")
def list_alerts(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return ok(monitor_service.list_alerts(db))


@router.put("/alerts/{alert_id}/resolve")
def resolve_alert(
    alert_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_edit),
):
    monitor_service.resolve_alert(db, alert_id)
    return ok()