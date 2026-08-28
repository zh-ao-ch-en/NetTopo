import type { Alert, Device, TopologyData } from '@/types'
import { getStorage, removeStorage, setStorage } from '@/utils/storage'
import { seedDevices } from './devices'
import { seedAlerts } from './monitor'
import { seedTopology } from './topology'
import type { MockUser } from './users'
import { seedUsers } from './users'

/** mock 数据库结构（模拟后端数据库 + 会话状态） */
export interface MockDb {
  users: MockUser[]
  devices: Device[]
  topology: TopologyData
  alerts: Alert[]
  /** 当前登录 token（模拟） */
  token: string | null
  /** 当前登录用户ID（模拟会话） */
  currentUserId: string | null
}

const DB_KEY = 'lab_mock_db'

function create(): MockDb {
  return {
    users: seedUsers(),
    devices: seedDevices(),
    topology: seedTopology(),
    alerts: seedAlerts(),
    token: null,
    currentUserId: null,
  }
}

let cache: MockDb | null = null

/** 获取 mock 数据库实例（首次从 localStorage 恢复，否则用种子初始化） */
export function db(): MockDb {
  if (!cache) {
    cache = getStorage<MockDb>(DB_KEY, create())
  }
  return cache
}

/** 持久化到 localStorage（模拟写入数据库） */
export function persist(): void {
  if (cache) setStorage(DB_KEY, cache)
}

/** 重置 mock 数据库为初始种子数据（用于演示"恢复出厂"） */
export function resetMockDb(): void {
  removeStorage(DB_KEY)
  cache = null
}