import type { Alert, Device, LoginPayload, LoginResult, PageResult, TopologyData, User } from '@/types'
import { API_CONFIG } from '@/config'
import { genId, today } from '@/utils/id'
import { db, persist } from './db'
import type { MockUser } from './users'

/** 模拟网络延迟 */
export function mockDelay(ms = API_CONFIG.mockDelay): Promise<void> {
  return new Promise((r) => setTimeout(r, ms))
}

/** 去除密码字段，返回对前端暴露的用户对象 */
function toPublicUser(u: MockUser): User {
  const { password, ...rest } = u
  void password
  return rest
}

// ---------------- 认证 ----------------
export async function mockLogin(payload: LoginPayload): Promise<LoginResult> {
  await mockDelay()
  const d = db()
  const u = d.users.find((x) => x.username === payload.username)
  if (!u || u.password !== payload.password) {
    throw new Error('用户名或密码错误')
  }
  if (!u.enabled) {
    throw new Error('账号已被禁用')
  }
  d.token = `mock-token-${u.id}-${Date.now().toString(36)}`
  d.currentUserId = u.id
  persist()
  return { token: d.token, user: toPublicUser(u) }
}

export async function mockGetProfile(): Promise<User> {
  await mockDelay(60)
  const d = db()
  const u = d.users.find((x) => x.id === d.currentUserId)
  if (!u) throw new Error('未登录或登录已失效')
  return toPublicUser(u)
}

export async function mockLogout(): Promise<void> {
  await mockDelay(60)
  const d = db()
  d.token = null
  d.currentUserId = null
  persist()
}

// ---------------- 设备 ----------------
export interface DeviceQuery {
  keyword?: string
  type?: string
  status?: string
  page?: number
  pageSize?: number
}

export async function mockListDevices(q: DeviceQuery = {}): Promise<PageResult<Device>> {
  await mockDelay()
  const d = db()
  let list = [...d.devices]
  if (q.keyword) {
    const kw = q.keyword.toLowerCase()
    list = list.filter((x) =>
      [x.name, x.assetNo, x.brand, x.model, x.mgmtIp, x.mac, x.owner, x.room].some((v) =>
        String(v).toLowerCase().includes(kw),
      ),
    )
  }
  if (q.type) list = list.filter((x) => x.type === q.type)
  if (q.status) list = list.filter((x) => x.status === q.status)
  const page = q.page ?? 1
  const pageSize = q.pageSize ?? 10
  const total = list.length
  const start = (page - 1) * pageSize
  return { list: list.slice(start, start + pageSize), total, page, pageSize }
}

export async function mockListAllDevices(): Promise<Device[]> {
  await mockDelay(60)
  return [...db().devices]
}

export async function mockGetDevice(id: string): Promise<Device> {
  await mockDelay(60)
  const dev = db().devices.find((x) => x.id === id)
  if (!dev) throw new Error('设备不存在')
  return { ...dev, ports: [...dev.ports] }
}

export async function mockCreateDevice(data: Partial<Device>): Promise<Device> {
  await mockDelay()
  const d = db()
  const now = new Date().toISOString()
  const dev: Device = {
    id: genId('dev-'),
    name: data.name ?? '',
    assetNo: data.assetNo ?? '',
    type: (data.type as Device['type']) ?? 'pc',
    brand: data.brand ?? '',
    model: data.model ?? '',
    mgmtIp: data.mgmtIp ?? '',
    mac: data.mac ?? '',
    ports: data.ports ?? [],
    room: data.room ?? '',
    rack: data.rack ?? '',
    rackUnit: data.rackUnit ?? '',
    project: data.project ?? '',
    serialNo: data.serialNo ?? '',
    purchaseDate: data.purchaseDate ?? '',
    warrantyUntil: data.warrantyUntil ?? '',
    price: data.price ?? 0,
    owner: data.owner ?? '',
    useUser: data.useUser ?? '',
    status: (data.status as Device['status']) ?? 'offline',
    metrics: data.metrics ?? {},
    remark: data.remark ?? '',
    createdAt: now,
    updatedAt: now,
  }
  d.devices.push(dev)
  persist()
  return dev
}

