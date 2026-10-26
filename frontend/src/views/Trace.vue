<template>
  <div class="trace-page">
    <div class="trace-head">
      <h2>🌾 农产品溯源查询</h2>
      <div class="search">
        <el-input v-model="code" placeholder="请输入溯源码" size="large" clearable @keyup.enter="onSearch" />
        <el-button type="primary" size="large" @click="onSearch">查询</el-button>
      </div>
      <el-link type="primary" @click="$router.push('/login')">返回登录</el-link>
    </div>

    <template v-if="data">
      <el-card class="mt">
        <div class="product-head">
          <div>
            <div class="p-name">{{ data.product?.name }}</div>
            <div class="p-sub">分类：{{ data.category?.name }}　产地：{{ data.product?.origin }}　品种：{{ data.product?.variety }}</div>
            <div class="p-sub">生产日期：{{ data.batch?.production_date }}　数量：{{ data.batch?.quantity }}{{ data.batch?.unit }}</div>
            <div class="p-sub">生产单位：{{ data.producer?.name }}（{{ data.producer?.phone }}）</div>
          </div>
          <el-tag type="success" size="large">状态：{{ data.batch?.status }}</el-tag>
        </div>
      </el-card>

      <el-card class="mt">
        <template #header>溯源链条</template>
        <el-timeline v-if="data.timeline.length">
          <el-timeline-item
            v-for="(t, i) in data.timeline"
            :key="i"
            :timestamp="`${t.stage} · ${t.time}`"
            :type="i === 0 ? 'primary' : 'success'"
            placement="top"
          >
            <div class="t-title">{{ t.title }}</div>
            <div class="t-detail">{{ t.detail }}</div>
            <div v-if="Object.keys(t.extra).length" class="t-extra">
              <el-tag v-for="(v, k) in t.extra" :key="k" size="small" class="mr">{{ k }}：{{ v }}</el-tag>
            </div>
          </el-timeline-item>
        </el-timeline>
        <el-empty v-else description="暂无环节记录" />
      </el-card>
    </template>

    <el-empty v-else-if="searched" description="未查询到该溯源码对应的批次" class="mt" />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { traceApi } from '../api'

const route = useRoute()
const code = ref('')
const data = ref(null)
const searched = ref(false)

async function onSearch() {
  if (!code.value.trim()) return
  searched.value = false
  data.value = null
  try {
    const res = await traceApi.get(code.value.trim())
    data.value = res.data
  } catch (e) {
    // 未找到等错误已提示
  } finally {
    searched.value = true
  }
}

onMounted(() => {
  if (route.params.code) {
    code.value = route.params.code
    onSearch()
  }
})
</script>

<style scoped>
.trace-page { max-width: 860px; margin: 0 auto; padding: 32px 16px; }
.trace-head { text-align: center; }
.trace-head h2 { color: #2e7d32; margin-bottom: 16px; }
.search { display: flex; gap: 12px; max-width: 560px; margin: 0 auto 12px; }
.mt { margin-top: 16px; }
.product-head { display: flex; justify-content: space-between; align-items: flex-start; }
.p-name { font-size: 22px; font-weight: 700; margin-bottom: 8px; }
.p-sub { color: #555; margin-bottom: 4px; }
.t-title { font-weight: 600; }
.t-detail { color: #555; margin: 4px 0; }
.t-extra { margin-top: 6px; }
.mr { margin-right: 6px; }
</style>
