// ============================================================
// 全局类型定义（前后端共享的数据契约，后端同学对接时以本文件为准）
// ============================================================

/** 用户角色 */
export type Role = 'admin' | 'lab_admin' | 'student'

/** 用户 */
export interface User {
  id: string
  username: string
  displayName: string
  role: Role
  email?: string
  phone?: string
  enabled: boolean
  createdAt: string
}

/** 登录请求体 */
export interface LoginPayload {
  username: string
  password: string
}

/** 登录返回 */
export interface LoginResult {
  token: string
  user: User
}

/** 设备类型（拓扑图标与设备台账共用） */
export type DeviceType = 'switch' | 'router' | 'firewall' | 'server' | 'pc' | 'ap'

/** 设备类型的中文名映射 */
export const DEVICE_TYPE_NAME: Record<DeviceType, string> = {
  switch: '交换机',
  router: '路由器',
  firewall: '防火墙',
  server: '服务器',
  pc: '主机/PC',
  ap: '无线AP',
}

/** 端口 */
export interface DevicePort {
  id: string
  name: string // 端口名，如 GE0/0/1
  type: string // 端口类型，如 1000Base-T
  speed: string // 速率，如 1Gbps
  status: 'up' | 'down'
  connectedTo?: string // 对端设备ID（预留）
}

/** 设备运行状态 */
export type DeviceStatus = 'online' | 'offline' | 'warning' | 'error'

/** 设备台账（5 维度字段） */
export interface Device {
  id: string
  // 基础身份
  name: string
  assetNo: string // 资产编号
  type: DeviceType
  brand: string // 品牌
  model: string // 型号
  // 网络参数
  mgmtIp: string // 管理IP
  mac: string
  ports: DevicePort[]
  // 位置与归属
  room: string // 机房
  rack: string // 机柜
  rackUnit: string // 工位/U位
  project: string // 所属项目/课题组
  // 资产/采购
  serialNo: string // 序列号
  purchaseDate: string // 采购日期
  warrantyUntil: string // 保修到期
  price: number // 价格
  // 运维状态
  owner: string // 负责人
  useUser: string // 使用人
  status: DeviceStatus
  metrics: Record<string, string> // 关键指标（CPU/内存/温度等）
  remark: string
  createdAt: string
  updatedAt: string
}

/** 拓扑节点类型（设备类型 + 云/分组） */
export type NodeType = DeviceType | 'cloud' | 'group'

/** 不同节点类型的默认尺寸（在画布上区分设备大小，用户可自由拉伸） */
export const DEFAULT_NODE_SIZE: Record<NodeType, { width: number; height: number }> = {
  firewall: { width: 200, height: 84 },
  router: { width: 200, height: 84 },
  switch: { width: 180, height: 76 },
  server: { width: 160, height: 72 },
  pc: { width: 150, height: 64 },
  ap: { width: 132, height: 60 },
  cloud: { width: 180, height: 96 },
  group: { width: 260, height: 160 },
}

/** 拓扑节点（可选 deviceId 用于与设备台账联动，为后续双向同步预留） */
export interface TopologyNode {
  id: string
  deviceId?: string // 关联的设备台账ID（预留）
  label: string
  type: NodeType
  x: number
  y: number
  width: number
  height: number
  status?: DeviceStatus
}

/** 拓扑连线 */
export interface TopologyEdge {
  id: string
  source: string // 起始节点ID
  target: string // 终止节点ID
  label?: string
  style?: 'solid' | 'dashed'
}

/** 拓扑图数据（可保存/加载/导入导出的最小单元） */
export interface TopologyData {
  id: string
  name: string
  nodes: TopologyNode[]
  edges: TopologyEdge[]
  updatedAt: string
}

/** 告警级别 */
export type AlertLevel = 'info' | 'warning' | 'critical'

/** 告警 */
export interface Alert {
  id: string
  deviceId?: string
  deviceName: string
  level: AlertLevel
  message: string
  time: string
  resolved: boolean
}

/** 分页返回 */
export interface PageResult<T> {
  list: T[]
  total: number
  page: number
  pageSize: number
}

/** 接口通用响应体 */
export interface ApiResponse<T = unknown> {
  code: number // 0 表示成功，非 0 表示业务错误
  message: string
  data: T
}

/** 角色权限位定义（前端做页面/按钮级控制，后端需据此做服务端鉴权） */
export const ROLE_PERMISSIONS: Record<Role, { edit: boolean; manageUsers: boolean }> = {
  admin: { edit: true, manageUsers: true },
  lab_admin: { edit: true, manageUsers: false },
  student: { edit: false, manageUsers: false },
}