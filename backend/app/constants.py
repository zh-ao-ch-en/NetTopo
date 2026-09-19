"""业务常量。字段取值与前端 src/types/index.ts 保持一一对应。"""

# 拓扑节点默认尺寸（与前端 DEFAULT_NODE_SIZE 一致）
# 警告：跨端复制常量——改动需同步前端 src/types/index.ts，否则编辑器与导入器/种子尺寸不一致
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

# 设备字段 camelCase -> ORM snake_case 映射（设备服务与数据导入器共用）
DEVICE_FIELD_MAP = {
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