import type { User } from '@/types'
import { request } from './http'

/** GET /users 查询用户列表 */
export function listUsers(): Promise<User[]> {
  return request({ url: '/users', method: 'GET' })
}

/** POST /users 新增用户 */
export function createUser(data: Partial<User> & { password?: string }): Promise<User> {
  return request({ url: '/users', method: 'POST', data })
}

/** PUT /users/:id 更新用户 */
export function updateUser(id: string, data: Partial<User>): Promise<User> {
  return request({ url: `/users/${id}`, method: 'PUT', data })
}

/** DELETE /users/:id 删除用户 */
export function deleteUser(id: string): Promise<void> {
  return request({ url: `/users/${id}`, method: 'DELETE' })
}