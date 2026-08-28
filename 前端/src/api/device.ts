import { API_CONFIG } from '@/config'
import type { Device, PageResult } from '@/types'
import {
  mockCreateDevice,
  mockDeleteDevice,
  mockGetDevice,
  mockListAllDevices,
  mockListDevices,
  mockUpdateDevice,
  type DeviceQuery,
} from '@/mock/api'
import { request } from './http'

/** GET /devices 分页查询设备 */
export function listDevices(q: DeviceQuery = {}): Promise<PageResult<Device>> {
  if (API_CONFIG.useMock) return mockListDevices(q)
  return request({ url: '/devices', method: 'GET', params: q })
}

/** GET /devices/all 获取全部设备（拓扑编辑器设备库使用） */
export function listAllDevices(): Promise<Device[]> {
  if (API_CONFIG.useMock) return mockListAllDevices()
  return request({ url: '/devices/all', method: 'GET' })
}

/** GET /devices/:id 设备详情 */
export function getDevice(id: string): Promise<Device> {
  if (API_CONFIG.useMock) return mockGetDevice(id)
  return request({ url: `/devices/${id}`, method: 'GET' })
}

/** POST /devices 创建设备 */
export function createDevice(data: Partial<Device>): Promise<Device> {
  if (API_CONFIG.useMock) return mockCreateDevice(data)
  return request({ url: '/devices', method: 'POST', data })
}

/** PUT /devices/:id 更新设备 */
export function updateDevice(id: string, data: Partial<Device>): Promise<Device> {
  if (API_CONFIG.useMock) return mockUpdateDevice(id, data)
  return request({ url: `/devices/${id}`, method: 'PUT', data })
}

/** DELETE /devices/:id 删除设备 */
export function deleteDevice(id: string): Promise<void> {
  if (API_CONFIG.useMock) return mockDeleteDevice(id)
  return request({ url: `/devices/${id}`, method: 'DELETE' })
}