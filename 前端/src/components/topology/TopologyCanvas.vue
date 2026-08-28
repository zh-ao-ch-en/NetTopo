<template>
  <div ref="wrapRef" class="topo-canvas">
    <svg ref="svgRef" @wheel.prevent="onWheel" @mousedown="onCanvasMouseDown">
      <g :transform="`translate(${panX},${panY}) scale(${scale})`">
        <!-- 连线 -->
        <g class="edges">
          <path
            v-for="e in edges"
            :key="e.id"
            :d="edgePath(e)"
            class="edge"
            :class="{ dashed: e.style === 'dashed', selected: e.id === selectedEdgeId }"
            fill="none"
            @click.stop="emit('selectEdge', e.id)"
          />
        </g>
        <!-- 节点 -->
        <g class="nodes">
          <g
            v-for="n in nodes"
            :key="n.id"
            class="node"
            :class="{ selected: n.id === selectedId, movable: editable }"
            :transform="`translate(${n.x},${n.y})`"
            @mousedown="onNodeMouseDown($event, n)"
          >
            <rect class="node-bg" :width="n.width" :height="n.height" rx="8" />
            <g class="node-icon" :transform="`translate(16,${n.height / 2 - 12})`">
              <DeviceIcon :type="n.type" :size="24" />
            </g>
            <text class="node-label" x="52" :y="n.height / 2 + 4">{{ shortLabel(n.label) }}</text>
            <circle class="status-dot" :class="statusClass(n)" :cx="n.width - 10" cy="12" r="4" />
            <rect
              v-if="editable"
              class="resize-handle"
              :x="n.width - 12"
              :y="n.height - 12"
              width="12"
              height="12"
              @mousedown.stop="onResizeMouseDown($event, n)"
            />
          </g>
        </g>
      </g>
    </svg>
    <div class="canvas-tools">
      <button class="tool-btn" title="放大" @click="zoomBy(1.15)">＋</button>
      <button class="tool-btn" title="缩小" @click="zoomBy(1 / 1.15)">－</button>
      <button class="tool-btn" title="适应画布" @click="fitView">⤢</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import type { DeviceStatus, TopologyEdge, TopologyNode } from '@/types'
import DeviceIcon from '@/components/DeviceIcon.vue'

const props = withDefaults(
  defineProps<{
    nodes: TopologyNode[]
    edges: TopologyEdge[]
    editable?: boolean
    selectedId?: string | null
    selectedEdgeId?: string | null
    deviceStatus?: Record<string, DeviceStatus>
  }>(),
  {
    editable: false,
    selectedId: null,
    selectedEdgeId: null,
    deviceStatus: () => ({}),
  },
)

const emit = defineEmits<{
  (e: 'selectNode', id: string | null): void
  (e: 'selectEdge', id: string | null): void
  (e: 'moveNode', id: string, x: number, y: number): void
  (e: 'resizeNode', id: string, width: number, height: number): void
}>()

const wrapRef = ref<HTMLDivElement>()
const svgRef = ref<SVGSVGElement>()
const scale = ref(1)
const panX = ref(0)
const panY = ref(0)

type DragState =
  | { kind: 'pan'; startX: number; startY: number; origPanX: number; origPanY: number; moved: boolean }
  | { kind: 'node'; id: string; startX: number; startY: number; offsetX: number; offsetY: number; moved: boolean }
  | { kind: 'resize'; id: string; startX: number; startY: number; origW: number; origH: number; moved: boolean }
  | null

let dragState: DragState = null

function svgRect(): DOMRect {
  return svgRef.value!.getBoundingClientRect()
}

function worldPoint(clientX: number, clientY: number) {
  const r = svgRect()
  return {
    x: (clientX - r.left - panX.value) / scale.value,
    y: (clientY - r.top - panY.value) / scale.value,
  }
}

function nodeById(id: string): TopologyNode | undefined {
  return props.nodes.find((n) => n.id === id)
}

function shortLabel(s: string, max = 9): string {
  return s.length > max ? s.slice(0, max) + '…' : s
}

function statusClass(n: TopologyNode): string {
  const st = n.status ?? props.deviceStatus[n.deviceId ?? ''] ?? 'online'
  return `st-${st}`
}

function edgePath(e: TopologyEdge): string {
  const s = nodeById(e.source)
  const t = nodeById(e.target)
  if (!s || !t) return ''
  const ax = s.x + s.width / 2
  const ay = s.y + s.height / 2
  const bx = t.x + t.width / 2
  const by = t.y + t.height / 2
  const c = Math.min(60, Math.abs(bx - ax) / 2)
  return `M ${ax} ${ay} C ${ax + c} ${ay}, ${bx - c} ${by}, ${bx} ${by}`
}

function onWheel(e: WheelEvent) {
  const r = svgRect()
  const mx = e.clientX - r.left
  const my = e.clientY - r.top
  const factor = e.deltaY < 0 ? 1.1 : 1 / 1.1
  const next = Math.min(2.5, Math.max(0.25, scale.value * factor))
  const k = next / scale.value
  panX.value = mx - (mx - panX.value) * k
  panY.value = my - (my - panY.value) * k
  scale.value = next
}

function zoomBy(factor: number) {
  const r = svgRect()
  const mx = r.width / 2
  const my = r.height / 2
  const next = Math.min(2.5, Math.max(0.25, scale.value * factor))
  const k = next / scale.value
  panX.value = mx - (mx - panX.value) * k
  panY.value = my - (my - panY.value) * k
  scale.value = next
}

function onCanvasMouseDown(e: MouseEvent) {
  if (e.button !== 0) return
  dragState = { kind: 'pan', startX: e.clientX, startY: e.clientY, origPanX: panX.value, origPanY: panY.value, moved: false }
  window.addEventListener('mousemove', onMove)
  window.addEventListener('mouseup', onUp)
}

