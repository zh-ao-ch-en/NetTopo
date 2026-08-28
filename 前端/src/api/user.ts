import { API_CONFIG } from '@/config'
import type { User } from '@/types'
import { mockCreateUser, mockDeleteUser, mockListUsers, mockUpdateUser } from '@/mock/api'
import { request } from './http'

/** GET /users 用户列表（仅管理员） */
export function listUsers(): Promise<User[]> {
  if (API_CONFIG.useMock) return mockListUsers()
  return request({ url: '/users', method: 'GET' })
}

/** POST /users 创建用户（仅管理员） */
export function createUser(data: Partial<User> & { password?: string }): Promise<User> {
  if (API_CONFIG.useMock) return mockCreateUser(data)
  return request({ url: '/users', method: 'POST', data })
}

/** PUT /users/:id 更新用户（仅管理员） */
export function updateUser(id: string, data: Partial<User> & { password?: string }): Promise<User> {
  if (API_CONFIG.useMock) return mockUpdateUser(id, data)
  return request({ url: `/users/${id}`, method: 'PUT', data })
}

/** DELETE /users/:id 删除用户（仅管理员） */
export function deleteUser(id: string): Promise<void> {
  if (API_CONFIG.useMock) return mockDeleteUser(id)
  return request({ url: `/users/${id}`, method: 'DELETE' })
}