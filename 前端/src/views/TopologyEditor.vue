<template>
  <div class="editor">
    <!-- 工具栏 -->
    <div class="card editor-toolbar">
      <div class="tool-group">
        <el-button size="small" :icon="Back" @click="router.push('/topology/view')">查看</el-button>
        <el-button size="small" type="primary" :icon="Check" @click="save">保存</el-button>
        <el-button size="small" :icon="Download" @click="exportJson">导出</el-button>
        <el-button size="small" :icon="Upload" @click="importJson">导入</el-button>
      </div>
      <div class="tool-group">
        <el-button
          size="small"
          :type="linkMode ? 'warning' : 'default'"
          :icon="Connection"
          @click="toggleLinkMode"
        >
          {{ linkMode ? '连线中（点击节点连线）' : '连线模式' }}
        </el-button>
        <el-button size="small" :icon="FullScreen" @click="canvasRef?.fitView()">适应画布</el-button>
        <el-button size="small" :icon="RefreshLeft" @click="resetTopology">重置拓扑</el-button>
        <el-button size="small" :icon="Delete" @click="clearAll">清空</el-button>
      </div>
      <div class="hint" v-if="linkMode">先点起点，再点目标节点即可连线；点击空白退出</div>
    </div>

    <div class="editor-body">
      <!-- 设备库 -->
      <aside class="card palette">
        <h4 class="palette-title">设备库（点击添加）</h4>
        <div class="palette-list">
          <div class="palette-item" v-for="d in devices" :key="d.id" @click="addDeviceNode(d)">
            <DeviceIcon :type="d.type" :size="16" />
            <span class="palette-name">{{ d.name }}</span>
          </div>
        </div>
        <h4 class="palette-title">通用节点</h4>
        <div class="palette-list">
          <div class="palette-item" @click="addGenericNode('cloud', '互联网')">
            <DeviceIcon type="cloud" :size="16" /><span class="palette-name">云 / 互联网</span>
          </div>
          <div class="palette-item" @click="addGenericNode('group', '分组')">
            <DeviceIcon type="group" :size="16" /><span class="palette-name">分组</span>
          </div>
        </div>
        <p class="palette-tip">提示：拖拽节点调整位置，滚轮缩放，空白拖动平移画布。</p>
      </aside>

      <!-- 画布 -->
      <div class="card canvas-wrap">
        <TopologyCanvas
          ref="canvasRef"
          :nodes="nodes"
          :edges="edges"
          :editable="!linkMode"
          :selected-id="selectedId"
          :selected-edge-id="selectedEdgeId"
          :device-status="deviceStatus"
          @select-node="onSelectNode"
          @select-edge="onSelectEdge"
          @move-node="onMoveNode"
          @resize-node="onResizeNode"
        />
      </div>

      <!-- 属性面板 -->
      <aside class="card inspector">
        <template v-if="selectedNode">
          <h4 class="insp-title">节点属性</h4>
          <el-form label-width="64px" size="small">
            <el-form-item label="名称">
              <el-input :model-value="selectedNode.label" @update:model-value="updateNodeLabel" />
            </el-form-item>
            <el-form-item label="类型">
              <el-select :model-value="selectedNode.type" style="width: 100%" :disabled="!!selectedNode.deviceId" @update:model-value="updateNodeType">
                <el-option v-for="(label, val) in TYPE_OPTIONS" :key="val" :label="label" :value="val" />
              </el-select>
            </el-form-item>
            <div class="insp-row">
              <el-form-item label="X"><el-input-number :model-value="selectedNode.x" :controls="false" @update:model-value="(v: number) => updateNodePos('x', v)" /></el-form-item>
              <el-form-item label="Y"><el-input-number :model-value="selectedNode.y" :controls="false" @update:model-value="(v: number) => updateNodePos('y', v)" /></el-form-item>
            </div>
            <div class="insp-row">
              <el-form-item label="宽"><el-input-number :model-value="selectedNode.width" :controls="false" :min="88" @update:model-value="(v: number) => updateNodeSize('width', v)" /></el-form-item>
              <el-form-item label="高"><el-input-number :model-value="selectedNode.height" :controls="false" :min="44" @update:model-value="(v: number) => updateNodeSize('height', v)" /></el-form-item>
            </div>
          </el-form>
          <div class="link-info" v-if="selectedNode.deviceId">
            关联设备：<strong>{{ deviceName(selectedNode.deviceId) }}</strong>
          </div>
          <el-button type="danger" size="small" :icon="Delete" class="danger-btn" @click="deleteSelected">删除节点</el-button>
        </template>

        <template v-else-if="selectedEdge">
          <h4 class="insp-title">连线属性</h4>
          <el-form label-width="64px" size="small">
            <el-form-item label="样式">
              <el-radio-group :model-value="selectedEdge.style ?? 'solid'" @update:model-value="updateEdgeStyle">
                <el-radio-button label="solid">实线</el-radio-button>
                <el-radio-button label="dashed">虚线</el-radio-button>
              </el-radio-group>
            </el-form-item>
          </el-form>
          <div class="link-info">
            {{ nodeLabel(selectedEdge.source) }} → {{ nodeLabel(selectedEdge.target) }}
          </div>
          <el-button type="danger" size="small" :icon="Delete" class="danger-btn" @click="deleteSelected">删除连线</el-button>
        </template>

        <template v-else>
          <h4 class="insp-title">提示</h4>
          <ul class="tips">
            <li>点击左侧设备库添加到画布</li>
            <li>拖动节点可调整位置</li>
            <li>选中节点后拖动右下角可自由拉伸大小</li>
            <li>开启「连线模式」后依次点击两个节点连线</li>
            <li>选中节点/连线后按 Delete 或点删除</li>
            <li>修改后自动保存，也可手动保存</li>
          </ul>
        </template>
      </aside>
    </div>

    <input ref="fileRef" type="file" accept="application/json" hidden @change="onImportFile" />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Back, Check, Connection, Delete, Download, FullScreen, RefreshLeft, Upload } from '@element-plus/icons-vue'
