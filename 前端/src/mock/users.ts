import type { User } from '@/types'

/** mock 内部用户（含密码，真实后端由数据库保存密码哈希，不返回明文） */
export interface MockUser extends User {
  password: string
}

export function seedUsers(): MockUser[] {
  return [
    {
      id: 'u-001',
      username: 'admin',
      password: 'admin123',
      displayName: '系统管理员',
      role: 'admin',
      email: 'admin@lab.edu.cn',
      phone: '13800000001',
      enabled: true,
      createdAt: '2023-01-01',
    },
    {
      id: 'u-002',
      username: 'teacher',
      password: 'teacher123',
      displayName: '王老师',
      role: 'lab_admin',
      email: 'wang@lab.edu.cn',
      phone: '13800000002',
      enabled: true,
      createdAt: '2023-02-01',
    },
    {
      id: 'u-003',
      username: 'student',
      password: 'student123',
      displayName: '张同学',
      role: 'student',
      email: 'zhang@lab.edu.cn',
      phone: '13800000003',
      enabled: true,
      createdAt: '2023-03-01',
    },
  ]
}