import type { Alert } from '@/types'
import { offsetDate } from '@/utils/id'

function at(time: string): string {
  return `${offsetDate(0)}T${time}`
}

/** 种子告警（模拟实时监控产生的告警） */
export function seedAlerts(): Alert[] {
  return [
    { id: 'al-001', deviceId: 'dev-005', deviceName: '接入交换机-02', level: 'critical', message: '设备离线，疑似断电', time: at('09:12:33'), resolved: false },
    { id: 'al-002', deviceId: 'dev-013', deviceName: '学生主机-01', level: 'critical', message: '设备离线', time: at('09:05:11'), resolved: false },
    { id: 'al-003', deviceId: 'dev-010', deviceName: 'Web服务器-01', level: 'warning', message: '磁盘使用率超过 80%', time: at('08:56:20'), resolved: false },
    { id: 'al-004', deviceId: 'dev-003', deviceName: '汇聚交换机-02', level: 'warning', message: 'CPU 负载持续偏高', time: at('08:41:02'), resolved: false },
    { id: 'al-005', deviceId: 'dev-015', deviceName: '无线AP-02', level: 'info', message: '接入终端数较多（当前 32 台）', time: at('08:20:47'), resolved: false },
    { id: 'al-006', deviceId: 'dev-002', deviceName: '汇聚交换机-01', level: 'info', message: '端口 GE0/0/3 状态变为 down', time: at('07:58:09'), resolved: true },
  ]
}