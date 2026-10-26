<template>
  <el-card>
    <div class="toolbar">
      <el-button type="primary" @click="openCreate">新建批次</el-button>
    </div>

    <el-table :data="list" v-loading="loading">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="product_name" label="产品" />
      <el-table-column prop="trace_code" label="溯源码" />
      <el-table-column prop="production_date" label="生产日期" width="110" />
      <el-table-column label="数量" width="110">
        <template #default="{ row }">{{ row.quantity }}{{ row.unit }}</template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="row.status === '已上市' ? 'success' : 'warning'" size="small">{{ row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="230">
        <template #default="{ row }">
          <el-button link type="primary" @click="openQr(row)">二维码</el-button>
          <el-button link type="primary" @click="$router.push(`/batches/${row.id}`)">详情</el-button>
          <el-button link type="danger" @click="onDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="createVisible" title="新建批次" width="460px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="产品">
          <el-select v-model="form.product_id" placeholder="请选择产品" filterable style="width: 100%">
            <el-option v-for="p in products" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="生产日期">
          <el-date-picker v-model="form.production_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="数量"><el-input v-model="form.quantity" /></el-form-item>
        <el-form-item label="单位"><el-input v-model="form.unit" placeholder="如 kg、箱" /></el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width: 100%">
            <el-option v-for="s in ['生产中', '加工中', '已上市']" :key="s" :label="s" :value="s" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createVisible = false">取消</el-button>
        <el-button type="primary" @click="onCreate">创建</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="qrVisible" title="批次二维码" width="360px">
      <div v-if="qr" class="qr-box">
        <img :src="assetUrl(qr.qr_code)" class="qr-img" />
        <div class="qr-code">{{ qr.trace_code }}</div>
        <el-button type="primary" size="small" @click="downloadQr">下载二维码</el-button>
      </div>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { assetUrl, batchApi, productApi } from '../api'

const list = ref([])
const products = ref([])
const loading = ref(false)
const createVisible = ref(false)
const qrVisible = ref(false)
const qr = ref(null)
const form = reactive({ product_id: null, production_date: '', quantity: '', unit: 'kg', status: '生产中' })

async function load() {
  loading.value = true
  try {
    const res = await batchApi.list()
    list.value = res.data
  } finally {
    loading.value = false
  }
}

async function loadProducts() {
  const res = await productApi.list({})
  products.value = res.data
}

function openCreate() {
  form.product_id = null
  form.production_date = ''
  form.quantity = ''
  form.unit = 'kg'
  form.status = '生产中'
  createVisible.value = true
}

async function onCreate() {
  if (!form.product_id) return ElMessage.warning('请选择产品')
  await batchApi.create({ ...form })
  ElMessage.success('批次创建成功')
  createVisible.value = false
  load()
}

async function openQr(row) {
  const res = await batchApi.qrcode(row.id)
  qr.value = res.data
  qrVisible.value = true
}

function downloadQr() {
  const a = document.createElement('a')
  a.href = assetUrl(qr.value.qr_code)
  a.download = `${qr.value.trace_code}.png`
  a.click()
}

function onDelete(row) {
  ElMessageBox.confirm(`确定删除批次「${row.trace_code}」吗？关联记录将一并删除。`, '提示', { type: 'warning' })
    .then(async () => {
      await batchApi.remove(row.id)
      ElMessage.success('删除成功')
      load()
    })
    .catch(() => {})
}

onMounted(() => {
  load()
  loadProducts()
})
</script>

<style scoped>
.toolbar { margin-bottom: 12px; }
.qr-box { display: flex; flex-direction: column; align-items: center; gap: 12px; }
.qr-img { width: 200px; height: 200px; }
.qr-code { font-family: monospace; }
</style>
