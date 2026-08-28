import { API_CONFIG } from '@/config'
import type { TopologyData } from '@/types'
import { mockGetTopology, mockSaveTopology } from '@/mock/api'
import { request } from './http'

/** GET /topology 获取拓扑数据 */
export function getTopology(): Promise<TopologyData> {
  if (API_CONFIG.useMock) return mockGetTopology()
  return request({ url: '/topology', method: 'GET' })
}

/** PUT /topology 保存拓扑数据（整体替换） */
export function saveTopology(data: TopologyData): Promise<TopologyData> {
  if (API_CONFIG.useMock) return mockSaveTopology(data)
  return request({ url: '/topology', method: 'PUT', data })
}