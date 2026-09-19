<template>
  <header class="topbar">
    <div class="crumb">
      <button class="menu-btn" title="菜单" @click="emit('toggle-sidebar')">
        <el-icon :size="20"><Menu /></el-icon>
      </button>
      <span class="crumb-title">{{ title }}</span>
      <el-tag v-if="roleName" size="small" effect="plain" class="role-tag">{{ roleName }}</el-tag>
    </div>
    <div class="actions">
      <el-tooltip :content="theme.isDark ? '切换到浅色' : '切换到深色'" placement="bottom">
        <button class="icon-btn" @click="theme.toggle()">
          <el-icon :size="18"><Sunny v-if="theme.isDark" /><Moon v-else /></el-icon>
        </button>
      </el-tooltip>
      <el-dropdown trigger="click" @command="onCommand">
        <div class="user">
          <span class="avatar">{{ initial }}</span>
          <div class="user-info">
            <span class="name">{{ auth.displayName }}</span>
            <span class="role">{{ roleName }}</span>
          </div>
          <el-icon :size="14" class="arrow"><ArrowDown /></el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="logout" divided>
              <el-icon><SwitchButton /></el-icon>退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Menu } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import { ROLE_NAME } from '@/utils/constants'

const emit = defineEmits<{
  (e: 'toggle-sidebar'): void
}>()

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const theme = useThemeStore()

const title = computed(() => String(route.meta.title ?? ''))
const roleName = computed(() => ROLE_NAME[auth.role] ?? '')
const initial = computed(() => (auth.displayName || 'U').charAt(0))

async function onCommand(cmd: string) {
  if (cmd === 'logout') {
    await auth.logout()
    ElMessage.success('已退出登录')
    router.push('/login')
  }
}
</script>

<style scoped>
.topbar {
  height: 60px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  background: var(--bg-card);
  border-bottom: 1px solid var(--border-color);
}
.crumb {
  display: flex;
  align-items: center;
  gap: 10px;
}
.menu-btn {
  display: none;
  width: 34px;
  height: 34px;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
}
.menu-btn:hover {
  color: var(--primary);
  border-color: var(--primary);
}
.crumb-title {
  font-size: 16px;
  font-weight: 600;
}
.role-tag {
  border-radius: 4px;
}
.actions {
  display: flex;
  align-items: center;
  gap: 14px;
}
.icon-btn {
  width: 34px;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}
.icon-btn:hover {
  color: var(--primary);
  border-color: var(--primary);
}
.user {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 8px;
}
.user:hover {
  background: var(--bg-hover);
}
.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--primary);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
}
.user-info {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}
.name {
  font-size: 13px;
  color: var(--text-primary);
}
.role {
  font-size: 11px;
  color: var(--text-weak);
}
.arrow {
  color: var(--text-weak);
}
@media (max-width: 900px) {
  .menu-btn {
    display: inline-flex;
  }
  .user-info,
  .role-tag {
    display: none;
  }
  .topbar {
    padding: 0 12px;
  }
}
</style>