<template>
  <el-card>
    <div class="toolbar">
      <el-button type="primary" @click="openDialog()">新增用户</el-button>
    </div>

    <el-table :data="list" v-loading="loading">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="username" label="用户名" />
      <el-table-column prop="name" label="姓名" />
      <el-table-column label="角色" width="110">
        <template #default="{ row }">
          <el-tag :type="roleType(row.role)" size="small">{{ roleText(row.role) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="phone" label="手机号" />
      <el-table-column prop="created_at" label="创建时间" width="170" />
      <el-table-column label="操作" width="150">
        <template #default="{ row }">
          <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
          <el-button link type="danger" @click="onDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="visible" :title="form.id ? '编辑用户' : '新增用户'" width="440px">
      <el-form :model="form" label-width="70px">
        <el-form-item label="用户名"><el-input v-model="form.username" :disabled="!!form.id" /></el-form-item>
        <el-form-item label="姓名"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="手机号"><el-input v-model="form.phone" /></el-form-item>
        <el-form-item label="角色">
          <el-select v-model="form.role" style="width: 100%">
            <el-option label="管理员" value="admin" />
            <el-option label="生产者" value="producer" />
            <el-option label="消费者" value="consumer" />
          </el-select>
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" show-password :placeholder="form.id ? '留空则不修改' : '请输入初始密码'" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="visible = false">取消</el-button>
        <el-button type="primary" @click="onSave">保存</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { userApi } from '../api'

const list = ref([])
const loading = ref(false)
const visible = ref(false)
const form = reactive({ id: null, username: '', name: '', phone: '', role: 'producer', password: '' })

function roleText(r) {
  return { admin: '管理员', producer: '生产者', consumer: '消费者' }[r] || r
}
function roleType(r) {
  return { admin: 'danger', producer: 'warning', consumer: 'info' }[r] || 'info'
}

async function load() {
  loading.value = true
  try {
    const res = await userApi.list()
    list.value = res.data
  } finally {
    loading.value = false
  }
}

function openDialog(row) {
  form.id = row?.id || null
  form.username = row?.username || ''
  form.name = row?.name || ''
  form.phone = row?.phone || ''
  form.role = row?.role || 'producer'
  form.password = ''
  visible.value = true
}

async function onSave() {
  if (!form.id && (!form.username || !form.password)) return ElMessage.warning('请填写用户名和密码')
  const payload = { name: form.name, phone: form.phone, role: form.role }
  if (form.id) {
    if (form.password) payload.password = form.password
    await userApi.update(form.id, payload)
  } else {
    payload.username = form.username
    payload.password = form.password
    await userApi.create(payload)
  }
  ElMessage.success('保存成功')
  visible.value = false
  load()
}

function onDelete(row) {
  ElMessageBox.confirm(`确定删除用户「${row.username}」吗？`, '提示', { type: 'warning' })
    .then(async () => {
      await userApi.remove(row.id)
      ElMessage.success('删除成功')
      load()
    })
    .catch(() => {})
}

onMounted(load)
</script>

<style scoped>
.toolbar { margin-bottom: 12px; }
</style>
