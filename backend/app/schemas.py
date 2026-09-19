"""Pydantic 请求模型（字段名与前端提交的 JSON 保持 camelCase 一致）。"""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class LoginIn(BaseModel):
    username: str
    password: str


class PortIn(BaseModel):
    id: Optional[str] = None
    name: str = ""
    type: str = ""
    speed: str = ""
    status: str = "down"
    connectedTo: Optional[str] = None


class DeviceIn(BaseModel):
    """创建/更新设备的请求体。全部字段可选，未传字段在创建时取默认值。"""

    name: Optional[str] = None
    assetNo: Optional[str] = None
    type: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    mgmtIp: Optional[str] = None
    mac: Optional[str] = None
    ports: Optional[list[PortIn]] = None
    room: Optional[str] = None
    rack: Optional[str] = None
    rackUnit: Optional[str] = None
    project: Optional[str] = None
    serialNo: Optional[str] = None
    purchaseDate: Optional[str] = None
    warrantyUntil: Optional[str] = None
    price: Optional[float] = None
    owner: Optional[str] = None
    useUser: Optional[str] = None
    status: Optional[str] = None
    metrics: Optional[dict] = None
    remark: Optional[str] = None


class UserIn(BaseModel):
    username: Optional[str] = None
    displayName: Optional[str] = None
    # 角色白名单（与前端 Role 及后端 deps 一致），非法值直接 422
    role: Optional[Literal["admin", "lab_admin", "student"]] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    enabled: Optional[bool] = None
    # 密码仅在提供时校验最短长度；创建账号的密码必填校验由 services/user 负责
    password: Optional[str] = Field(default=None, min_length=8)


class TopologyNodeIn(BaseModel):
    id: str
    deviceId: Optional[str] = None
    label: str = ""
    type: str = ""
    x: float = 0
    y: float = 0
    width: float = 0
    height: float = 0
    status: Optional[str] = None


class TopologyEdgeIn(BaseModel):
    id: str
    source: str
    target: str
    label: Optional[str] = None
    style: Optional[str] = None


class TopologyIn(BaseModel):
    id: Optional[str] = None
    name: str = ""
    nodes: list[TopologyNodeIn] = []
    edges: list[TopologyEdgeIn] = []
    updatedAt: Optional[str] = None