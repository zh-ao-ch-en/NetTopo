# 网络实验室拓扑与设备管理系统 · 后端

FastAPI + SQLAlchemy 2.x + SQLite（可切 MySQL）实现的后端，为前端提供 REST API。
接口严格遵循前端 `docs/api-contract.md`，统一返回 `{ code, message, data }`。

## 技术栈

- **框架**：FastAPI
- **ORM**：SQLAlchemy 2.x（SQLite 起步，换 MySQL 只改连接串）
- **鉴权**：JWT（Bearer）+ bcrypt 密码哈希
- **自动布局**（预留）：networkx

## 快速开始

```bash
cd 后端
python -m venv .venv
# Windows 激活： .venv\Scripts\activate
pip install -r requirements.txt

# 启动（首次启动自动建表并写入种子数据）
uvicorn app.main:app --reload --port 8000

# 接口文档（自动生成）
#   http://127.0.0.1:8000/docs
```

> Python 需 3.10+。

## 重置/重灌种子数据

```bash
cd 后端
python -m app.seed
```

首次启动时若 `users` 表为空（新库）会自动写入种子数据：
- 3 个账号：`admin/admin123`（管理员）、`teacher/teacher123`（实验室管理员）、`student/student123`（只读）
- 15 台设备、1 张拓扑（15 节点 + 14 连线）、6 条告警

## 目录结构

```
后端/
├── requirements.txt
├── .env.example
└── app/
    ├── main.py            # FastAPI 入口（CORS、异常处理、启动种子）
    ├── config.py          # 环境变量配置
    ├── database.py        # 引擎、会话、Base
    ├── models.py          # SQLAlchemy 表结构（7 张表）
    ├── schemas.py         # Pydantic 请求模型
    ├── serializers.py     # ORM -> 契约 JSON
    ├── response.py        # 统一响应体
    ├── constants.py       # 设备类型/节点尺寸/权限
    ├── utils.py           # ID/时间工具
    ├── seed.py            # 种子数据（固定演示数据）
    ├── core/
    │   ├── security.py    # JWT + bcrypt
    │   └── deps.py        # get_current_user / require_edit / require_admin
    ├── services/          # 业务逻辑（auth/device/topology/monitor/user）
    ├── api/               # 路由层（认证/设备/拓扑/监控/用户）
    └── ingest/            # 数据导入器（暂不启用，供未来探测→Agent→写库用）
        ├── layout.py      #   自动布局
        ├── importer.py    #   外部 JSON -> upsert
        └── __main__.py    #   python -m app.ingest <dataset.json>
```

## API 概览（对应契约 15 个端点）

| 方法 | 路径 | 说明 | 权限 |
|---|---|---|---|
| POST | `/api/auth/login` | 登录 | 公开 |
| GET | `/api/auth/profile` | 当前用户 | 登录 |
| POST | `/api/auth/logout` | 退出 | 登录 |
| GET | `/api/devices` | 设备分页查询 | 登录 |
| GET | `/api/devices/all` | 全部设备 | 登录 |
| GET | `/api/devices/{id}` | 设备详情 | 登录 |
| POST | `/api/devices` | 创建设备 | 编辑 |
| PUT | `/api/devices/{id}` | 更新设备 | 编辑 |
| DELETE | `/api/devices/{id}` | 删除设备（级联清拓扑） | 编辑 |
| GET | `/api/topology` | 获取拓扑 | 登录 |
| PUT | `/api/topology` | 整体保存拓扑 | 编辑 |
| GET | `/api/monitor/summary` | 状态统计 | 登录 |
| GET | `/api/monitor/alerts` | 告警列表 | 登录 |
| PUT | `/api/monitor/alerts/{id}/resolve` | 处理告警 | 编辑 |
| GET/POST/PUT/DELETE | `/api/users` | 用户管理 | 仅 admin |

## 数据进入方式（留足扩展空间）

后端**只负责从数据库读**。数据写入有两种途径：

1. **现在**：`python -m app.seed` 写入固定演示数据。
2. **未来**：探测工具扫描局域网 → Agent 清洗/纠错 → 输出 JSON → `python -m app.ingest <dataset.json>` 导入（按 mac 做 upsert，自动布局补坐标）。

导入器位于 `app/ingest`，当前不影响任何正在运行的接口。