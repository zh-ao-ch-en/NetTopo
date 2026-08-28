# REST API 契约文档（前端 ↔ 后端）

> 本文档为前后端接口对接的唯一依据。后端同学请按此实现接口；改动契约需双方同步更新。
> 前端类型定义见 `src/types/index.ts`，字段名与本文保持一一对应。

## 1. 总体约定

- **接口前缀**：`/api`（可通过前端 `src/config.ts` 的 `baseURL` 调整）
- **请求/响应编码**：JSON（UTF-8）
- **统一响应体**：

  ```json
  {
    "code": 0,
    "message": "ok",
    "data": {}
  }
  ```

  - `code = 0` 表示成功；非 0 表示业务错误，前端会提取 `message` 提示用户。
  - `data` 为各接口的返回对象（成功时）。

- **认证方式**：登录接口返回 `token`，后续请求在 `Authorization` 请求头携带：`Authorization: Bearer <token>`。
- **HTTP 状态码**：业务成功返回 200；未认证返回 401；无权限返回 403；其余异常返回 4xx/5xx，`message` 给出原因。
- **分页**：分页接口请求参数 `page`（从 1 开始）、`pageSize`；返回 `{ list, total, page, pageSize }`。

---

## 2. 数据模型

### 2.1 用户 User

| 字段 | 类型 | 说明 |
|---|---|---|
| id | string | 用户主键 |
| username | string | 登录用户名，唯一 |
| displayName | string | 姓名/显示名 |
| role | string | 角色：`admin` / `lab_admin` / `student` |
| email | string? | 邮箱 |
| phone | string? | 电话 |
| enabled | boolean | 是否启用 |
| createdAt | string | 创建时间 |

### 2.2 设备 Device

| 字段 | 类型 | 维度 | 说明 |
|---|---|---|---|
| id | string | — | 设备主键 |
| name | string | 基础身份 | 设备名称 |
| assetNo | string | 基础身份 | 资产编号 |
| type | string | 基础身份 | `switch`/`router`/`firewall`/`server`/`pc`/`ap` |
| brand | string | 基础身份 | 品牌 |
| model | string | 基础身份 | 型号 |
| mgmtIp | string | 网络参数 | 管理 IP |
| mac | string | 网络参数 | MAC 地址 |
| ports | DevicePort[] | 网络参数 | 端口列表 |
| room | string | 位置归属 | 机房 |
| rack | string | 位置归属 | 机柜 |
| rackUnit | string | 位置归属 | 工位/U 位 |
| project | string | 位置归属 | 所属项目/课题组 |
| serialNo | string | 资产采购 | 序列号 |
| purchaseDate | string | 资产采购 | 采购日期 |
| warrantyUntil | string | 资产采购 | 保修到期 |
| price | number | 资产采购 | 价格（元） |
| owner | string | 运维状态 | 负责人 |
| useUser | string | 运维状态 | 使用人 |
| status | string | 运维状态 | `online`/`offline`/`warning`/`error` |
| metrics | object | 运维状态 | 关键指标（键值字符串） |
| remark | string | 运维状态 | 备注 |
| createdAt / updatedAt | string | — | 时间戳 |

### 2.3 端口 DevicePort

| 字段 | 类型 | 说明 |
|---|---|---|
| id | string | 端口主键 |
| name | string | 端口名，如 `GE0/0/1` |
| type | string | 端口类型 |
| speed | string | 速率，如 `1Gbps` |
| status | string | `up` / `down` |
| connectedTo | string? | 对端设备 ID（预留联动） |

### 2.4 拓扑 TopologyData

| 字段 | 类型 | 说明 |
|---|---|---|
| id | string | 拓扑主键 |
| name | string | 拓扑名称 |
| nodes | TopologyNode[] | 节点列表 |
| edges | TopologyEdge[] | 连线列表 |
| updatedAt | string | 更新时间 |

### 2.5 拓扑节点 TopologyNode

