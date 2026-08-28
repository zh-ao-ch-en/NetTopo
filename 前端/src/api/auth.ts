import { API_CONFIG } from '@/config'
import type { LoginPayload, LoginResult, User } from '@/types'
import { mockGetProfile, mockLogin, mockLogout } from '@/mock/api'
import { request } from './http'

/** POST /auth/login 登录 */
export function login(payload: LoginPayload): Promise<LoginResult> {
  if (API_CONFIG.useMock) return mockLogin(payload)
  return request<LoginResult>({ url: '/auth/login', method: 'POST', data: payload })
}

/** GET /auth/profile 获取当前登录用户 */
export function getProfile(): Promise<User> {
  if (API_CONFIG.useMock) return mockGetProfile()
  return request<User>({ url: '/auth/profile', method: 'GET' })
}

/** POST /auth/logout 退出登录 */
export function logout(): Promise<void> {
  if (API_CONFIG.useMock) return mockLogout()
  return request<void>({ url: '/auth/logout', method: 'POST' })
}