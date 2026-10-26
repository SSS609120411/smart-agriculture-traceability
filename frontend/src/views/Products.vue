<template>
  <el-card>
    <div class="toolbar">
      <el-select v-model="filterCategory" placeholder="按分类筛选" clearable style="width: 200px" @change="load">
        <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
      </el-select>
      <el-button type="primary" @click="openDialog()">新增产品</el-button>
    </div>

    <el-table :data="list" v-loading="loading">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="产品名称" />
      <el-table-column prop="category_name" label="分类" width="100" />
      <el-table-column prop="origin" label="产地" />
      <el-table-column prop="variety" label="品种" width="120" />
      <el-table-column prop="description" label="描述" show-overflow-tooltip />
      <el-table-column label="操作" width="150">
        <template #default="{ row }">
          <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
          <el-button link type="danger" @click="onDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="visible" :title="form.id ? '编辑产品' : '新增产品'" width="480px">
      <el-form :model="form" label-width="70px">
        <el-form-item label="分类">
          <el-select v-model="form.category_id" placeholder="请选择分类" style="width: 100%">
            <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="产地"><el-input v-model="form.origin" /></el-form-item>
        <el-form-item label="品种"><el-input v-model="form.variety" /></el-form-item>
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
import { categoryApi, productApi } from '../api'

const list = ref([])
const categories = ref([])
const filterCategory = ref(null)
const loading = ref(false)
const visible = ref(false)
const form = reactive({ id: null, category_id: null, name: '', origin: '', variety: '', description: '' })

async function loadCategories() {
  const res = await categoryApi.list()
  categories.value = res.data
}

async function load() {
  loading.value = true
  try {
    const res = await productApi.list(filterCategory.value ? { category_id: filterCategory.value } : {})
    list.value = res.data
  } finally {
    loading.value = false
  }
}

function openDialog(row) {
  form.id = row?.id || null
  form.category_id = row?.category_id || null
  form.name = row?.name || ''
  form.origin = row?.origin || ''
  form.variety = row?.variety || ''
  form.description = row?.description || ''
  visible.value = true
}

async function onSave() {
  if (!form.name) return ElMessage.warning('请输入产品名称')
  const payload = { ...form }
  if (form.id) await productApi.update(form.id, payload)
  else await productApi.create(payload)
  ElMessage.success('保存成功')
  visible.value = false
  load()
}

function onDelete(row) {
  ElMessageBox.confirm(`确定删除产品「${row.name}」吗？`, '提示', { type: 'warning' })
    .then(async () => {
      await productApi.remove(row.id)
      ElMessage.success('删除成功')
      load()
    })
    .catch(() => {})
}

onMounted(() => {
  loadCategories()
  load()
})
</script>

<style scoped>
.toolbar { margin-bottom: 12px; display: flex; gap: 12px; }
</style>