| 字段 | 类型 | 说明 |
|---|---|---|
| id | string | 节点主键 |
| deviceId | string? | 关联设备 ID；为空表示通用节点（云/分组） |
| label | string | 显示名称 |
| type | string | 图标类型：设备 type 或 `cloud`/`group` |
| x / y | number | 左上角坐标 |
| width / height | number | 尺寸（按节点类型区分默认大小，用户可自由拉伸） |

### 2.6 拓扑连线 TopologyEdge

| 字段 | 类型 | 说明 |
|---|---|---|
| id | string | 连线主键 |
| source | string | 起始节点 ID |
| target | string | 终止节点 ID |
| label | string? | 标签 |
| style | string | `solid` / `dashed` |

### 2.7 告警 Alert

| 字段 | 类型 | 说明 |
|---|---|---|
| id | string | 告警主键 |
| deviceId | string? | 关联设备 ID |
| deviceName | string | 设备名称 |
| level | string | `info` / `warning` / `critical` |
| message | string | 告警内容 |
| time | string | 发生时间 |
| resolved | boolean | 是否已处理 |

---

## 3. 接口清单

### 3.1 认证

| 方法 | 路径 | 说明 | 权限 |
|---|---|---|---|
| POST | `/api/auth/login` | 登录 | 公开 |
| GET | `/api/auth/profile` | 获取当前用户 | 登录 |
| POST | `/api/auth/logout` | 退出登录 | 登录 |

**登录请求**：`{ "username": "admin", "password": "admin123" }`
**登录返回**：`{ "token": "...", "user": { User } }`

### 3.2 设备

| 方法 | 路径 | 说明 | 权限 |
|---|---|---|---|
| GET | `/api/devices` | 分页查询 | 登录 |
| GET | `/api/devices/all` | 全部设备（拓扑设备库） | 登录 |
| GET | `/api/devices/:id` | 设备详情 | 登录 |
| POST | `/api/devices` | 创建设备 | 编辑 |
| PUT | `/api/devices/:id` | 更新设备 | 编辑 |
| DELETE | `/api/devices/:id` | 删除设备（需级联清理拓扑引用） | 编辑 |

**GET /api/devices 查询参数**：`keyword`（模糊）、`type`、`status`、`page`、`pageSize`。

### 3.3 拓扑

| 方法 | 路径 | 说明 | 权限 |
|---|---|---|---|
| GET | `/api/topology` | 获取拓扑 | 登录 |
| PUT | `/api/topology` | 整体保存拓扑 | 编辑 |

### 3.4 监控

| 方法 | 路径 | 说明 | 权限 |
|---|---|---|---|
| GET | `/api/monitor/summary` | 状态统计 | 登录 |
| GET | `/api/monitor/alerts` | 告警列表 | 登录 |
| PUT | `/api/monitor/alerts/:id/resolve` | 处理告警 | 编辑 |

**summary 返回**：`{ "total": n, "online": n, "offline": n, "warning": n, "error": n }`

### 3.5 用户（仅系统管理员）

| 方法 | 路径 | 说明 | 权限 |
|---|---|---|---|
| GET | `/api/users` | 用户列表 | 管理员 |
| POST | `/api/users` | 创建用户 | 管理员 |
| PUT | `/api/users/:id` | 更新用户 | 管理员 |
| DELETE | `/api/users/:id` | 删除用户 | 管理员 |

---

## 4. 权限矩阵

| 能力 | admin | lab_admin | student |
|---|:---:|:---:|:---:|
| 查看设备/拓扑/监控 | ✓ | ✓ | ✓ |
| 编辑设备/拓扑/处理告警 | ✓ | ✓ | ✗ |
| 用户/角色管理 | ✓ | ✗ | ✗ |

后端需在**服务端**做同等鉴权校验（前端仅做界面层控制）。

---

## 5. 预留扩展

- **拓扑 ↔ 设备联动**：`TopologyNode.deviceId` 已关联设备，可扩展「在拓扑中修改设备、台账同步更新」。
- **端口管理**：`Device.ports` 已建模，可补充独立端口 CRUD 接口（如 `POST /api/devices/:id/ports`）。
- **实时监控**：可后期以 WebSocket 推送替代轮询（现有接口结构不变）。