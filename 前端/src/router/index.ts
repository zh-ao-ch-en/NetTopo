import { createRouter, createWebHashHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/Login.vue'),
    meta: { public: true },
  },
  {
    path: '/',
    component: () => import('@/components/layout/AppLayout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '状态监控', icon: 'Odometer' },
      },
      {
        path: 'devices',
        name: 'devices',
        component: () => import('@/views/DeviceList.vue'),
        meta: { title: '设备管理', icon: 'Cpu' },
      },
      {
        path: 'topology/view',
        name: 'topology-view',
        component: () => import('@/views/TopologyView.vue'),
        meta: { title: '拓扑查看', icon: 'Share' },
      },
      {
        path: 'topology/editor',
        name: 'topology-editor',
        component: () => import('@/views/TopologyEditor.vue'),
        meta: { title: '拓扑编辑', icon: 'EditPen' },
      },
      {
        path: 'users',
        name: 'users',
        component: () => import('@/views/UserManage.vue'),
        meta: { title: '用户管理', icon: 'User', roles: ['admin'] },
      },
    ],
  },
  { path: '/:pathMatch(.*)*', redirect: '/dashboard' },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.public) {
    if (to.name === 'login' && auth.isLoggedIn) return { path: '/' }
    return true
  }
  if (!auth.isLoggedIn) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }
  if (to.meta.roles && !(to.meta.roles as string[]).includes(auth.role)) {
    return { path: '/dashboard' }
  }
  return true
})

export default router