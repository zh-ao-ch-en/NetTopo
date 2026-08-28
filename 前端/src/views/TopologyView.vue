<template>
  <div>
    <div class="head">
      <div>
        <h2 class="page-title">拓扑查看</h2>
        <p class="page-subtitle">{{ topoName }} · {{ nodes.length }} 个节点 / {{ edges.length }} 条连线</p>
      </div>
      <el-button type="primary" :icon="EditPen" @click="router.push('/topology/editor')">进入编辑器</el-button>
    </div>

    <div class="card view-body" v-loading="loading">
      <TopologyCanvas
        ref="canvasRef"
        :nodes="nodes"
        :edges="edges"
        :device-status="deviceStatus"
        @select-node="onSelect"
        @select-edge="() => {}"
      />
      <div class="view-tip">点击设备节点将跳转到设备管理并展示该设备详情</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { EditPen } from '@element-plus/icons-vue'
import type { Device, DeviceStatus, TopologyEdge, TopologyNode } from '@/types'
import { getTopology } from '@/api/topology'
import { listAllDevices } from '@/api/device'
import TopologyCanvas from '@/components/topology/TopologyCanvas.vue'

const router = useRouter()
const loading = ref(false)
const topoName = ref('')
const nodes = ref<TopologyNode[]>([])
const edges = ref<TopologyEdge[]>([])
const devices = ref<Device[]>([])

const deviceStatus = computed<Record<string, DeviceStatus>>(() => {
  const map: Record<string, DeviceStatus> = {}
  for (const d of devices.value) map[d.id] = d.status
  return map
})

function onSelect(id: string | null) {
  if (!id) return
  const node = nodes.value.find((n) => n.id === id)
  if (node?.deviceId) {
    router.push({ path: '/devices', query: { device: node.deviceId } })
  }
}

async function load() {
  loading.value = true
  try {
    const [topo, all] = await Promise.all([getTopology(), listAllDevices()])
    topoName.value = topo.name
    nodes.value = topo.nodes
    edges.value = topo.edges
    devices.value = all
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}
.view-body {
  position: relative;
  height: calc(100vh - 180px);
  min-height: 420px;
  overflow: hidden;
}
.view-tip {
  position: absolute;
  left: 14px;
  bottom: 14px;
  font-size: 12px;
  color: var(--text-weak);
  pointer-events: none;
}
</style>