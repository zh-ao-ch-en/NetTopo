<template>
  <svg
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="1.6"
    stroke-linecap="round"
    stroke-linejoin="round"
  >
    <!-- 交换机 -->
    <template v-if="type === 'switch'">
      <rect x="3" y="7" width="18" height="10" rx="2" />
      <path d="M6.5 10v4 M9.5 10v4 M12.5 10v4 M15.5 10v4 M18.5 10v4" />
    </template>
    <!-- 路由器 -->
    <template v-else-if="type === 'router'">
      <rect x="3" y="10" width="18" height="10" rx="2" />
      <path d="M5 15h2.5 M9.5 15h2.5 M14 15h2 M18 15h1.5" />
      <path d="M12 9V5 M9 8l3-3 3 3" />
    </template>
    <!-- 防火墙 -->
    <template v-else-if="type === 'firewall'">
      <path d="M12 3l7 3v5c0 4-3.2 7-7 9-3.8-2-7-5-7-9V6l7-3z" />
      <path d="M9 12l2 2 4-4" />
    </template>
    <!-- 服务器 -->
    <template v-else-if="type === 'server'">
      <rect x="3" y="4" width="18" height="7" rx="1.5" />
      <rect x="3" y="13" width="18" height="7" rx="1.5" />
      <circle cx="6.5" cy="7.5" r="1" fill="currentColor" stroke="none" />
      <circle cx="6.5" cy="16.5" r="1" fill="currentColor" stroke="none" />
      <path d="M10.5 7.5h5 M10.5 16.5h5" />
    </template>
    <!-- 主机/PC -->
    <template v-else-if="type === 'pc'">
      <rect x="3" y="4" width="18" height="12" rx="1.5" />
      <path d="M9 20h6 M12 16v4" />
    </template>
    <!-- 无线AP -->
    <template v-else-if="type === 'ap'">
      <circle cx="12" cy="17" r="2" />
      <path d="M7.5 12.5a6.4 6.4 0 019 0" />
      <path d="M4.5 9.5a10.6 10.6 0 0115 0" />
      <path d="M12 9V7" />
    </template>
    <!-- 云 -->
    <template v-else-if="type === 'cloud'">
      <path d="M17.5 19H9a5 5 0 114.8-7.2 4.5 4.5 0 013.7 7.2z" />
    </template>
    <!-- 分组 -->
    <template v-else-if="type === 'group'">
      <rect x="3" y="3" width="18" height="18" rx="3" stroke-dasharray="4 3" />
    </template>
    <!-- 兜底 -->
    <template v-else>
      <rect x="3" y="7" width="18" height="10" rx="2" />
    </template>
  </svg>
</template>

<script setup lang="ts">
import type { DeviceType } from '@/types'

withDefaults(
  defineProps<{
    type: DeviceType | 'cloud' | 'group'
    size?: number
  }>(),
  { size: 20 },
)
</script>