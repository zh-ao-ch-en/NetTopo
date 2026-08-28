"""监控服务：状态统计、告警列表、处理告警。"""
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Alert, Device
from app.serializers import alert_to_dict


def summary(db: Session) -> dict:
    s = {"total": 0, "online": 0, "offline": 0, "warning": 0, "error": 0}
    for dev in db.query(Device).all():
        s["total"] += 1
        if dev.status in s:
            s[dev.status] += 1
    return s


def list_alerts(db: Session) -> list:
    alerts = db.query(Alert).order_by(Alert.time.desc()).all()
    return [alert_to_dict(a) for a in alerts]


def resolve_alert(db: Session, alert_id: str) -> None:
    a = db.get(Alert, alert_id)
    if a is None:
        raise HTTPException(status_code=404, detail="告警不存在")
    a.resolved = True
    db.commit()