import type { Device, DeviceStatus, DeviceType, TopologyEdge, TopologyNode } from '@/types'
import { DEFAULT_NODE_SIZE, DEVICE_TYPE_NAME } from '@/utils/constants'
import { genId } from '@/utils/id'
import { getTopology, saveTopology } from '@/api/topology'
import { listAllDevices } from '@/api/device'
import { seedTopology } from '@/mock/topology'
import TopologyCanvas from '@/components/topology/TopologyCanvas.vue'
import DeviceIcon from '@/components/DeviceIcon.vue'

const router = useRouter()
const canvasRef = ref<InstanceType<typeof TopologyCanvas>>()
const fileRef = ref<HTMLInputElement>()

const topoId = ref('topo-main')
const topoName = ref('网络实验室主拓扑')
const nodes = ref<TopologyNode[]>([])
const edges = ref<TopologyEdge[]>([])
const devices = ref<Device[]>([])

const selectedId = ref<string | null>(null)
const selectedEdgeId = ref<string | null>(null)
const linkMode = ref(false)
const pendingSource = ref<string | null>(null)

const TYPE_OPTIONS = { ...DEVICE_TYPE_NAME, cloud: '云 / 互联网', group: '分组' } as Record<string, string>

const deviceStatus = computed<Record<string, DeviceStatus>>(() => {
  const map: Record<string, DeviceStatus> = {}
  for (const d of devices.value) map[d.id] = d.status
  return map
})

const selectedNode = computed(() => nodes.value.find((n) => n.id === selectedId.value) ?? null)
const selectedEdge = computed(() => edges.value.find((e) => e.id === selectedEdgeId.value) ?? null)

let saveTimer: number | null = null
let ready = false

function scheduleSave() {
  if (!ready) return
  if (saveTimer) clearTimeout(saveTimer)
  saveTimer = window.setTimeout(() => {
    saveTopology({ id: topoId.value, name: topoName.value, nodes: nodes.value, edges: edges.value, updatedAt: '' }).catch(() => {})
  }, 600)
}

async function load() {
  const [topo, all] = await Promise.all([getTopology(), listAllDevices()])
  topoId.value = topo.id
  topoName.value = topo.name
  nodes.value = topo.nodes
  edges.value = topo.edges
  devices.value = all
  ready = true
}

function onSelectNode(id: string | null) {
  if (linkMode.value) {
    if (!id) {
      pendingSource.value = null
      selectedId.value = null
      return
    }
    if (!pendingSource.value) {
      pendingSource.value = id
      selectedId.value = id
      ElMessage.info('已选择起点，请点击目标节点')
    } else if (pendingSource.value === id) {
      pendingSource.value = null
      selectedId.value = null
    } else {
      addEdge(pendingSource.value, id)
      pendingSource.value = null
      selectedId.value = null
    }
    return
  }
  selectedId.value = id
  selectedEdgeId.value = null
}

