import type { LoginPayload, LoginResult, User } from '@/types'
import { request } from './http'

/** POST /auth/login 登录 */
export function login(payload: LoginPayload): Promise<LoginResult> {
  return request<LoginResult>({ url: '/auth/login', method: 'POST', data: payload })
}

/** GET /auth/profile 获取当前登录用户 */
export function getProfile(): Promise<User> {
  return request<User>({ url: '/auth/profile', method: 'GET' })
}

/** POST /auth/logout 退出登录 */
export function logout(): Promise<void> {
  return request<void>({ url: '/auth/logout', method: 'POST' })
}