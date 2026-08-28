import axios, { type AxiosInstance, type AxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'
import { API_CONFIG } from '@/config'
import type { ApiResponse } from '@/types'

/**
 * axios 实例与统一封装：
 * - 请求拦截：自动附加 Bearer token
 * - 响应拦截：统一解包 { code, message, data }，code!==0 时提示并 reject
 * 后端同学接入时只需保证接口返回体符合 ApiResponse 结构。
 */
const http: AxiosInstance = axios.create({
  baseURL: API_CONFIG.baseURL,
  timeout: 15000,
})

http.interceptors.request.use((config) => {
  const token = localStorage.getItem(API_CONFIG.tokenKey)
  if (token) {
    config.headers = config.headers || {}
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

http.interceptors.response.use(
  (response) => {
    const body = response.data as ApiResponse
    if (body && typeof body === 'object' && 'code' in body) {
      if (body.code !== 0) {
        ElMessage.error(body.message || '请求失败')
        return Promise.reject(new Error(body.message || '请求失败'))
      }
      return body.data
    }
    return response.data
  },
  (error) => {
    const msg = error?.response?.data?.message || error.message || '网络错误'
    ElMessage.error(msg)
    return Promise.reject(error)
  },
)

/** 泛型请求方法（响应拦截器已解包出 data） */
export function request<T = unknown>(config: AxiosRequestConfig): Promise<T> {
  return http.request(config) as unknown as Promise<T>
}

export default http