"""设备服务。"""
from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models import Device, DevicePort, TopologyEdge, TopologyNode
from app.schemas import DeviceIn, PortIn
from app.serializers import device_to_dict
from app.utils import gen_id, now_iso

# 请求体 camelCase -> ORM 字段 snake_case 映射
_FIELD_MAP = {
    "name": "name",
    "assetNo": "asset_no",
    "type": "type",
    "brand": "brand",
    "model": "model",
    "mgmtIp": "mgmt_ip",
    "mac": "mac",
    "room": "room",
    "rack": "rack",
    "rackUnit": "rack_unit",
    "project": "project",
    "serialNo": "serial_no",
    "purchaseDate": "purchase_date",
    "warrantyUntil": "warranty_until",
    "price": "price",
    "owner": "owner",
    "useUser": "use_user",
    "status": "status",
    "metrics": "metrics",
    "remark": "remark",
}


def _make_port(p: PortIn) -> DevicePort:
    return DevicePort(
        id=p.id or gen_id("p-"),
        name=p.name,
        type=p.type,
        speed=p.speed,
        status=p.status,
        connected_to=p.connectedTo,
    )


def list_devices(
    db: Session,
    keyword: str | None = None,
    type_: str | None = None,
    status: str | None = None,
    page: int = 1,
    page_size: int = 10,
) -> dict:
    q = db.query(Device)
    if keyword:
        kw = f"%{keyword}%"
        q = q.filter(
            or_(
                Device.name.ilike(kw),
                Device.asset_no.ilike(kw),
                Device.brand.ilike(kw),
                Device.model.ilike(kw),
                Device.mgmt_ip.ilike(kw),
                Device.mac.ilike(kw),
                Device.owner.ilike(kw),
                Device.room.ilike(kw),
            )
        )
    if type_:
        q = q.filter(Device.type == type_)
    if status:
        q = q.filter(Device.status == status)
    total = q.count()
    items = q.order_by(Device.id).offset((page - 1) * page_size).limit(page_size).all()
    return {
        "list": [device_to_dict(d) for d in items],
        "total": total,
        "page": page,
        "pageSize": page_size,
    }


def list_all(db: Session) -> list:
    return [device_to_dict(d) for d in db.query(Device).order_by(Device.id).all()]


def get_device(db: Session, device_id: str) -> dict:
    dev = db.get(Device, device_id)
    if dev is None:
        raise HTTPException(status_code=404, detail="设备不存在")
    return device_to_dict(dev)


def create_device(db: Session, data: DeviceIn) -> dict:
    now = now_iso()
    dev = Device(
        id=gen_id("dev-"),
        name=data.name or "",
        asset_no=data.assetNo or "",
        type=data.type or "pc",
        brand=data.brand or "",
        model=data.model or "",
        mgmt_ip=data.mgmtIp or "",
        mac=data.mac or "",
        room=data.room or "",
        rack=data.rack or "",
        rack_unit=data.rackUnit or "",
        project=data.project or "",
        serial_no=data.serialNo or "",
        purchase_date=data.purchaseDate or "",
        warranty_until=data.warrantyUntil or "",
        price=data.price if data.price is not None else 0.0,
        owner=data.owner or "",
        use_user=data.useUser or "",
        status=data.status or "offline",
        metrics=data.metrics or {},
        remark=data.remark or "",
        created_at=now,
        updated_at=now,
    )
    if data.ports is not None:
        for p in data.ports:
            dev.ports.append(_make_port(p))
    db.add(dev)
    db.commit()
    db.refresh(dev)
    return device_to_dict(dev)


def update_device(db: Session, device_id: str, data: DeviceIn) -> dict:
    dev = db.get(Device, device_id)
    if dev is None:
        raise HTTPException(status_code=404, detail="设备不存在")
    updates = data.model_dump(exclude_unset=True)
    for camel, snake in _FIELD_MAP.items():
        if camel in updates:
            setattr(dev, snake, updates[camel])
    if "ports" in updates:
        for p in list(dev.ports):
            db.delete(p)
        db.flush()
        for p in data.ports or []:
            dev.ports.append(_make_port(p))
    dev.updated_at = now_iso()
    db.commit()
    db.refresh(dev)
    return device_to_dict(dev)


def delete_device(db: Session, device_id: str) -> None:
    dev = db.get(Device, device_id)
    if dev is None:
        raise HTTPException(status_code=404, detail="设备不存在")
    # 级联清理拓扑引用（契约要求）：删节点 + 相关连线，再删设备（端口级联删）
    node_ids = {
        n.id
        for n in db.query(TopologyNode)
        .filter((TopologyNode.device_id == device_id) | (TopologyNode.id == device_id))
        .all()
    }
    if node_ids:
        db.query(TopologyEdge).filter(
            or_(TopologyEdge.source.in_(node_ids), TopologyEdge.target.in_(node_ids))
        ).delete(synchronize_session=False)
    db.query(TopologyNode).filter(
        (TopologyNode.device_id == device_id) | (TopologyNode.id == device_id)
    ).delete(synchronize_session=False)
    db.delete(dev)
    db.commit()