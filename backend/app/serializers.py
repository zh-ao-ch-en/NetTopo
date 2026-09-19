"""ORM 对象 -> 契约 JSON 的序列化（字段名转为前端 camelCase）。"""
from __future__ import annotations

from app.models import Alert, Device, DevicePort, User
from app.utils import fmt


def port_to_dict(p: DevicePort) -> dict:
    d = {
        "id": p.id,
        "name": p.name,
        "type": p.type,
        "speed": p.speed,
        "status": p.status,
    }
    if p.connected_to is not None:
        d["connectedTo"] = p.connected_to
    return d


def device_to_dict(dev: Device, include_ports: bool = True) -> dict:
    d = {
        "id": dev.id,
        "name": dev.name,
        "assetNo": dev.asset_no,
        "type": dev.type,
        "brand": dev.brand,
        "model": dev.model,
        "mgmtIp": dev.mgmt_ip,
        "mac": dev.mac,
        "room": dev.room,
        "rack": dev.rack,
        "rackUnit": dev.rack_unit,
        "project": dev.project,
        "serialNo": dev.serial_no,
        "purchaseDate": fmt(dev.purchase_date),
        "warrantyUntil": fmt(dev.warranty_until),
        "price": dev.price,
        "owner": dev.owner,
        "useUser": dev.use_user,
        "status": dev.status,
        "metrics": dev.metrics or {},
        "remark": dev.remark,
        "createdAt": fmt(dev.created_at),
        "updatedAt": fmt(dev.updated_at),
    }
    if include_ports:
        d["ports"] = [port_to_dict(p) for p in dev.ports]
    return d


def user_to_dict(u: User) -> dict:
    d = {
        "id": u.id,
        "username": u.username,
        "displayName": u.display_name,
        "role": u.role,
        "enabled": u.enabled,
        "createdAt": fmt(u.created_at),
    }
    if u.email is not None:
        d["email"] = u.email
    if u.phone is not None:
        d["phone"] = u.phone
    return d


def alert_to_dict(a: Alert) -> dict:
    d = {
        "id": a.id,
        "deviceName": a.device_name,
        "level": a.level,
        "message": a.message,
        "time": fmt(a.time),
        "resolved": a.resolved,
    }
    if a.device_id is not None:
        d["deviceId"] = a.device_id
    return d