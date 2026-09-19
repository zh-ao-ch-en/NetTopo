"""SQLAlchemy 数据模型（表结构 = 拆表方案 B）。

对外接口仍严格按契约返回/接收，这里只是库内部的物理存储形态。
"""
from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String)
    display_name: Mapped[str] = mapped_column(String, default="")
    role: Mapped[str] = mapped_column(String, default="student")  # admin/lab_admin/student
    email: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    # 基础身份
    name: Mapped[str] = mapped_column(String, default="")
    asset_no: Mapped[str] = mapped_column(String, default="")
    type: Mapped[str] = mapped_column(String, default="pc")
    brand: Mapped[str] = mapped_column(String, default="")
    model: Mapped[str] = mapped_column(String, default="")
    # 网络参数
    mgmt_ip: Mapped[str] = mapped_column(String, default="")
    mac: Mapped[str] = mapped_column(String, default="", index=True)
    # 位置与归属
    room: Mapped[str] = mapped_column(String, default="")
    rack: Mapped[str] = mapped_column(String, default="")
    rack_unit: Mapped[str] = mapped_column(String, default="")
    project: Mapped[str] = mapped_column(String, default="")
    # 资产/采购
    serial_no: Mapped[str] = mapped_column(String, default="")
    purchase_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    warranty_until: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    price: Mapped[float] = mapped_column(Float, default=0)
    # 运维状态
    owner: Mapped[str] = mapped_column(String, default="")
    use_user: Mapped[str] = mapped_column(String, default="")
    status: Mapped[str] = mapped_column(String, default="offline")  # online/offline/warning/error
    metrics: Mapped[dict] = mapped_column(JSON, default=dict)
    remark: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    ports: Mapped[list["DevicePort"]] = relationship(
        back_populates="device",
        cascade="all, delete-orphan",
        order_by="DevicePort.id",
    )


class DevicePort(Base):
    __tablename__ = "device_ports"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    device_id: Mapped[str] = mapped_column(ForeignKey("devices.id"), index=True)
    name: Mapped[str] = mapped_column(String, default="")
    type: Mapped[str] = mapped_column(String, default="")
    speed: Mapped[str] = mapped_column(String, default="")
    status: Mapped[str] = mapped_column(String, default="down")  # up/down
    connected_to: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    device: Mapped["Device"] = relationship(back_populates="ports")


class Topology(Base):
    __tablename__ = "topologies"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, default="")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


class TopologyNode(Base):
    __tablename__ = "topology_nodes"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    topology_id: Mapped[str] = mapped_column(ForeignKey("topologies.id"), index=True)
    device_id: Mapped[Optional[str]] = mapped_column(
        String, ForeignKey("devices.id", ondelete="SET NULL"), nullable=True, index=True
    )
    label: Mapped[str] = mapped_column(String, default="")
    type: Mapped[str] = mapped_column(String, default="")
    x: Mapped[float] = mapped_column(Float, default=0)
    y: Mapped[float] = mapped_column(Float, default=0)
    width: Mapped[float] = mapped_column(Float, default=0)
    height: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[Optional[str]] = mapped_column(String, nullable=True)


class TopologyEdge(Base):
    __tablename__ = "topology_edges"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    topology_id: Mapped[str] = mapped_column(ForeignKey("topologies.id"), index=True)
    source: Mapped[str] = mapped_column(String, index=True)
    target: Mapped[str] = mapped_column(String, index=True)
    label: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    style: Mapped[Optional[str]] = mapped_column(String, nullable=True)


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    device_id: Mapped[Optional[str]] = mapped_column(
        String, ForeignKey("devices.id", ondelete="SET NULL"), nullable=True
    )
    device_name: Mapped[str] = mapped_column(String, default="")
    level: Mapped[str] = mapped_column(String, default="info")  # info/warning/critical
    message: Mapped[str] = mapped_column(Text, default="")
    time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)


class LoginAttempt(Base):
    """登录限流计数：按 key_type(ip/user) + key_value 记录失败次数与锁定。

    存数据库而非进程内存，保证多 worker / 多实例部署时计数共享。
    时间字段用 epoch 秒（整数）便于跨平台比较。
    """

    __tablename__ = "login_attempts"
    __table_args__ = (UniqueConstraint("key_type", "key_value", name="uq_login_attempts"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: uuid.uuid4().hex)
    key_type: Mapped[str] = mapped_column(String(16), index=True)  # 'ip' | 'user'
    key_value: Mapped[str] = mapped_column(String(255), index=True)
    fail_count: Mapped[int] = mapped_column(Integer, default=0)
    last_fail_at: Mapped[int] = mapped_column(Integer, default=0)  # epoch 秒
    locked_until: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # epoch 秒