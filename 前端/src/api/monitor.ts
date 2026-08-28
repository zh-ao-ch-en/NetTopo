import { API_CONFIG } from '@/config'
import type { Alert } from '@/types'
import { mockGetStatusSummary, mockListAlerts, mockResolveAlert, type StatusSummary } from '@/mock/api'
import { request } from './http'

export type { StatusSummary }

/** GET /monitor/summary 设备状态统计 */
export function getStatusSummary(): Promise<StatusSummary> {
  if (API_CONFIG.useMock) return mockGetStatusSummary()
  return request({ url: '/monitor/summary', method: 'GET' })
}

/** GET /monitor/alerts 告警列表 */
export function listAlerts(): Promise<Alert[]> {
  if (API_CONFIG.useMock) return mockListAlerts()
  return request({ url: '/monitor/alerts', method: 'GET' })
}

/** PUT /monitor/alerts/:id/resolve 处理告警 */
export function resolveAlert(id: string): Promise<void> {
  if (API_CONFIG.useMock) return mockResolveAlert(id)
  return request({ url: `/monitor/alerts/${id}/resolve`, method: 'PUT' })
}