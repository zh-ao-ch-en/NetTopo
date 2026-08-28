import type { Role } from '@/types'
import { ROLE_PERMISSIONS } from '@/types'

/** 角色是否拥有编辑权限（设备/拓扑的增删改） */
export function canEdit(role: Role): boolean {
  return ROLE_PERMISSIONS[role]?.edit ?? false
}

/** 角色是否拥有用户/权限管理权限 */
export function canManageUsers(role: Role): boolean {
  return ROLE_PERMISSIONS[role]?.manageUsers ?? false
}