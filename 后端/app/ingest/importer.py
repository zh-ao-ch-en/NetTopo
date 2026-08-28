"""数据导入器：外部 JSON -> 校验 -> upsert 设备/拓扑（含自动布局）。

输入 JSON 约定（探测/Agent 只需产出这个结构，就无需关心后端细节）：

{
  "topology": {"id": "topo-main", "name": "网络实验室主拓扑"},   // id 可省略
  "devices": [
    {"name": "接入交换机-01", "type": "switch", "mac": "00:E0:FC:33:33:01",
     "mgmtIp": "192.168.1.11", "brand": "H3C", "model": "...", "room": "实验室1", ...}
  ],
  "links": [
    {"source": "00:E0:FC:33:33:01", "target": "00:E0:FC:11:11:01", "label": null, "style": "solid"}
  ]
}

- devices 里的 mac 是稳定唯一键，重复导入按 mac 做 upsert（有则更新、无则插入）。
- links 的 source/target 填 mac（或设备 id），导入器会解析为设备 id。
- 坐标无需提供，导入器自动布局填充。
"""
from __future__ import annotations

import json

from sqlalchemy.orm import Session

from app.constants import DEFAULT_NODE_SIZE
from app.ingest.layout import compute_layout
from app.models import Device
from app.schemas import TopologyEdgeIn, TopologyIn, TopologyNodeIn
from app.services.topology import DEFAULT_TOPOLOGY_ID, save_topology
from app.utils import gen_id, now_iso

# 设备字段 camelCase -> ORM snake_case（与设备服务保持一致）
_DEVICE_FIELD_MAP = {
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


def load_source(path: str) -> dict:
    """读取外部数据源。当前仅支持 JSON 文件；将来可换成探测工具直连、Agent 输出、队列等。"""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _upsert_device(db: Session, d: dict) -> Device:
    mac = (d.get("mac") or "").strip()
    dev = None
    if mac:
        dev = db.query(Device).filter(Device.mac == mac).first()
    if dev is None:
        dev = Device(id=gen_id("dev-"), mac=mac)
        db.add(dev)
    for camel, snake in _DEVICE_FIELD_MAP.items():
        if camel in d and d[camel] is not None:
            setattr(dev, snake, d[camel])
    # 兜底默认值
    dev.name = dev.name or d.get("name") or ""
    dev.type = dev.type or d.get("type") or "pc"
    dev.status = dev.status or "offline"
    dev.metrics = dev.metrics or {}
    dev.created_at = dev.created_at or now_iso()
    dev.updated_at = now_iso()
    return dev


def _resolve(endpoint, mac_map: dict) -> str | None:
    if not endpoint:
        return None
    return mac_map.get(endpoint, endpoint)


def import_dataset(db: Session, data: dict, algorithm: str = "spring") -> dict:
    devices_in = data.get("devices") or []
    links = data.get("links") or []
    topo_meta = data.get("topology") or {}

    # 1) upsert 设备，建立 mac -> device_id 映射
    mac_map: dict[str, str] = {}
    node_infos: list[dict] = []
    for d in devices_in:
        dev = _upsert_device(db, d)
        mac = (d.get("mac") or "").strip()
        if mac:
            mac_map[mac] = dev.id
        node_infos.append(
            {
                "id": dev.id,
                "deviceId": dev.id,
                "label": dev.name or dev.id,
                "type": dev.type or "pc",
            }
        )
    db.flush()

    # 2) 构建连线
    edges: list[dict] = []
    for i, l in enumerate(links):
        s = _resolve(l.get("source"), mac_map)
        t = _resolve(l.get("target"), mac_map)
        if not s or not t or s == t:
            continue
        edges.append(
            {
                "id": l.get("id") or f"e-{i + 1}",
                "source": s,
                "target": t,
                "label": l.get("label"),
                "style": l.get("style") or "solid",
            }
        )

    # 3) 自动布局，写入节点尺寸/坐标
    pos = compute_layout(
        [n["id"] for n in node_infos],
        [{"source": e["source"], "target": e["target"]} for e in edges],
        algorithm=algorithm,
    )
    for n in node_infos:
        size = DEFAULT_NODE_SIZE.get(n["type"], DEFAULT_NODE_SIZE["pc"])
        n["width"], n["height"] = size["width"], size["height"]
        x, y = pos.get(n["id"], (0, 0))
        n["x"], n["y"] = x, y

    # 4) 保存拓扑（复用拓扑服务，保证与契约一致）
    topo_id = topo_meta.get("id") or DEFAULT_TOPOLOGY_ID
    topo_in = TopologyIn(
        id=topo_id,
        name=topo_meta.get("name") or "",
        nodes=[
            TopologyNodeIn(
                id=n["id"],
                deviceId=n.get("deviceId"),
                label=n["label"],
                type=n["type"],
                x=n["x"],
                y=n["y"],
                width=n["width"],
                height=n["height"],
                status=n.get("status"),
            )
            for n in node_infos
        ],
        edges=[
            TopologyEdgeIn(
                id=e["id"],
                source=e["source"],
                target=e["target"],
                label=e.get("label"),
                style=e.get("style"),
            )
            for e in edges
        ],
        updatedAt=now_iso(),
    )
    result = save_topology(db, topo_in)
    db.commit()
    return result