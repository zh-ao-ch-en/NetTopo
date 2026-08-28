<template>
  <div>
    <h2 class="page-title">设备管理</h2>
    <p class="page-subtitle">实验室设备台账的增删改查</p>

    <!-- 工具栏 -->
    <div class="toolbar card">
      <div class="filters">
        <el-input
          v-model="query.keyword"
          placeholder="搜索名称/编号/型号/IP/负责人"
          clearable
          style="width: 260px"
          :prefix-icon="Search"
          @keyup.enter="search"
          @clear="search"
        />
        <el-select v-model="query.type" placeholder="设备类型" clearable style="width: 140px" @change="search">
          <el-option v-for="(label, val) in DEVICE_TYPE_NAME" :key="val" :label="label" :value="val" />
        </el-select>
        <el-select v-model="query.status" placeholder="状态" clearable style="width: 120px" @change="search">
          <el-option v-for="(label, val) in DEVICE_STATUS_NAME" :key="val" :label="label" :value="val" />
        </el-select>
        <el-button type="primary" :icon="Search" @click="search">查询</el-button>
      </div>
      <el-button v-if="canEdit(auth.role)" type="primary" :icon="Plus" @click="openCreate">新增设备</el-button>
    </div>

    <!-- 表格 -->
    <div class="card table-card">
      <el-table :data="rows" v-loading="loading" style="width: 100%">
        <el-table-column label="类型" width="120">
          <template #default="{ row }">
            <span class="type-cell">
              <DeviceIcon :type="row.type" :size="18" />
              {{ DEVICE_TYPE_NAME[row.type as DeviceType] }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="设备名称" min-width="150" show-overflow-tooltip />
        <el-table-column label="品牌 / 型号" min-width="150" show-overflow-tooltip>
          <template #default="{ row }">{{ row.brand }} {{ row.model }}</template>
        </el-table-column>
        <el-table-column prop="mgmtIp" label="管理IP" width="130" />
        <el-table-column label="位置" min-width="140" show-overflow-tooltip>
          <template #default="{ row }">{{ row.room }} / {{ row.rack }} {{ row.rackUnit }}</template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="DEVICE_STATUS_TYPE[row.status as DeviceStatus]" size="small" effect="light">
              {{ DEVICE_STATUS_NAME[row.status as DeviceStatus] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="owner" label="负责人" width="100" />
        <el-table-column label="操作" width="180" fixed="right" align="center">
          <template #default="{ row }">
            <div class="op-cell">
              <div class="op-stack">
                <el-button size="small" text type="primary" @click="openDetail(row)">详情</el-button>
                <el-button v-if="canEdit(auth.role)" size="small" text type="primary" @click="openEdit(row)">编辑</el-button>
              </div>
              <el-button v-if="canEdit(auth.role)" size="small" text type="danger" @click="remove(row)">删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      <div class="pager">
        <el-pagination
          v-model:current-page="query.page"
          v-model:page-size="query.pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @current-change="load"
          @size-change="search"
        />
      </div>
    </div>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑设备' : '新增设备'" width="680px" top="6vh">
      <el-form :model="form" label-width="96px" class="device-form">
        <el-tabs v-model="activeTab">
          <el-tab-pane label="基础身份" name="base">
            <el-form-item label="设备名称" required>
              <el-input v-model="form.name" placeholder="如 核心交换机-01" />
            </el-form-item>
            <el-form-item label="设备类型">
              <el-select v-model="form.type" style="width: 100%">
                <el-option v-for="(label, val) in DEVICE_TYPE_NAME" :key="val" :label="label" :value="val" />
              </el-select>
            </el-form-item>
            <div class="form-row">
              <el-form-item label="品牌"><el-input v-model="form.brand" /></el-form-item>
              <el-form-item label="型号"><el-input v-model="form.model" /></el-form-item>
            </div>
            <el-form-item label="资产编号"><el-input v-model="form.assetNo" /></el-form-item>
          </el-tab-pane>
          <el-tab-pane label="网络参数" name="net">
            <el-form-item label="管理IP"><el-input v-model="form.mgmtIp" placeholder="192.168.1.1" /></el-form-item>
            <el-form-item label="MAC地址"><el-input v-model="form.mac" placeholder="00:E0:FC:00:00:00" /></el-form-item>
          </el-tab-pane>
          <el-tab-pane label="位置与资产" name="loc">
            <div class="form-row">
              <el-form-item label="机房"><el-input v-model="form.room" /></el-form-item>
              <el-form-item label="机柜"><el-input v-model="form.rack" /></el-form-item>
            </div>
            <div class="form-row">
              <el-form-item label="工位/U位"><el-input v-model="form.rackUnit" /></el-form-item>
              <el-form-item label="所属项目"><el-input v-model="form.project" /></el-form-item>
            </div>
            <el-form-item label="序列号"><el-input v-model="form.serialNo" /></el-form-item>
            <div class="form-row">
              <el-form-item label="采购日期">
                <el-date-picker v-model="form.purchaseDate" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
              </el-form-item>
              <el-form-item label="保修到期">
                <el-date-picker v-model="form.warrantyUntil" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
              </el-form-item>
            </div>
            <el-form-item label="价格(元)"><el-input-number v-model="form.price" :min="0" :step="100" style="width: 220px" /></el-form-item>
          </el-tab-pane>
          <el-tab-pane label="运维状态" name="ops">
            <div class="form-row">
              <el-form-item label="负责人"><el-input v-model="form.owner" /></el-form-item>
              <el-form-item label="使用人"><el-input v-model="form.useUser" /></el-form-item>
            </div>
            <el-form-item label="运行状态">
              <el-select v-model="form.status" style="width: 100%">
                <el-option v-for="(label, val) in DEVICE_STATUS_NAME" :key="val" :label="label" :value="val" />
              </el-select>
            </el-form-item>
            <el-form-item label="备注"><el-input v-model="form.remark" type="textarea" :rows="2" /></el-form-item>
          </el-tab-pane>
        </el-tabs>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="submit">保存</el-button>
      </template>
    </el-dialog>

    <!-- 详情抽屉 -->
    <el-drawer v-model="drawerVisible" title="设备详情" size="440px">
      <template v-if="detail">
        <div class="detail-head">
          <DeviceIcon :type="detail.type" :size="40" />
          <div>
            <div class="detail-name">{{ detail.name }}</div>
            <div class="detail-sub">{{ DEVICE_TYPE_NAME[detail.type] }} · {{ detail.brand }} {{ detail.model }}</div>
          </div>
        </div>
        <el-descriptions :column="1" border size="small">
          <el-descriptions-item label="资产编号">{{ detail.assetNo || '-' }}</el-descriptions-item>
          <el-descriptions-item label="管理IP">{{ detail.mgmtIp || '-' }}</el-descriptions-item>
          <el-descriptions-item label="MAC地址">{{ detail.mac || '-' }}</el-descriptions-item>
          <el-descriptions-item label="位置">{{ loc(detail) }}</el-descriptions-item>
          <el-descriptions-item label="序列号">{{ detail.serialNo || '-' }}</el-descriptions-item>
          <el-descriptions-item label="采购/保修">{{ detail.purchaseDate || '-' }} ~ {{ detail.warrantyUntil || '-' }}</el-descriptions-item>
          <el-descriptions-item label="负责人">{{ detail.owner || '-' }}（使用人：{{ detail.useUser || '-' }}）</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="DEVICE_STATUS_TYPE[detail.status]" size="small">{{ DEVICE_STATUS_NAME[detail.status] }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="备注">{{ detail.remark || '-' }}</el-descriptions-item>
        </el-descriptions>

        <h4 class="sec-title">端口列表</h4>
        <el-table :data="detail.ports" size="small" empty-text="暂无端口" max-height="240">
          <el-table-column prop="name" label="端口" width="110" />
          <el-table-column prop="speed" label="速率" width="80" />
          <el-table-column label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="row.status === 'up' ? 'success' : 'info'" size="small">{{ row.status === 'up' ? 'UP' : 'DOWN' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="connectedTo" label="对端" />
        </el-table>

        <h4 class="sec-title">关键指标</h4>
        <div class="metrics">
          <div v-for="(v, k) in detail.metrics" :key="k" class="metric-item">
            <span class="metric-key">{{ k }}</span>
            <span class="metric-val">{{ v }}</span>
          </div>
          <div v-if="!Object.keys(detail.metrics).length" class="empty">暂无指标</div>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus } from '@element-plus/icons-vue'
import type { Device, DeviceStatus, DeviceType } from '@/types'
import { DEVICE_STATUS_NAME, DEVICE_STATUS_TYPE, DEVICE_TYPE_NAME } from '@/utils/constants'
import { createDevice, deleteDevice, getDevice, listDevices, updateDevice } from '@/api/device'
import { useAuthStore } from '@/stores/auth'
import { canEdit } from '@/utils/permission'
import DeviceIcon from '@/components/DeviceIcon.vue'

const auth = useAuthStore()
const route = useRoute()
const loading = ref(false)
const saving = ref(false)
const rows = ref<Device[]>([])
const total = ref(0)

const query = reactive({ keyword: '', type: '', status: '', page: 1, pageSize: 10 })

const dialogVisible = ref(false)
const isEdit = ref(false)
const activeTab = ref('base')

const emptyForm = (): Device => ({
  id: '',
  name: '',
  assetNo: '',
  type: 'switch',
  brand: '',
  model: '',
  mgmtIp: '',
  mac: '',
  ports: [],
  room: '',
  rack: '',
  rackUnit: '',
  project: '',
  serialNo: '',
  purchaseDate: '',
  warrantyUntil: '',
  price: 0,
  owner: '',
  useUser: '',
  status: 'offline',
  metrics: {},
  remark: '',
  createdAt: '',
  updatedAt: '',
})

const form = reactive<Device>(emptyForm())

const drawerVisible = ref(false)
const detail = ref<Device | null>(null)

async function load() {
  loading.value = true
  try {
    const res = await listDevices({
      keyword: query.keyword || undefined,
      type: query.type || undefined,
      status: query.status || undefined,
      page: query.page,
      pageSize: query.pageSize,
    })
    rows.value = res.list
    total.value = res.total
  } finally {
    loading.value = false
  }
}

function search() {
  query.page = 1
  load()
}

function openCreate() {
  Object.assign(form, emptyForm(), { type: 'switch', status: 'online' })
  isEdit.value = false
  activeTab.value = 'base'
  dialogVisible.value = true
}

function openEdit(row: Device) {
  Object.assign(form, emptyForm(), row)
  isEdit.value = true
  activeTab.value = 'base'
  dialogVisible.value = true
}

async function submit() {
  if (!form.name) {
    ElMessage.warning('请填写设备名称')
    return
  }
  saving.value = true
  try {
    if (isEdit.value) {
      await updateDevice(form.id, { ...form })
      ElMessage.success('设备已更新')
    } else {
      await createDevice({ ...form })
      ElMessage.success('设备已创建')
    }
    dialogVisible.value = false
    load()
  } catch (e) {
    ElMessage.error((e as Error).message || '保存失败')
  } finally {
    saving.value = false
  }
}

async function openDetail(row: Device) {
  try {
    detail.value = await getDevice(row.id)
    drawerVisible.value = true
  } catch (e) {
    ElMessage.error((e as Error).message || '加载失败')
  }
}

async function remove(row: Device) {
  try {
    await ElMessageBox.confirm(`确定删除设备「${row.name}」吗？删除后将同步移除拓扑中的关联节点。`, '删除确认', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
  } catch {
    return
  }
  try {
    await deleteDevice(row.id)
    ElMessage.success('已删除')
    load()
  } catch (e) {
    ElMessage.error((e as Error).message || '删除失败')
  }
}

function loc(d: Device) {
  return [d.room, d.rack, d.rackUnit].filter(Boolean).join(' / ') || '-'
}

async function openDetailById(id: string) {
  try {
    detail.value = await getDevice(id)
    drawerVisible.value = true
  } catch (e) {
    ElMessage.error((e as Error).message || '加载失败')
  }
}

onMounted(async () => {
  await load()
  const deviceId = route.query.device as string | undefined
  if (deviceId) openDetailById(deviceId)
})
</script>

<style scoped>
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  margin-bottom: 16px;
}
.filters {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}
.table-card {
  padding: 8px 16px 16px;
}
.type-cell {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--primary);
}
.pager {
  display: flex;
  justify-content: flex-end;
  margin-top: 14px;
}
.form-row {
  display: flex;
  gap: 16px;
}
.form-row .el-form-item {
  flex: 1;
}
.detail-head {
  display: flex;
  align-items: center;
  gap: 14px;
  color: var(--primary);
  margin-bottom: 18px;
}
.detail-name {
  font-size: 17px;
  font-weight: 600;
  color: var(--text-primary);
}
.detail-sub {
  font-size: 13px;
  color: var(--text-secondary);
}
.sec-title {
  font-size: 14px;
  font-weight: 600;
  margin: 20px 0 10px;
}
.metrics {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}
.metric-item {
  display: flex;
  justify-content: space-between;
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
}
.metric-key {
  color: var(--text-secondary);
  font-size: 13px;
}
.metric-val {
  font-weight: 600;
  color: var(--primary);
}
.empty {
  color: var(--text-weak);
  font-size: 13px;
}
.op-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}
.op-stack {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}
.op-stack :deep(.el-button + .el-button) {
  margin-left: 0;
}
@media (max-width: 720px) {
  .toolbar {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }
  .filters {
    width: 100%;
  }
  .filters :deep(.el-input),
  .filters :deep(.el-select) {
    width: 100% !important;
  }
  .filters :deep(.el-button) {
    width: 100%;
  }
  .form-row {
    flex-direction: column;
    gap: 0;
  }
  .pager {
    justify-content: center;
  }
}
</style>