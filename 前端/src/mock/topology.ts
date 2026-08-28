import type { NodeType, TopologyData } from '@/types'
import { DEFAULT_NODE_SIZE } from '@/types'
import { offsetDate } from '@/utils/id'

function node(id: string, label: string, type: NodeType, x: number, y: number, deviceId = id) {
  return { id, deviceId, label, type, x, y, ...DEFAULT_NODE_SIZE[type] }
}

/** 初始拓扑样例（首次运行写入 mock 数据库，可在编辑器中修改后保存） */
export function seedTopology(): TopologyData {
  return {
    id: 'topo-main',
    name: '网络实验室主拓扑',
    updatedAt: new Date().toISOString(),
    nodes: [
      node('dev-007', '出口防火墙-01', 'firewall', 400, 20),
      node('dev-006', '核心路由器-01', 'router', 400, 130),
      node('dev-001', '核心交换机-01', 'switch', 400, 250),
      node('dev-002', '汇聚交换机-01', 'switch', 200, 370),
      node('dev-003', '汇聚交换机-02', 'switch', 600, 370),
      node('dev-004', '接入交换机-01', 'switch', 80, 500),
      node('dev-005', '接入交换机-02', 'switch', 440, 500),
      node('dev-008', '虚拟化服务器-01', 'server', 20, 650),
      node('dev-009', '数据库服务器-01', 'server', 210, 650),
      node('dev-010', 'Web服务器-01', 'server', 400, 650),
      node('dev-011', '学生工作站-01', 'pc', 590, 650),
      node('dev-012', '学生工作站-02', 'pc', 780, 650),
      node('dev-013', '学生主机-01', 'pc', 940, 500),
      node('dev-014', '无线AP-01', 'ap', 240, 800),
      node('dev-015', '无线AP-02', 'ap', 660, 800),
    ],
    edges: [
      { id: 'e1', source: 'dev-007', target: 'dev-006', style: 'solid' },
      { id: 'e2', source: 'dev-006', target: 'dev-001', style: 'solid' },
      { id: 'e3', source: 'dev-001', target: 'dev-002', style: 'solid' },
      { id: 'e4', source: 'dev-001', target: 'dev-003', style: 'solid' },
      { id: 'e5', source: 'dev-002', target: 'dev-004', style: 'solid' },
      { id: 'e6', source: 'dev-003', target: 'dev-005', style: 'solid' },
      { id: 'e7', source: 'dev-004', target: 'dev-008', style: 'solid' },
      { id: 'e8', source: 'dev-004', target: 'dev-009', style: 'solid' },
      { id: 'e9', source: 'dev-004', target: 'dev-010', style: 'solid' },
      { id: 'e10', source: 'dev-004', target: 'dev-011', style: 'solid' },
      { id: 'e11', source: 'dev-004', target: 'dev-012', style: 'solid' },
      { id: 'e12', source: 'dev-005', target: 'dev-013', style: 'solid' },
      { id: 'e13', source: 'dev-004', target: 'dev-014', style: 'dashed' },
      { id: 'e14', source: 'dev-005', target: 'dev-015', style: 'dashed' },
    ],
  }
}

export { offsetDate }