function onSelectEdge(id: string | null) {
  selectedEdgeId.value = id
  selectedId.value = null
}

function addEdge(src: string, tgt: string) {
  const exists = edges.value.some((e) => (e.source === src && e.target === tgt) || (e.source === tgt && e.target === src))
  if (exists) {
    ElMessage.warning('两节点之间已存在连线')
    return
  }
  edges.value.push({ id: genId('e-'), source: src, target: tgt, style: 'solid' })
  scheduleSave()
}

function onMoveNode(id: string, x: number, y: number) {
  const n = nodes.value.find((n) => n.id === id)
  if (n) {
    n.x = x
    n.y = y
    scheduleSave()
  }
}

function onResizeNode(id: string, width: number, height: number) {
  const n = nodes.value.find((n) => n.id === id)
  if (n) {
    n.width = width
    n.height = height
    scheduleSave()
  }
}

let addCount = 0
function nextPos() {
  const x = 300 + (addCount % 6) * 60
  const y = 160 + (addCount % 4) * 60
  addCount++
  return { x, y }
}

function addDeviceNode(d: Device) {
  const p = nextPos()
  const size = DEFAULT_NODE_SIZE[d.type]
  nodes.value.push({ id: genId('n-'), deviceId: d.id, label: d.name, type: d.type, x: p.x, y: p.y, width: size.width, height: size.height })
  scheduleSave()
  ElMessage.success(`已添加「${d.name}」`)
}

function addGenericNode(type: 'cloud' | 'group', label: string) {
  const p = nextPos()
  const size = DEFAULT_NODE_SIZE[type]
  nodes.value.push({ id: genId('n-'), label, type, x: p.x, y: p.y, width: size.width, height: size.height })
  scheduleSave()
}

function toggleLinkMode() {
  linkMode.value = !linkMode.value
  pendingSource.value = null
  selectedId.value = null
  selectedEdgeId.value = null
}

function updateNodeLabel(v: string) {
  if (selectedNode.value) {
    selectedNode.value.label = v
    scheduleSave()
  }
}
function updateNodeType(v: string) {
  if (selectedNode.value && !selectedNode.value.deviceId) {
    selectedNode.value.type = v as DeviceType | 'cloud' | 'group'
    scheduleSave()
  }
}
function updateNodePos(axis: 'x' | 'y', v: number) {
  if (selectedNode.value) {
    selectedNode.value[axis] = v
    scheduleSave()
  }
}
function updateNodeSize(axis: 'width' | 'height', v: number) {
  if (selectedNode.value && v) {
    selectedNode.value[axis] = Math.max(40, Math.round(v))
    scheduleSave()
  }
}
function updateEdgeStyle(v: string) {
  if (selectedEdge.value) {
    selectedEdge.value.style = v as 'solid' | 'dashed'
    scheduleSave()
  }
}

function deleteSelected() {
  if (selectedId.value) {
    const id = selectedId.value
    nodes.value = nodes.value.filter((n) => n.id !== id)
    edges.value = edges.value.filter((e) => e.source !== id && e.target !== id)
    selectedId.value = null
    scheduleSave()
    ElMessage.success('节点已删除')
  } else if (selectedEdgeId.value) {
    const id = selectedEdgeId.value
    edges.value = edges.value.filter((e) => e.id !== id)
    selectedEdgeId.value = null
    scheduleSave()
    ElMessage.success('连线已删除')
  }
}

function nodeLabel(id: string) {
  return nodes.value.find((n) => n.id === id)?.label ?? id
}
function deviceName(id: string) {
  return devices.value.find((d) => d.id === id)?.name ?? id
}

async function save() {
  try {
    await saveTopology({ id: topoId.value, name: topoName.value, nodes: nodes.value, edges: edges.value, updatedAt: '' })
    ElMessage.success('拓扑已保存')
  } catch (e) {
    ElMessage.error((e as Error).message || '保存失败')
  }
}

function exportJson() {
  const data = { id: topoId.value, name: topoName.value, nodes: nodes.value, edges: edges.value }
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${topoName.value || 'topology'}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('已导出 JSON 文件')
}