function onNodeMouseDown(e: MouseEvent, n: TopologyNode) {
  if (e.button !== 0) return
  e.stopPropagation()
  if (!props.editable) {
    emit('selectNode', n.id)
    return
  }
  e.preventDefault()
  const p = worldPoint(e.clientX, e.clientY)
  dragState = { kind: 'node', id: n.id, startX: e.clientX, startY: e.clientY, offsetX: p.x - n.x, offsetY: p.y - n.y, moved: false }
  window.addEventListener('mousemove', onMove)
  window.addEventListener('mouseup', onUp)
}

const MIN_NODE_W = 88
const MIN_NODE_H = 44

function onResizeMouseDown(e: MouseEvent, n: TopologyNode) {
  if (e.button !== 0 || !props.editable) return
  e.stopPropagation()
  e.preventDefault()
  dragState = { kind: 'resize', id: n.id, startX: e.clientX, startY: e.clientY, origW: n.width, origH: n.height, moved: false }
  window.addEventListener('mousemove', onMove)
  window.addEventListener('mouseup', onUp)
}

function onMove(e: MouseEvent) {
  if (!dragState) return
  const dx = e.clientX - dragState.startX
  const dy = e.clientY - dragState.startY
  if (Math.abs(dx) + Math.abs(dy) > 3) dragState.moved = true
  if (dragState.kind === 'pan') {
    panX.value = dragState.origPanX + dx
    panY.value = dragState.origPanY + dy
  } else if (dragState.kind === 'node') {
    const p = worldPoint(e.clientX, e.clientY)
    emit('moveNode', dragState.id, Math.round(p.x - dragState.offsetX), Math.round(p.y - dragState.offsetY))
  } else if (dragState.kind === 'resize') {
    const w = Math.max(MIN_NODE_W, Math.round(dragState.origW + dx / scale.value))
    const h = Math.max(MIN_NODE_H, Math.round(dragState.origH + dy / scale.value))
    emit('resizeNode', dragState.id, w, h)
  }
}

function onUp() {
  window.removeEventListener('mousemove', onMove)
  window.removeEventListener('mouseup', onUp)
  const st = dragState
  dragState = null
  if (st && !st.moved) {
    if (st.kind === 'pan') emit('selectNode', null)
    else if (st.kind === 'node') emit('selectNode', st.id)
  }
}

function fitView() {
  const r = svgRef.value!.getBoundingClientRect()
  const cw = r.width || 800
  const ch = r.height || 500
  if (!props.nodes.length) {
    scale.value = 1
    panX.value = 60
    panY.value = 40
    return
  }
  let minX = Infinity
  let minY = Infinity
  let maxX = -Infinity
  let maxY = -Infinity
  for (const n of props.nodes) {
    minX = Math.min(minX, n.x)
    minY = Math.min(minY, n.y)
    maxX = Math.max(maxX, n.x + n.width)
    maxY = Math.max(maxY, n.y + n.height)
  }
  const w = maxX - minX
  const h = maxY - minY
  const pad = 80
  const s = Math.min((cw - pad * 2) / w, (ch - pad * 2) / h, 1.4)
  scale.value = Math.max(0.2, s)
  panX.value = (cw - w * scale.value) / 2 - minX * scale.value
  panY.value = (ch - h * scale.value) / 2 - minY * scale.value
}

onMounted(() => {
  setTimeout(fitView, 50)
})

defineExpose({ fitView })
</script>

<style scoped>
.topo-canvas {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
  background: radial-gradient(circle at 50% 0%, var(--bg-hover) 0%, var(--bg-card) 70%);
  cursor: grab;
}
.topo-canvas:active {
  cursor: grabbing;
}
svg {
  width: 100%;
  height: 100%;
  display: block;
}
.edge {
  stroke: var(--text-weak);
  stroke-width: 1.6;
  opacity: 0.7;
}
.edge.dashed {
  stroke-dasharray: 6 5;
}
.edge:hover {
  stroke: var(--primary);
  stroke-width: 2;
}
.edge.selected {
  stroke: var(--primary);
  stroke-width: 2;
  opacity: 1;
}
.node {
  cursor: pointer;
}
.node.movable {
  cursor: move;
}
.node-bg {
  fill: var(--bg-card);
  stroke: var(--border-color);
  stroke-width: 1.2;
  transition: stroke 0.15s;
}
.node:hover .node-bg {
  stroke: var(--primary);
}
.node.selected .node-bg {
  stroke: var(--primary);
  stroke-width: 2;
  filter: drop-shadow(0 0 6px var(--primary-soft));
}
.node-icon {
  color: var(--primary);
}
.node-label {
  fill: var(--text-primary);
  font-size: 11.5px;
  font-weight: 500;
}
.status-dot {
  stroke: none;
}
.resize-handle {
  fill: var(--primary);
  opacity: 0;
  cursor: nwse-resize;
}
.node:hover .resize-handle,
.node.selected .resize-handle {
  opacity: 0.9;
}
.st-online {
  fill: var(--success);
}
.st-offline {
  fill: var(--info);
}
.st-warning {
  fill: var(--warning);
}
.st-error {
  fill: var(--danger);
}
.canvas-tools {
  position: absolute;
  right: 14px;
  bottom: 14px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.tool-btn {
  width: 34px;
  height: 34px;
  border: 1px solid var(--border-color);
  background: var(--bg-card);
  color: var(--text-primary);
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  box-shadow: var(--shadow-card);
}
.tool-btn:hover {
  border-color: var(--primary);
  color: var(--primary);
}
</style>