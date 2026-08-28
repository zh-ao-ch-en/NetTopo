<template>
  <div>
    <h2 class="page-title">用户管理</h2>
    <p class="page-subtitle">管理系统账号与角色（仅系统管理员可见）</p>

    <div class="toolbar card">
      <span class="toolbar-tip">不同角色拥有不同权限：管理员/教师可编辑，学生只读</span>
      <el-button type="primary" :icon="Plus" @click="openCreate">新增用户</el-button>
    </div>

    <div class="card table-card">
      <el-table :data="rows" v-loading="loading" style="width: 100%">
        <el-table-column prop="username" label="用户名" width="130" />
        <el-table-column prop="displayName" label="姓名" width="120" />
        <el-table-column label="角色" width="130">
          <template #default="{ row }">
            <el-tag :type="roleTagType(row.role)" size="small">{{ ROLE_NAME[row.role as Role] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="email" label="邮箱" min-width="160" show-overflow-tooltip />
        <el-table-column prop="phone" label="电话" width="130" />
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.enabled ? 'success' : 'info'" size="small">{{ row.enabled ? '启用' : '禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="创建时间" width="120" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" text type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" text type="danger" :disabled="row.id === auth.user?.id" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑用户' : '新增用户'" width="480px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="用户名" required>
          <el-input v-model="form.username" :disabled="isEdit" placeholder="登录账号" />
        </el-form-item>
        <el-form-item label="姓名" required>
          <el-input v-model="form.displayName" />
        </el-form-item>
        <el-form-item :label="isEdit ? '重置密码' : '密码'" :required="!isEdit">
          <el-input v-model="form.password" type="password" show-password :placeholder="isEdit ? '留空则不修改' : '初始密码'" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="form.role" style="width: 100%">
            <el-option v-for="(label, val) in ROLE_NAME" :key="val" :label="label" :value="val" />
          </el-select>
        </el-form-item>
        <el-form-item label="邮箱"><el-input v-model="form.email" /></el-form-item>
        <el-form-item label="电话"><el-input v-model="form.phone" /></el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="form.enabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="submit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import type { Role, User } from '@/types'
import { ROLE_NAME } from '@/utils/constants'
import { createUser, deleteUser, listUsers, updateUser } from '@/api/user'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const loading = ref(false)
const saving = ref(false)
const rows = ref<User[]>([])
const dialogVisible = ref(false)
const isEdit = ref(false)

interface UserForm {
  id: string
  username: string
  password: string
  displayName: string
  role: Role
  email: string
  phone: string
  enabled: boolean
}

const form = reactive<UserForm>({
  id: '',
  username: '',
  password: '',
  displayName: '',
  role: 'student',
  email: '',
  phone: '',
  enabled: true,
})

function roleTagType(role: Role) {
  if (role === 'admin') return 'danger'
  if (role === 'lab_admin') return 'warning'
  if (role === 'student') return 'success'
  return 'info'
}

async function load() {
  loading.value = true
  try {
    rows.value = await listUsers()
  } finally {
    loading.value = false
  }
}

function openCreate() {
  Object.assign(form, { id: '', username: '', password: '', displayName: '', role: 'student', email: '', phone: '', enabled: true })
  isEdit.value = false
  dialogVisible.value = true
}

function openEdit(row: User) {
  Object.assign(form, { ...row, password: '' })
  isEdit.value = true
  dialogVisible.value = true
}

async function submit() {
  if (!form.username || !form.displayName) {
    ElMessage.warning('请填写用户名和姓名')
    return
  }
  if (!isEdit.value && !form.password) {
    ElMessage.warning('请填写初始密码')
    return
  }
  saving.value = true
  try {
    const payload: Partial<User> & { password?: string } = {
      username: form.username,
      displayName: form.displayName,
      role: form.role,
      email: form.email,
      phone: form.phone,
      enabled: form.enabled,
    }
    if (form.password) payload.password = form.password
    if (isEdit.value) {
      await updateUser(form.id, payload)
      ElMessage.success('用户已更新')
    } else {
      await createUser(payload)
      ElMessage.success('用户已创建')
    }
    dialogVisible.value = false
    load()
  } catch (e) {
    ElMessage.error((e as Error).message || '保存失败')
  } finally {
    saving.value = false
  }
}

async function remove(row: User) {
  try {
    await ElMessageBox.confirm(`确定删除用户「${row.displayName}」吗？`, '删除确认', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
  } catch {
    return
  }
  try {
    await deleteUser(row.id)
    ElMessage.success('已删除')
    load()
  } catch (e) {
    ElMessage.error((e as Error).message || '删除失败')
  }
}

onMounted(load)
</script>

<style scoped>
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  margin-bottom: 16px;
}
.toolbar-tip {
  font-size: 13px;
  color: var(--text-secondary);
}
.table-card {
  padding: 8px 16px 16px;
}
@media (max-width: 720px) {
  .toolbar {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }
  .toolbar-tip {
    text-align: center;
  }
}
</style>