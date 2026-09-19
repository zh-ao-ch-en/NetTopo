<template>
  <el-menu
    class="side-menu"
    :default-active="active"
    router
    :collapse="false"
  >
    <el-menu-item index="/dashboard">
      <el-icon><Odometer /></el-icon>
      <span>状态监控</span>
    </el-menu-item>
    <el-menu-item index="/devices">
      <el-icon><Cpu /></el-icon>
      <span>设备管理</span>
    </el-menu-item>
    <el-menu-item index="/topology/view">
      <el-icon><Share /></el-icon>
      <span>拓扑查看</span>
    </el-menu-item>
    <el-menu-item index="/topology/editor">
      <el-icon><EditPen /></el-icon>
      <span>拓扑编辑</span>
    </el-menu-item>
    <el-menu-item v-if="canManageUsers(auth.role)" index="/users">
      <el-icon><User /></el-icon>
      <span>用户管理</span>
    </el-menu-item>
  </el-menu>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { canManageUsers } from '@/utils/permission'

const route = useRoute()
const auth = useAuthStore()
const active = computed(() => route.path)
</script>

<style scoped>
.side-menu {
  border-right: none;
  flex: 1;
  background: transparent;
  padding: 8px;
}
.side-menu :deep(.el-menu-item) {
  border-radius: 8px;
  margin-bottom: 4px;
  height: 42px;
  color: var(--text-secondary);
}
.side-menu :deep(.el-menu-item:hover) {
  background: var(--bg-hover);
  color: var(--text-primary);
}
.side-menu :deep(.el-menu-item.is-active) {
  background: var(--primary-soft);
  color: var(--primary);
}
</style>