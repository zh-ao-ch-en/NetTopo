import { defineStore } from 'pinia'
import type { LoginPayload, Role, User } from '@/types'
import * as authApi from '@/api/auth'
import { API_CONFIG } from '@/config'

interface AuthState {
  token: string
  user: User | null
}

function readUser(): User | null {
  try {
    const raw = localStorage.getItem(API_CONFIG.userKey)
    return raw ? (JSON.parse(raw) as User) : null
  } catch {
    return null
  }
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    token: localStorage.getItem(API_CONFIG.tokenKey) || '',
    user: readUser(),
  }),
  getters: {
    isLoggedIn: (s) => !!s.token && !!s.user,
    role: (s): Role => s.user?.role || 'student',
    displayName: (s) => s.user?.displayName || '',
  },
  actions: {
    async login(payload: LoginPayload) {
      const res = await authApi.login(payload)
      this.token = res.token
      this.user = res.user
      localStorage.setItem(API_CONFIG.tokenKey, res.token)
      localStorage.setItem(API_CONFIG.userKey, JSON.stringify(res.user))
    },
    async logout() {
      try {
        await authApi.logout()
      } catch {
        // 忽略退出接口异常
      }
      this.token = ''
      this.user = null
      localStorage.removeItem(API_CONFIG.tokenKey)
      localStorage.removeItem(API_CONFIG.userKey)
    },
    async refreshProfile() {
      if (!this.token) return
      try {
        this.user = await authApi.getProfile()
        localStorage.setItem(API_CONFIG.userKey, JSON.stringify(this.user))
      } catch {
        await this.logout()
      }
    },
  },
})