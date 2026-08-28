<template>
  <div class="layout">
    <aside class="sidebar" :class="{ open: sidebarOpen }">
      <div class="logo">
        <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.6">
          <circle cx="5" cy="12" r="2.4" />
          <circle cx="19" cy="5" r="2.4" />
          <circle cx="19" cy="19" r="2.4" />
          <path d="M7.2 11 16.8 6M7.2 13l9.6 5" />
        </svg>
        <span class="logo-text">网络实验室<small>拓扑与设备管理系统</small></span>
      </div>
      <SideMenu />
    </aside>
    <div v-if="sidebarOpen" class="backdrop" @click="sidebarOpen = false"></div>
    <section class="main">
      <TopBar @toggle-sidebar="sidebarOpen = !sidebarOpen" />
      <main class="content">
        <router-view v-slot="{ Component }">
          <transition name="fade-slide" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import SideMenu from './SideMenu.vue'
import TopBar from './TopBar.vue'

const route = useRoute()
const sidebarOpen = ref(false)

watch(
  () => route.path,
  () => {
    sidebarOpen.value = false
  },
)
</script>

<style scoped>
.layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}
.sidebar {
  width: 224px;
  flex-shrink: 0;
  background: var(--bg-sidebar);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  z-index: 1001;
}
.logo {
  height: 60px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 18px;
  border-bottom: 1px solid var(--border-color);
  color: var(--primary);
  flex-shrink: 0;
}
.logo-text {
  font-size: 15px;
  font-weight: 700;
  line-height: 1.25;
  color: var(--text-primary);
  display: flex;
  flex-direction: column;
}
.logo-text small {
  font-size: 11px;
  color: var(--text-weak);
  font-weight: 400;
}
.main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.content {
  flex: 1;
  overflow: auto;
  padding: 20px;
}
.backdrop {
  display: none;
}

@media (max-width: 900px) {
  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    width: 232px;
    transform: translateX(-100%);
    transition: transform 0.25s ease;
    box-shadow: var(--shadow-card);
  }
  .sidebar.open {
    transform: translateX(0);
  }
  .backdrop {
    display: block;
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.42);
    z-index: 1000;
  }
  .content {
    padding: 14px;
  }
}
@media (max-width: 480px) {
  .content {
    padding: 10px;
  }
}
</style>