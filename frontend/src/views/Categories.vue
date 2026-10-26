<template>
  <el-card>
    <div class="toolbar">
      <el-button type="primary" @click="openDialog()">新增分类</el-button>
    </div>
    <el-table :data="list" v-loading="loading">
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="name" label="分类名称" />
      <el-table-column prop="description" label="描述" />
      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
          <el-button link type="danger" @click="onDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="visible" :title="form.id ? '编辑分类' : '新增分类'" width="420px">
      <el-form :model="form" label-width="70px">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" type="textarea" /></el-form-item>
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
import { categoryApi } from '../api'

const list = ref([])
const loading = ref(false)
const visible = ref(false)
const form = reactive({ id: null, name: '', description: '' })

async function load() {
  loading.value = true
  try {
    const res = await categoryApi.list()
    list.value = res.data
  } finally {
    loading.value = false
  }
}

function openDialog(row) {
  form.id = row?.id || null
  form.name = row?.name || ''
  form.description = row?.description || ''
  visible.value = true
}

async function onSave() {
  if (!form.name) return ElMessage.warning('请输入分类名称')
  if (form.id) await categoryApi.update(form.id, { name: form.name, description: form.description })
  else await categoryApi.create({ name: form.name, description: form.description })
  ElMessage.success('保存成功')
  visible.value = false
  load()
}

function onDelete(row) {
  ElMessageBox.confirm(`确定删除分类「${row.name}」吗？`, '提示', { type: 'warning' })
    .then(async () => {
      await categoryApi.remove(row.id)
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
