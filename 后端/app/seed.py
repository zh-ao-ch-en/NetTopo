"""种子数据：首次启动时写入一套固定的演示数据（与前端 mock 完全一致）。

数据来源：后端首次启动时若 users 表为空，则自动写入。
手动重置：在后端目录下执行  python -m app.seed
"""
from sqlalchemy.orm import Session

from app.constants import DEFAULT_NODE_SIZE
from app.core.security import hash_password
from app.database import Base, SessionLocal, engine
from app.models import (
    Alert,
    Device,
    DevicePort,
    Topology,
    TopologyEdge,
    TopologyNode,
    User,
)
from app.utils import now_iso, offset_date, today

# ---- 用户：id, username, password, display_name, role, email, phone, created_at ----
USERS = [
    ("u-001", "admin", "admin123", "系统管理员", "admin", "admin@lab.edu.cn", "13800000001", "2023-01-01"),
    ("u-002", "teacher", "teacher123", "王老师", "lab_admin", "wang@lab.edu.cn", "13800000002", "2023-02-01"),
    ("u-003", "student", "student123", "张同学", "student", "zhang@lab.edu.cn", "13800000003", "2023-03-01"),
]

# ---- 设备：完整字段（ports 为 (name, status[, connected_to]) 元组）----
DEVICES = [
    {
        "id": "dev-001", "name": "核心交换机-01", "asset_no": "ZC-2018-SW-001", "type": "switch",
        "brand": "H3C", "model": "S7506E", "mgmt_ip": "192.168.1.1", "mac": "00:E0:FC:11:11:01",
        "ports": [("GE0/0/1", "up", "dev-002"), ("GE0/0/2", "up", "dev-004"), ("GE0/0/3", "up", "dev-005"), ("XGE1/0/1", "up", "dev-006")],
        "room": "机房A", "rack": "R-01", "rack_unit": "U1-U3", "project": "核心网络",
        "serial_no": "210235A12345", "purchase_days": -2500, "warranty_days": 900, "price": 185000,
        "owner": "张工", "use_user": "网络教研组", "status": "online",
        "metrics": {"CPU": "23%", "内存": "41%", "温度": "42°C"}, "remark": "网络核心层交换机",
        "created_days": -2500, "updated_days": -30,
    },
    {
        "id": "dev-002", "name": "汇聚交换机-01", "asset_no": "ZC-2021-SW-011", "type": "switch",
        "brand": "Huawei", "model": "S5731-S48T4X", "mgmt_ip": "192.168.1.2", "mac": "00:E0:FC:22:22:01",
        "ports": [("GE0/0/1", "up", "dev-001"), ("GE0/0/2", "up", "dev-003"), ("GE0/0/3", "down")],
        "room": "机房A", "rack": "R-02", "rack_unit": "U5", "project": "核心网络",
        "serial_no": "210231B67890", "purchase_days": -1400, "warranty_days": 1200, "price": 56000,
        "owner": "张工", "use_user": "网络教研组", "status": "online",
        "metrics": {"CPU": "35%", "内存": "58%", "温度": "45°C"}, "remark": "",
        "created_days": -1400, "updated_days": -10,
    },
    {
        "id": "dev-003", "name": "汇聚交换机-02", "asset_no": "ZC-2021-SW-012", "type": "switch",
        "brand": "Huawei", "model": "S5731-S48T4X", "mgmt_ip": "192.168.1.3", "mac": "00:E0:FC:22:22:02",
        "ports": [("GE0/0/1", "up", "dev-002"), ("GE0/0/2", "up", "dev-011")],
        "room": "机房A", "rack": "R-02", "rack_unit": "U6", "project": "核心网络",
        "serial_no": "210231B67891", "purchase_days": -1400, "warranty_days": 1200, "price": 56000,
        "owner": "张工", "use_user": "网络教研组", "status": "warning",
        "metrics": {"CPU": "78%", "内存": "66%", "温度": "52°C"}, "remark": "CPU 负载偏高，需观察",
        "created_days": -1400, "updated_days": -2,
    },
    {
        "id": "dev-004", "name": "接入交换机-01", "asset_no": "ZC-2022-SW-101", "type": "switch",
        "brand": "H3C", "model": "S5130S-52P-EI", "mgmt_ip": "192.168.1.11", "mac": "00:E0:FC:33:33:01",
        "ports": [("GE0/0/1", "up", "dev-001"), ("GE0/0/2", "up", "dev-011"), ("GE0/0/3", "up", "dev-012"), ("GE0/0/4", "down")],
        "room": "实验室1", "rack": "R-10", "rack_unit": "U10", "project": "实验教学",
        "serial_no": "210345C11111", "purchase_days": -1000, "warranty_days": 1600, "price": 18000,
        "owner": "李老师", "use_user": "实验教学组", "status": "online",
        "metrics": {"CPU": "12%", "内存": "30%", "温度": "38°C"}, "remark": "",
        "created_days": -1000, "updated_days": -5,
    },
    {
        "id": "dev-005", "name": "接入交换机-02", "asset_no": "ZC-2022-SW-102", "type": "switch",
        "brand": "H3C", "model": "S5130S-52P-EI", "mgmt_ip": "192.168.1.12", "mac": "00:E0:FC:33:33:02",
        "ports": [("GE0/0/1", "up", "dev-001"), ("GE0/0/2", "up", "dev-013"), ("GE0/0/3", "down")],
        "room": "实验室2", "rack": "R-11", "rack_unit": "U10", "project": "实验教学",
        "serial_no": "210345C11112", "purchase_days": -1000, "warranty_days": 1600, "price": 18000,
        "owner": "李老师", "use_user": "实验教学组", "status": "offline",
        "metrics": {"CPU": "-", "内存": "-", "温度": "-"}, "remark": "设备离线，可能被断电",
        "created_days": -1000, "updated_days": -1,
    },
    {
        "id": "dev-006", "name": "核心路由器-01", "asset_no": "ZC-2018-RT-001", "type": "router",
        "brand": "Huawei", "model": "NE40E-X8", "mgmt_ip": "192.168.0.1", "mac": "00:E0:FC:44:44:01",
        "ports": [("XGE0/0/0", "up", "dev-001"), ("GE0/0/1", "up", "dev-007"), ("GE0/0/2", "down")],
        "room": "机房A", "rack": "R-01", "rack_unit": "U4", "project": "核心网络",
        "serial_no": "180513R00001", "purchase_days": -2800, "warranty_days": 300, "price": 320000,
        "owner": "张工", "use_user": "网络教研组", "status": "online",
        "metrics": {"CPU": "18%", "内存": "52%", "温度": "40°C"}, "remark": "核心出口路由",
        "created_days": -2800, "updated_days": -20,
    },
    {
        "id": "dev-007", "name": "出口防火墙-01", "asset_no": "ZC-2019-FW-001", "type": "firewall",
        "brand": "H3C", "model": "SecPath F1000-AI-50", "mgmt_ip": "192.168.0.254", "mac": "00:E0:FC:55:55:01",
        "ports": [("GE0/0/0", "up", "dev-006"), ("GE0/0/1", "up")],
        "room": "机房A", "rack": "R-01", "rack_unit": "U5", "project": "网络安全",
        "serial_no": "190612F00001", "purchase_days": -2200, "warranty_days": 800, "price": 128000,
        "owner": "王工", "use_user": "安全组", "status": "online",
        "metrics": {"CPU": "9%", "内存": "37%", "会话数": "12843"}, "remark": "互联网出口防火墙",
        "created_days": -2200, "updated_days": -15,
    },
    {
        "id": "dev-008", "name": "虚拟化服务器-01", "asset_no": "ZC-2020-SRV-021", "type": "server",
        "brand": "Dell", "model": "PowerEdge R750", "mgmt_ip": "192.168.2.10", "mac": "00:E0:FC:66:66:01",
        "ports": [("eth0", "up", "dev-004"), ("eth1", "up")],
        "room": "机房A", "rack": "R-03", "rack_unit": "U12-U13", "project": "云计算平台",
        "serial_no": "200811S00021", "purchase_days": -1500, "warranty_days": 1000, "price": 89000,
        "owner": "刘工", "use_user": "云计算教研组", "status": "online",
        "metrics": {"CPU": "46%", "内存": "62%", "磁盘": "71%"}, "remark": "运行 KVM 虚拟化集群",
        "created_days": -1500, "updated_days": -4,
    },
    {
        "id": "dev-009", "name": "数据库服务器-01", "asset_no": "ZC-2020-SRV-022", "type": "server",
        "brand": "Dell", "model": "PowerEdge R650", "mgmt_ip": "192.168.2.20", "mac": "00:E0:FC:66:66:02",
        "ports": [("eth0", "up", "dev-004")],
        "room": "机房A", "rack": "R-03", "rack_unit": "U14", "project": "数据服务",
        "serial_no": "200811S00022", "purchase_days": -1500, "warranty_days": 1000, "price": 96000,
        "owner": "刘工", "use_user": "数据教研组", "status": "online",
        "metrics": {"CPU": "58%", "内存": "73%", "磁盘": "66%"}, "remark": "MySQL 主库",
        "created_days": -1500, "updated_days": -3,
    },
    {
        "id": "dev-010", "name": "Web服务器-01", "asset_no": "ZC-2021-SRV-011", "type": "server",
        "brand": "HP", "model": "ProLiant DL380 Gen10", "mgmt_ip": "192.168.2.30", "mac": "00:E0:FC:77:77:01",
        "ports": [("eth0", "up", "dev-004")],
        "room": "机房A", "rack": "R-04", "rack_unit": "U10", "project": "Web服务",
        "serial_no": "210114W00011", "purchase_days": -900, "warranty_days": 1500, "price": 72000,
        "owner": "刘工", "use_user": "Web教研组", "status": "warning",
        "metrics": {"CPU": "82%", "内存": "69%", "磁盘": "84%"}, "remark": "磁盘空间告警阈值",
        "created_days": -900, "updated_days": -1,
    },
    {
        "id": "dev-011", "name": "学生工作站-01", "asset_no": "ZC-2022-PC-201", "type": "pc",
        "brand": "Lenovo", "model": "ThinkStation P350", "mgmt_ip": "192.168.3.101", "mac": "00:E0:FC:88:88:01",
        "ports": [("eth0", "up", "dev-004")],
        "room": "实验室1", "rack": "桌面工位", "rack_unit": "工位1", "project": "实验教学",
        "serial_no": "220301P00201", "purchase_days": -600, "warranty_days": 1800, "price": 12500,
        "owner": "李老师", "use_user": "学生A组", "status": "online",
        "metrics": {"CPU": "21%", "内存": "44%", "温度": "48°C"}, "remark": "",
        "created_days": -600, "updated_days": -1,
    },
    {
        "id": "dev-012", "name": "学生工作站-02", "asset_no": "ZC-2022-PC-202", "type": "pc",
        "brand": "Lenovo", "model": "ThinkStation P350", "mgmt_ip": "192.168.3.102", "mac": "00:E0:FC:88:88:02",
        "ports": [("eth0", "up", "dev-004")],
        "room": "实验室1", "rack": "桌面工位", "rack_unit": "工位2", "project": "实验教学",
        "serial_no": "220301P00202", "purchase_days": -600, "warranty_days": 1800, "price": 12500,
        "owner": "李老师", "use_user": "学生B组", "status": "online",
        "metrics": {"CPU": "15%", "内存": "38%", "温度": "45°C"}, "remark": "",
        "created_days": -600, "updated_days": -1,
    },
    {
        "id": "dev-013", "name": "学生主机-01", "asset_no": "ZC-2023-PC-301", "type": "pc",
        "brand": "HP", "model": "ProDesk 400 G9", "mgmt_ip": "192.168.3.201", "mac": "00:E0:FC:88:88:03",
        "ports": [("eth0", "up", "dev-005")],
        "room": "实验室2", "rack": "桌面工位", "rack_unit": "工位1", "project": "实验教学",
        "serial_no": "230115P00301", "purchase_days": -300, "warranty_days": 2000, "price": 6800,
        "owner": "李老师", "use_user": "学生C组", "status": "offline",
        "metrics": {"CPU": "-", "内存": "-", "温度": "-"}, "remark": "",
        "created_days": -300, "updated_days": -1,
    },
    {
        "id": "dev-014", "name": "无线AP-01", "asset_no": "ZC-2023-AP-001", "type": "ap",
        "brand": "Huawei", "model": "AirEngine 5761-11", "mgmt_ip": "192.168.4.11", "mac": "00:E0:FC:99:99:01",
        "ports": [("GE0", "up")],
        "room": "实验室1", "rack": "天花板", "rack_unit": "点位1", "project": "无线网络",
        "serial_no": "230210A00001", "purchase_days": -260, "warranty_days": 2100, "price": 3200,
        "owner": "张工", "use_user": "全体师生", "status": "online",
        "metrics": {"接入终端": "18", "信道": "36", "温度": "42°C"}, "remark": "",
        "created_days": -260, "updated_days": -1,
    },
    {
        "id": "dev-015", "name": "无线AP-02", "asset_no": "ZC-2023-AP-002", "type": "ap",
        "brand": "Huawei", "model": "AirEngine 5761-11", "mgmt_ip": "192.168.4.12", "mac": "00:E0:FC:99:99:02",
        "ports": [("GE0", "up")],
        "room": "实验室2", "rack": "天花板", "rack_unit": "点位2", "project": "无线网络",
        "serial_no": "230210A00002", "purchase_days": -260, "warranty_days": 2100, "price": 3200,
        "owner": "张工", "use_user": "全体师生", "status": "warning",
        "metrics": {"接入终端": "32", "信道": "44", "温度": "49°C"}, "remark": "接入终端偏多",
        "created_days": -260, "updated_days": -1,
    },
]

