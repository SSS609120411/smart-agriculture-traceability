<template>
  <div v-loading="loading">
    <el-card class="mb" v-if="batch">
      <div class="batch-head">
        <div>
          <div class="b-title">{{ batch.product_name }}</div>
          <div class="b-sub">
            溯源码：<el-tag>{{ batch.trace_code }}</el-tag>
            状态：<el-tag :type="batch.status === '已上市' ? 'success' : 'warning'">{{ batch.status }}</el-tag>
          </div>
          <div class="b-sub">生产日期：{{ batch.production_date }}　数量：{{ batch.quantity }}{{ batch.unit }}</div>
        </div>
        <div class="qr" v-if="qr">
          <img :src="assetUrl(qr.qr_code)" class="qr-img" />
          <div class="qr-code">{{ qr.trace_code }}</div>
        </div>
      </div>
    </el-card>

    <el-card>
      <el-tabs v-model="activeStage">
        <el-tab-pane v-for="s in stageConfig" :key="s.key" :label="s.label" :name="s.key">
          <el-button type="primary" size="small" class="mb" @click="openAdd(s)">新增{{ s.label }}记录</el-button>
          <el-table :data="records[s.key]" size="small" border>
            <el-table-column v-for="f in s.fields" :key="f.prop" :prop="f.prop" :label="f.label" show-overflow-tooltip />
            <el-table-column label="操作" width="80">
              <template #default="{ row }">
                <el-button link type="danger" @click="onDeleteRecord(s.key, row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!records[s.key].length" description="暂无记录" :image-size="60" />
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="'新增' + (currentStage?.label || '') + '记录'" width="480px">
      <el-form :model="recordForm" label-width="90px">
        <el-form-item v-for="f in currentStage?.fields" :key="f.prop" :label="f.label">
          <el-input v-model="recordForm[f.prop]" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="onSaveRecord">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { assetUrl, batchApi, recordApi } from '../api'

const route = useRoute()
const batchId = Number(route.params.id)

const batch = ref(null)
const qr = ref(null)
const loading = ref(false)
const activeStage = ref('planting')
const dialogVisible = ref(false)
const currentStage = ref(null)
const recordForm = ref({})
const records = reactive({ planting: [], quality: [], processing: [], logistics: [], sales: [] })

const stageConfig = [
  {
    key: 'planting', label: '种植',
    fields: [
      { prop: 'record_type', label: '类型' },
      { prop: 'detail', label: '详情' },
      { prop: 'record_date', label: '日期' },
      { prop: 'location', label: '位置' },
    ],
  },
  {
    key: 'quality', label: '质检',
    fields: [
      { prop: 'inspect_date', label: '检测日期' },
      { prop: 'inspector', label: '检测人' },
      { prop: 'items', label: '检测项目' },
      { prop: 'result', label: '结果' },
      { prop: 'report_url', label: '报告编号' },
    ],
  },
  {
    key: 'processing', label: '加工',
    fields: [
      { prop: 'process_date', label: '日期' },
      { prop: 'process_type', label: '类型' },
      { prop: 'detail', label: '详情' },
      { prop: 'operator', label: '操作人' },
    ],
  },
  {
    key: 'logistics', label: '物流',
    fields: [
      { prop: 'transport_date', label: '日期' },
      { prop: 'from_place', label: '起运地' },
      { prop: 'to_place', label: '目的地' },
      { prop: 'carrier', label: '承运方' },
      { prop: 'temperature', label: '温度' },
    ],
  },
  {
    key: 'sales', label: '销售',
    fields: [
      { prop: 'sale_date', label: '日期' },
      { prop: 'channel', label: '渠道' },
      { prop: 'quantity', label: '数量' },
      { prop: 'price', label: '价格' },
      { prop: 'buyer', label: '买方' },
    ],
  },
]

async function loadBatch() {
  loading.value = true
  try {
    const [b, q] = await Promise.all([batchApi.detail(batchId), batchApi.qrcode(batchId)])
    batch.value = b.data
    qr.value = q.data
    await loadRecords()
  } finally {
    loading.value = false
  }
}

async function loadRecords() {
  const tasks = stageConfig.map((s) => recordApi.list(batchId, s.key))
  const results = await Promise.all(tasks)
  stageConfig.forEach((s, i) => (records[s.key] = results[i].data))
}

function openAdd(stage) {
  currentStage.value = stage
  const form = {}
  stage.fields.forEach((f) => (form[f.prop] = ''))
  recordForm.value = form
  dialogVisible.value = true
}

async function onSaveRecord() {
  const payload = {}
  currentStage.value.fields.forEach((f) => (payload[f.prop] = recordForm.value[f.prop]))
  await recordApi.create(batchId, currentStage.value.key, payload)
  ElMessage.success('已添加')
  dialogVisible.value = false
  loadRecords()
}

function onDeleteRecord(stage, id) {
  ElMessageBox.confirm('确定删除该记录吗？', '提示', { type: 'warning' })
    .then(async () => {
      await recordApi.remove(stage, id)
      ElMessage.success('删除成功')
      loadRecords()
    })
    .catch(() => {})
}

onMounted(loadBatch)
</script>

<style scoped>
.mb { margin-bottom: 16px; }
.batch-head { display: flex; justify-content: space-between; align-items: flex-start; }
.b-title { font-size: 20px; font-weight: 700; margin-bottom: 10px; }
.b-sub { color: #555; margin-bottom: 6px; }
.qr { text-align: center; }
.qr-img { width: 140px; height: 140px; }
.qr-code { font-family: monospace; font-size: 12px; }
</style>
