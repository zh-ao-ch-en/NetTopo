"""业务常量。字段取值与前端 src/types/index.ts 保持一一对应。"""

# 设备类型中文名
DEVICE_TYPE_NAME = {
    "switch": "交换机",
    "router": "路由器",
    "firewall": "防火墙",
    "server": "服务器",
    "pc": "主机/PC",
    "ap": "无线AP",
}

# 拓扑节点默认尺寸（与前端 DEFAULT_NODE_SIZE 一致）
DEFAULT_NODE_SIZE = {
    "firewall": {"width": 200, "height": 84},
    "router": {"width": 200, "height": 84},
    "switch": {"width": 180, "height": 76},
    "server": {"width": 160, "height": 72},
    "pc": {"width": 150, "height": 64},
    "ap": {"width": 132, "height": 60},
    "cloud": {"width": 180, "height": 96},
    "group": {"width": 260, "height": 160},
}

# 角色权限（前端仅做界面控制，后端必须据此做服务端鉴权）
ROLE_PERMISSIONS = {
    "admin": {"edit": True, "manage_users": True},
    "lab_admin": {"edit": True, "manage_users": False},
    "student": {"edit": False, "manage_users": False},
}