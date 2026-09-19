import type { Alert, StatusSummary } from '@/types'
import { request } from './http'

/** GET /monitor/summary 设备状态统计 */
export function getStatusSummary(): Promise<StatusSummary> {
  return request<StatusSummary>({ url: '/monitor/summary', method: 'GET' })
}

/** GET /monitor/alerts 告警列表 */
export function listAlerts(): Promise<Alert[]> {
  return request({ url: '/monitor/alerts', method: 'GET' })
}

/** PUT /monitor/alerts/:id/resolve 处理告警 */
export function resolveAlert(id: string): Promise<void> {
  return request({ url: `/monitor/alerts/${id}/resolve`, method: 'PUT' })
}