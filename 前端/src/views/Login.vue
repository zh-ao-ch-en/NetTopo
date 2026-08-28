<template>
  <div class="login-page">
    <div class="grid-overlay"></div>
    <div class="login-card card">
      <div class="login-header">
        <svg viewBox="0 0 24 24" width="44" height="44" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="5" cy="12" r="2.4" />
          <circle cx="19" cy="5" r="2.4" />
          <circle cx="19" cy="19" r="2.4" />
          <path d="M7.2 11 16.8 6M7.2 13l9.6 5" />
        </svg>
        <h1>网络实验室拓扑与设备管理系统</h1>
        <p>Network Lab Topology &amp; Device Management System</p>
      </div>

      <el-form :model="form" @submit.prevent="onSubmit">
        <el-form-item>
          <el-input v-model="form.username" size="large" placeholder="用户名" :prefix-icon="User" clearable />
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="form.password"
            type="password"
            size="large"
            placeholder="密码"
            :prefix-icon="Lock"
            show-password
            @keyup.enter="onSubmit"
          />
        </el-form-item>
        <el-button type="primary" size="large" class="login-btn" :loading="loading" @click="onSubmit">
          登 录
        </el-button>
      </el-form>

      <div class="demo-tips">
        <span class="tips-label">演示账号（点击填充）</span>
        <el-tag v-for="a in demo" :key="a.username" class="demo-tag" effect="plain" @click="fill(a)">
          {{ a.label }}
        </el-tag>
      </div>
    </div>
    <p class="footer-tip">仅前端演示 · 数据接口为本地 mock · 后端接入见 README</p>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import type { LoginPayload } from '@/types'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const form = ref<LoginPayload>({ username: 'admin', password: 'admin123' })
const loading = ref(false)

const demo = [
  { label: '管理员 admin/admin123', username: 'admin', password: 'admin123' },
  { label: '教师 teacher/teacher123', username: 'teacher', password: 'teacher123' },
  { label: '学生 student/student123', username: 'student', password: 'student123' },
]

function fill(a: { username: string; password: string }) {
  form.value = { username: a.username, password: a.password }
}

async function onSubmit() {
  if (!form.value.username || !form.value.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  loading.value = true
  try {
    await auth.login(form.value)
    ElMessage.success('登录成功')
    const redirect = (route.query.redirect as string) || '/'
    router.push(redirect)
  } catch (e) {
    ElMessage.error((e as Error).message || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  position: relative;
  height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: radial-gradient(circle at 20% 20%, var(--primary-soft) 0%, transparent 45%), var(--bg-page);
  overflow: hidden;
}
.grid-overlay {
  position: absolute;
  inset: 0;
  background-image: linear-gradient(var(--border-color) 1px, transparent 1px),
    linear-gradient(90deg, var(--border-color) 1px, transparent 1px);
  background-size: 42px 42px;
  opacity: 0.35;
  mask-image: radial-gradient(circle at 50% 40%, #000 20%, transparent 75%);
}
.login-card {
  position: relative;
  width: 400px;
  padding: 38px 36px 28px;
  z-index: 1;
}
.login-header {
  text-align: center;
  color: var(--primary);
  margin-bottom: 28px;
}
.login-header h1 {
  font-size: 18px;
  margin: 14px 0 6px;
  color: var(--text-primary);
}
.login-header p {
  font-size: 12px;
  color: var(--text-weak);
  margin: 0;
}
.login-btn {
  width: 100%;
  margin-top: 4px;
  letter-spacing: 4px;
  font-weight: 600;
}
.demo-tips {
  margin-top: 22px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  justify-content: center;
}
.tips-label {
  font-size: 12px;
  color: var(--text-weak);
  width: 100%;
  text-align: center;
  margin-bottom: 2px;
}
.demo-tag {
  cursor: pointer;
}
.footer-tip {
  position: absolute;
  bottom: 22px;
  font-size: 12px;
  color: var(--text-weak);
  z-index: 1;
}
@media (max-width: 480px) {
  .login-card {
    width: 92%;
    padding: 28px 22px 22px;
  }
  .login-header h1 {
    font-size: 16px;
  }
}
</style>