function importJson() {
  fileRef.value?.click()
}

function onImportFile(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = () => {
    try {
      const data = JSON.parse(String(reader.result))
      if (!Array.isArray(data.nodes) || !Array.isArray(data.edges)) throw new Error('格式不正确')
      topoName.value = data.name ?? topoName.value
      nodes.value = data.nodes
      edges.value = data.edges
      selectedId.value = null
      selectedEdgeId.value = null
      scheduleSave()
      ElMessage.success('导入成功')
    } catch (err) {
      ElMessage.error('导入失败：' + (err as Error).message)
    }
  }
  reader.readAsText(file)
  input.value = ''
}

function resetTopology() {
  const seed = seedTopology()
  topoName.value = seed.name
  nodes.value = JSON.parse(JSON.stringify(seed.nodes))
  edges.value = JSON.parse(JSON.stringify(seed.edges))
  selectedId.value = null
  selectedEdgeId.value = null
  scheduleSave()
  ElMessage.success('已重置为初始拓扑')
}

async function clearAll() {
  try {
    await ElMessageBox.confirm('确定清空画布上的所有节点和连线吗？', '清空确认', {
      type: 'warning',
      confirmButtonText: '清空',
      cancelButtonText: '取消',
    })
  } catch {
    return
  }
  nodes.value = []
  edges.value = []
  selectedId.value = null
  selectedEdgeId.value = null
  scheduleSave()
  ElMessage.success('已清空')
}

function onKeydown(e: KeyboardEvent) {
  if ((e.key === 'Delete' || e.key === 'Backspace') && (selectedId.value || selectedEdgeId.value)) {
    const target = e.target as HTMLElement
    if (target && (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA')) return
    deleteSelected()
  }
}

onMounted(() => {
  load()
  window.addEventListener('keydown', onKeydown)
})
</script>

<style scoped>
.editor {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 100px);
  min-height: 480px;
}
.editor-toolbar {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 10px 14px;
  margin-bottom: 14px;
  flex-wrap: wrap;
}
.tool-group {
  display: flex;
  align-items: center;
  gap: 8px;
}
.hint {
  font-size: 12px;
  color: var(--warning);
  margin-left: auto;
}
.editor-body {
  flex: 1;
  display: flex;
  gap: 14px;
  min-height: 0;
}
.palette {
  width: 216px;
  overflow: auto;
  padding: 12px;
  flex-shrink: 0;
}
.palette-title {
  font-size: 13px;
  font-weight: 600;
  margin: 4px 0 8px;
}
.palette-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-height: 46%;
  overflow: auto;
  margin-bottom: 8px;
}
.palette-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 9px;
  border-radius: 7px;
  cursor: pointer;
  color: var(--primary);
  font-size: 13px;
  border: 1px solid transparent;
}
.palette-item:hover {
  background: var(--primary-soft);
  border-color: var(--primary);
}
.palette-name {
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.palette-tip {
  font-size: 12px;
  color: var(--text-weak);
  line-height: 1.6;
}
.canvas-wrap {
  flex: 1;
  overflow: hidden;
  min-width: 0;
}
.inspector {
  width: 250px;
  flex-shrink: 0;
  padding: 14px;
  overflow: auto;
}
.insp-title {
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 12px;
}
.insp-row {
  display: flex;
  gap: 8px;
}
.insp-row .el-form-item {
  flex: 1;
}
.link-info {
  font-size: 13px;
  color: var(--text-secondary);
  padding: 8px 0;
  line-height: 1.5;
}
.link-info strong {
  color: var(--primary);
}
.danger-btn {
  width: 100%;
  margin-top: 6px;
}
.tips {
  margin: 0;
  padding-left: 18px;
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.9;
}
@media (max-width: 900px) {
  .editor {
    height: auto;
    min-height: 0;
  }
  .hint {
    margin-left: 0;
    width: 100%;
  }
  .editor-body {
    flex-direction: column;
  }
  .palette {
    width: auto;
    overflow: visible;
  }
  .palette-list {
    max-height: none;
    overflow: visible;
    flex-direction: row;
    flex-wrap: wrap;
  }
  .palette-item {
    flex: 1 1 45%;
  }
  .canvas-wrap {
    height: 56vh;
    min-height: 340px;
    flex: none;
  }
  .inspector {
    width: auto;
  }
}
</style>