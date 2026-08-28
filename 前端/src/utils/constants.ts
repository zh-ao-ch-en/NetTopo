import type { AlertLevel, DeviceStatus, Role } from '@/types'

export { DEFAULT_NODE_SIZE, DEVICE_TYPE_NAME } from '@/types'

export const ROLE_NAME: Record<Role, string> = {
  admin: '系统管理员',
  lab_admin: '实验室管理员',
  student: '普通使用者',
}

export const DEVICE_STATUS_NAME: Record<DeviceStatus, string> = {
  online: '在线',
  offline: '离线',
  warning: '告警',
  error: '故障',
}

export const DEVICE_STATUS_TYPE: Record<DeviceStatus, 'success' | 'info' | 'warning' | 'danger'> = {
  online: 'success',
  offline: 'info',
  warning: 'warning',
  error: 'danger',
}

export const ALERT_LEVEL_NAME: Record<AlertLevel, string> = {
  info: '提示',
  warning: '警告',
  critical: '严重',
}