# ---- 拓扑节点：id, label, type, x, y ----
TOPOLOGY_NODES = [
    ("dev-007", "出口防火墙-01", "firewall", 400, 20),
    ("dev-006", "核心路由器-01", "router", 400, 130),
    ("dev-001", "核心交换机-01", "switch", 400, 250),
    ("dev-002", "汇聚交换机-01", "switch", 200, 370),
    ("dev-003", "汇聚交换机-02", "switch", 600, 370),
    ("dev-004", "接入交换机-01", "switch", 80, 500),
    ("dev-005", "接入交换机-02", "switch", 440, 500),
    ("dev-008", "虚拟化服务器-01", "server", 20, 650),
    ("dev-009", "数据库服务器-01", "server", 210, 650),
    ("dev-010", "Web服务器-01", "server", 400, 650),
    ("dev-011", "学生工作站-01", "pc", 590, 650),
    ("dev-012", "学生工作站-02", "pc", 780, 650),
    ("dev-013", "学生主机-01", "pc", 940, 500),
    ("dev-014", "无线AP-01", "ap", 240, 800),
    ("dev-015", "无线AP-02", "ap", 660, 800),
]

# ---- 拓扑连线：id, source, target, label, style ----
TOPOLOGY_EDGES = [
    ("e1", "dev-007", "dev-006", None, "solid"),
    ("e2", "dev-006", "dev-001", None, "solid"),
    ("e3", "dev-001", "dev-002", None, "solid"),
    ("e4", "dev-001", "dev-003", None, "solid"),
    ("e5", "dev-002", "dev-004", None, "solid"),
    ("e6", "dev-003", "dev-005", None, "solid"),
    ("e7", "dev-004", "dev-008", None, "solid"),
    ("e8", "dev-004", "dev-009", None, "solid"),
    ("e9", "dev-004", "dev-010", None, "solid"),
    ("e10", "dev-004", "dev-011", None, "solid"),
    ("e11", "dev-004", "dev-012", None, "solid"),
    ("e12", "dev-005", "dev-013", None, "solid"),
    ("e13", "dev-004", "dev-014", None, "dashed"),
    ("e14", "dev-005", "dev-015", None, "dashed"),
]