export async function mockUpdateDevice(id: string, data: Partial<Device>): Promise<Device> {
  await mockDelay()
  const d = db()
  const idx = d.devices.findIndex((x) => x.id === id)
  if (idx < 0) throw new Error('设备不存在')
  const updated: Device = { ...d.devices[idx], ...data, id, updatedAt: new Date().toISOString() }
  d.devices[idx] = updated
  persist()
  return updated
}

export async function mockDeleteDevice(id: string): Promise<void> {
  await mockDelay()
  const d = db()
  // 同步清理拓扑中引用该设备的节点与连线
  const nodeIds = new Set(d.topology.nodes.filter((n) => n.deviceId === id).map((n) => n.id))
  nodeIds.add(id)
  d.topology.nodes = d.topology.nodes.filter((n) => !nodeIds.has(n.id) && n.deviceId !== id)
  d.topology.edges = d.topology.edges.filter((e) => !nodeIds.has(e.source) && !nodeIds.has(e.target))
  d.devices = d.devices.filter((x) => x.id !== id)
  persist()
}

// ---------------- 拓扑 ----------------
export async function mockGetTopology(): Promise<TopologyData> {
  await mockDelay()
  return JSON.parse(JSON.stringify(db().topology)) as TopologyData
}

export async function mockSaveTopology(data: TopologyData): Promise<TopologyData> {
  await mockDelay()
  const d = db()
  d.topology = { ...data, updatedAt: new Date().toISOString() }
  persist()
  return d.topology
}

// ---------------- 监控 ----------------
export interface StatusSummary {
  total: number
  online: number
  offline: number
  warning: number
  error: number
}

export async function mockGetStatusSummary(): Promise<StatusSummary> {
  await mockDelay(60)
  const summary: StatusSummary = { total: 0, online: 0, offline: 0, warning: 0, error: 0 }
  for (const d of db().devices) {
    summary.total++
    if (d.status === 'online') summary.online++
    else if (d.status === 'offline') summary.offline++
    else if (d.status === 'warning') summary.warning++
    else if (d.status === 'error') summary.error++
  }
  return summary
}

export async function mockListAlerts(): Promise<Alert[]> {
  await mockDelay(60)
  return [...db().alerts].sort((a, b) => (a.time < b.time ? 1 : -1))
}

export async function mockResolveAlert(id: string): Promise<void> {
  await mockDelay(60)
  const al = db().alerts.find((x) => x.id === id)
  if (al) al.resolved = true
  persist()
}

// ---------------- 用户 ----------------
export async function mockListUsers(): Promise<User[]> {
  await mockDelay()
  return db().users.map(toPublicUser)
}

export async function mockCreateUser(data: Partial<MockUser>): Promise<User> {
  await mockDelay()
  const d = db()
  const u: MockUser = {
    id: genId('u-'),
    username: data.username ?? '',
    password: data.password ?? '',
    displayName: data.displayName ?? '',
    role: data.role ?? 'student',
    email: data.email,
    phone: data.phone,
    enabled: data.enabled ?? true,
    createdAt: today(),
  }
  d.users.push(u)
  persist()
  return toPublicUser(u)
}

export async function mockUpdateUser(id: string, data: Partial<MockUser>): Promise<User> {
  await mockDelay()
  const d = db()
  const idx = d.users.findIndex((x) => x.id === id)
  if (idx < 0) throw new Error('用户不存在')
  const updated: MockUser = { ...d.users[idx], ...data, id }
  d.users[idx] = updated
  persist()
  return toPublicUser(updated)
}

export async function mockDeleteUser(id: string): Promise<void> {
  await mockDelay()
  const d = db()
  d.users = d.users.filter((x) => x.id !== id)
  persist()
}