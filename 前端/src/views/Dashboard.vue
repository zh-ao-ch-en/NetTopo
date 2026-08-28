<template>
  <div>
    <h2 class="page-title">状态监控</h2>
    <p class="page-subtitle">设备运行状态总览与实时告警（当前为模拟数据）</p>

    <!-- 统计卡片 -->
    <div class="stat-grid">
      <div class="stat-card card" v-for="s in stats" :key="s.label">
        <div class="stat-icon" :style="{ background: s.bg, color: s.color }">
          <el-icon :size="22"><component :is="s.icon" /></el-icon>
        </div>
        <div class="stat-body">
          <div class="stat-num" :style="{ color: s.color }">{{ s.value }}</div>
          <div class="stat-label">{{ s.label }}</div>
        </div>
      </div>
    </div>

    <!-- 告警列表 -->
    <div class="card panel">
      <div class="panel-head">
        <h3 class="panel-title">告警信息</h3>
        <el-button size="small" text @click="load()">刷新</el-button>
      </div>
      <el-table :data="alerts" v-loading="loading" style="width: 100%">
        <el-table-column label="级别" width="90">
          <template #default="{ row }">
            <el-tag :type="levelType(row.level)" size="small" effect="dark">{{ levelName(row.level) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="deviceName" label="设备" min-width="140" />
        <el-table-column prop="message" label="告警内容" min-width="240" show-overflow-tooltip />
        <el-table-column label="时间" width="180">
          <template #default="{ row }">{{ formatTime(row.time) }}</template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.resolved ? 'info' : 'danger'" size="small" effect="plain">
              {{ row.resolved ? '已处理' : '未处理' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="110" v-if="canEdit(auth.role)">
          <template #default="{ row }">
            <el-button v-if="!row.resolved" size="small" type="primary" text @click="resolve(row)">处理</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import type { Alert, AlertLevel } from '@/types'
import { listAlerts, resolveAlert, getStatusSummary, type StatusSummary } from '@/api/monitor'
import { useAuthStore } from '@/stores/auth'
import { canEdit } from '@/utils/permission'
import { ALERT_LEVEL_NAME } from '@/utils/constants'

const auth = useAuthStore()
const loading = ref(false)
const alerts = ref<Alert[]>([])
const summary = ref<StatusSummary>({ total: 0, online: 0, offline: 0, warning: 0, error: 0 })

const stats = computed(() => [
  { label: '设备总数', value: summary.value.total, icon: 'Cpu', color: 'var(--primary)', bg: 'var(--primary-soft)' },
  { label: '在线', value: summary.value.online, icon: 'CircleCheck', color: 'var(--success)', bg: 'rgba(34,197,94,0.12)' },
  { label: '离线', value: summary.value.offline, icon: 'CircleClose', color: 'var(--info)', bg: 'rgba(148,163,184,0.14)' },
  { label: '告警', value: summary.value.warning, icon: 'Warning', color: 'var(--warning)', bg: 'rgba(245,158,11,0.14)' },
  { label: '故障', value: summary.value.error, icon: 'CircleCloseFilled', color: 'var(--danger)', bg: 'rgba(239,68,68,0.14)' },
])

function levelType(level: AlertLevel) {
  return level === 'critical' ? 'danger' : level === 'warning' ? 'warning' : 'info'
}
function levelName(level: AlertLevel) {
  return ALERT_LEVEL_NAME[level]
}
function formatTime(t: string) {
  return t.replace('T', ' ').slice(0, 19)
}

async function load() {
  loading.value = true
  try {
    const [s, a] = await Promise.all([getStatusSummary(), listAlerts()])
    summary.value = s
    alerts.value = a
  } finally {
    loading.value = false
  }
}

async function resolve(row: Alert) {
  try {
    await resolveAlert(row.id)
    ElMessage.success('已标记为处理')
    load()
  } catch (e) {
    ElMessage.error((e as Error).message || '操作失败')
  }
}

onMounted(load)
</script>

<style scoped>
.stat-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}
.stat-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px;
}
.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.stat-num {
  font-size: 26px;
  font-weight: 700;
  line-height: 1.1;
}
.stat-label {
  font-size: 13px;
  color: var(--text-secondary);
}
.panel {
  padding: 16px 18px;
}
.panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}
.panel-title {
  font-size: 15px;
  font-weight: 600;
  margin: 0;
}
@media (max-width: 1100px) {
  .stat-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
@media (max-width: 720px) {
  .stat-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
@media (max-width: 420px) {
  .stat-grid {
    grid-template-columns: 1fr;
  }
}
</style>