# ---- 告警：id, device_id, device_name, level, message, time(HH:mm:ss), resolved ----
ALERTS = [
    ("al-001", "dev-005", "接入交换机-02", "critical", "设备离线，疑似断电", "09:12:33", False),
    ("al-002", "dev-013", "学生主机-01", "critical", "设备离线", "09:05:11", False),
    ("al-003", "dev-010", "Web服务器-01", "warning", "磁盘使用率超过 80%", "08:56:20", False),
    ("al-004", "dev-003", "汇聚交换机-02", "warning", "CPU 负载持续偏高", "08:41:02", False),
    ("al-005", "dev-015", "无线AP-02", "info", "接入终端数较多（当前 32 台）", "08:20:47", False),
    ("al-006", "dev-002", "汇聚交换机-01", "info", "端口 GE0/0/3 状态变为 down", "07:58:09", True),
]


def _port(device_id: str, name: str, status="up", connected=None):
    # 端口 id 必须全局唯一：不同设备的物理端口名（如 GE0/0/1）会重复，需带上设备 id
    return DevicePort(
        id=f"p-{device_id}-{name}", name=name, type="1000Base-T", speed="1Gbps", status=status, connected_to=connected
    )


def _build_device(d: dict) -> Device:
    dev = Device(
        id=d["id"],
        name=d["name"],
        asset_no=d["asset_no"],
        type=d["type"],
        brand=d["brand"],
        model=d["model"],
        mgmt_ip=d["mgmt_ip"],
        mac=d["mac"],
        room=d["room"],
        rack=d["rack"],
        rack_unit=d["rack_unit"],
        project=d["project"],
        serial_no=d["serial_no"],
        purchase_date=offset_date(d["purchase_days"]),
        warranty_until=offset_date(d["warranty_days"]),
        price=d["price"],
        owner=d["owner"],
        use_user=d["use_user"],
        status=d["status"],
        metrics=d["metrics"],
        remark=d["remark"],
        created_at=offset_date(d["created_days"]),
        updated_at=offset_date(d["updated_days"]),
    )
    for p in d["ports"]:
        dev.ports.append(_port(d["id"], *p))
    return dev


