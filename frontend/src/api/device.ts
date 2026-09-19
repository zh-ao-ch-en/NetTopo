import type { Device, PageResult } from '@/types'
import { request } from './http'

/** 设备分页查询参数 */
export interface DeviceQuery {
  keyword?: string
  type?: string
  status?: string
  page?: number
  pageSize?: number
}

/** GET /devices 分页查询设备 */
export function listDevices(q: DeviceQuery = {}): Promise<PageResult<Device>> {
  return request({ url: '/devices', method: 'GET', params: q })
}

/** GET /devices/all 获取全部设备（拓扑编辑器设备库使用） */
export function listAllDevices(): Promise<Device[]> {
  return request({ url: '/devices/all', method: 'GET' })
}

/** GET /devices/:id 设备详情 */
export function getDevice(id: string): Promise<Device> {
  return request({ url: `/devices/${id}`, method: 'GET' })
}

/** POST /devices 创建设备 */
export function createDevice(data: Partial<Device>): Promise<Device> {
  return request({ url: '/devices', method: 'POST', data })
}

/** PUT /devices/:id 更新设备 */
export function updateDevice(id: string, data: Partial<Device>): Promise<Device> {
  return request({ url: `/devices/${id}`, method: 'PUT', data })
}

/** DELETE /devices/:id 删除设备 */
export function deleteDevice(id: string): Promise<void> {
  return request({ url: `/devices/${id}`, method: 'DELETE' })
}