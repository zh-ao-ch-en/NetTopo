# 网络实验室拓扑与设备管理系统 · 前端

Vue3 + Vite + TypeScript 实现的前端，配合本地 mock 数据层，可独立运行与演示。后端就绪后可无缝切换为真实接口。

## 技术栈

- **框架**：Vue 3（Composition API + `<script setup>`）
- **构建**：Vite 6
- **语言**：TypeScript 5
- **UI 组件**：Element Plus（含暗色主题）
- **状态管理**：Pinia
- **路由**：Vue Router 4（Hash 模式）
- **请求**：axios（统一封装，附加 Bearer token）
- **拓扑图**：自研 SVG 画布（缩放/平移/拖拽/连线，无重型图形库依赖）

## 快速开始

```bash
# 安装依赖（Node 18+，推荐 Node 20/22）
npm install

# 启动开发服务器（默认 http://localhost:5173）
npm run dev

# 生产构建（输出到 dist/）
npm run build

# 预览构建产物
npm run preview
```

> 若 PowerShell 提示 npm.ps1 执行策略禁止，请改用 `npm.cmd`，或以管理员运行
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`。

## 演示账号（当前 mock 阶段）

| 角色 | 用户名 | 密码 | 权限 |
|---|---|---|---|
| 系统管理员 | `admin` | `admin123` | 全部权限，含用户管理 |
| 实验室管理员 | `teacher` | `teacher123` | 设备/拓扑编辑，不管用户 |
| 普通使用者 | `student` | `student123` | 只读 |

## 功能模块

1. **状态监控**：设备状态统计卡片 + 告警列表（可处理告警）
2. **设备管理**：设备台账增删改查、关键字/类型/状态筛选、详情抽屉（端口、指标）
3. **拓扑查看**：拓扑图缩放/平移，节点按设备类型区分默认大小，点击设备自动跳转到设备管理并展示详情
4. **拓扑编辑**：拖拽布局、设备库添加节点、节点自由拉伸、连线、保存/导出/导入 JSON、自动保存
5. **用户管理**：仅管理员，账号/角色管理
6. **主题切换**：深色科技风（默认）/ 浅色，一键切换
7. **响应式适配**：桌面/平板/手机自适应，移动端侧栏抽屉化、面板纵向堆叠

## 目录结构

```
前端/
├── index.html
├── vite.config.ts
├── package.json
├── docs/
│   └── api-contract.md          # REST API 契约（后端同学对接依据）
└── src/
    ├── main.ts                  # 入口
    ├── config.ts                # 全局配置（mock 开关、接口前缀等）
    ├── types/index.ts           # 共享类型与数据模型
    ├── router/index.ts          # 路由 + 登录/权限守卫
    ├── stores/                  # Pinia 状态（认证、主题）
    ├── api/                     # 数据访问层（前端↔后端边界）
    │   ├── http.ts              #   axios 实例与统一封装
    │   ├── auth.ts / device.ts / topology.ts / monitor.ts / user.ts
    ├── mock/                    # 本地 mock 实现（后端接入后可整体移除）
    │   ├── db.ts                #   内存 + localStorage 模拟数据库
    │   ├── api.ts               #   各接口的 mock 实现
    │   └── devices/users/topology/monitor.ts  # 种子数据
    ├── components/
    │   ├── layout/              # 布局（侧栏/顶栏）
    │   ├── topology/TopologyCanvas.vue  # 拓扑渲染核心
    │   └── DeviceIcon.vue       # 设备 SVG 图标
    ├── views/                   # 页面（登录/监控/设备/拓扑/用户）
    └── utils/                   # 工具（存储、权限、常量等）
```

## 后端接入说明（关键）

前端与后端的**唯一边界**是 `src/api/` 目录。每个服务函数都遵循同一模式：

```ts
export function listDevices(q = {}): Promise<PageResult<Device>> {
  if (API_CONFIG.useMock) return mockListDevices(q)   // 当前走 mock
  return request({ url: '/devices', method: 'GET', params: q })  // 真实后端
}
```

接入后端只需两步：

1. 修改 `src/config.ts`：将 `useMock` 置为 `false`，配置 `baseURL`。
2. 后端按 `docs/api-contract.md` 实现接口，返回体统一为 `{ code, message, data }`。

前端所有类型定义集中在 `src/types/index.ts`，后端同学可据此对齐数据模型。
后续如需实现「拓扑 ↔ 设备台账」双向联动，只需利用 `TopologyNode.deviceId` 字段（已预留）打通两端。

## 数据持久化说明（mock 阶段）

- 设备、拓扑、告警、用户通过 `src/mock/db.ts` 持久化到浏览器 `localStorage`（键 `lab_mock_db`）。
- 登录 token 与用户信息存于 `lab_token` / `lab_user`。
- 主题存于 `lab_theme`。
- 如需恢复初始演示数据，可在浏览器控制台删除 `lab_mock_db` 后刷新，或使用编辑器「重置拓扑」。