def seed_all(db: Session) -> None:
    for uid, uname, pwd, disp, role, email, phone, created in USERS:
        db.add(
            User(
                id=uid,
                username=uname,
                password_hash=hash_password(pwd),
                display_name=disp,
                role=role,
                email=email,
                phone=phone,
                enabled=True,
                created_at=created,
            )
        )

    for d in DEVICES:
        db.add(_build_device(d))

    db.add(Topology(id="topo-main", name="网络实验室主拓扑", updated_at=now_iso()))

    for nid, label, ntype, x, y in TOPOLOGY_NODES:
        size = DEFAULT_NODE_SIZE[ntype]
        db.add(
            TopologyNode(
                id=nid,
                topology_id="topo-main",
                device_id=nid,
                label=label,
                type=ntype,
                x=x,
                y=y,
                width=size["width"],
                height=size["height"],
            )
        )

    for eid, src, tgt, label, style in TOPOLOGY_EDGES:
        db.add(TopologyEdge(id=eid, topology_id="topo-main", source=src, target=tgt, label=label, style=style))

    for aid, dev_id, dev_name, level, msg, time_, resolved in ALERTS:
        db.add(
            Alert(
                id=aid,
                device_id=dev_id,
                device_name=dev_name,
                level=level,
                message=msg,
                time=f"{today()}T{time_}",
                resolved=resolved,
            )
        )

    db.commit()


def seed_if_empty(db: Session) -> None:
    """首次启动时若库为空则写入种子数据（已存在则不重复写入）。"""
    if db.query(User).count() > 0:
        return
    seed_all(db)


def reset_and_seed() -> None:
    """手动重置：删库重建并写入种子数据。"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_all(db)
    print("已重置数据库并写入种子数据")


if __name__ == "__main__":
    reset_and_seed()