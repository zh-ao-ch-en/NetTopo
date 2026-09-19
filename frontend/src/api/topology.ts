import type { TopologyData } from '@/types'
import { request } from './http'

/** GET /topology 获取拓扑 */
export function getTopology(): Promise<TopologyData> {
  return request({ url: '/topology', method: 'GET' })
}

/** PUT /topology 保存拓扑 */
export function saveTopology(data: TopologyData): Promise<TopologyData> {
  return request({ url: '/topology', method: 'PUT', data })
}

/** PUT /topology/reset 重置为初始拓扑 */
export function resetTopology(): Promise<TopologyData> {
  return request({ url: '/topology/reset', method: 'PUT' })
}