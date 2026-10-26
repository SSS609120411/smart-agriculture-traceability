<template>
  <div>
    <el-row :gutter="16">
      <el-col :span="6" v-for="s in cards" :key="s.label">
        <el-card shadow="hover">
          <div class="stat"><div class="num">{{ s.value }}</div><div class="label">{{ s.label }}</div></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="mt">
      <el-col :span="8"><el-card header="产品分类分布"><div ref="catRef" class="chart"></div></el-card></el-col>
      <el-col :span="8"><el-card header="批次状态分布"><div ref="statusRef" class="chart"></div></el-card></el-col>
      <el-col :span="8"><el-card header="各环节记录统计"><div ref="stageRef" class="chart"></div></el-card></el-col>
    </el-row>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import * as echarts from 'echarts'
import { dashboardApi } from '../api'

const catRef = ref()
const statusRef = ref()
const stageRef = ref()

const cards = reactive([
  { label: '产品数量', value: 0 },
  { label: '批次数量', value: 0 },
  { label: '分类数量', value: 0 },
  { label: '用户数量', value: 0 },
])

function renderPie(el, data) {
  if (!el) return
  const chart = echarts.init(el)
  chart.setOption({
    tooltip: { trigger: 'item' },
    legend: { bottom: 0 },
    series: [{ type: 'pie', radius: ['40%', '65%'], data, label: { formatter: '{b}: {c}' } }],
  })
}

function renderBar(el, data) {
  if (!el) return
  const chart = echarts.init(el)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: 40, right: 20, top: 20, bottom: 30 },
    xAxis: { type: 'category', data: data.map((i) => i.name) },
    yAxis: { type: 'value', minInterval: 1 },
    series: [{ type: 'bar', data: data.map((i) => i.value), itemStyle: { color: '#67c23a' }, barMaxWidth: 40 }],
  })
}

onMounted(async () => {
  try {
    const res = await dashboardApi.stats()
    const d = res.data
    cards[0].value = d.product_count
    cards[1].value = d.batch_count
    cards[2].value = d.category_count
    cards[3].value = d.user_count
    renderPie(catRef.value, d.category_dist)
    renderPie(statusRef.value, d.status_dist)
    renderBar(stageRef.value, d.stage_stats)
  } catch (e) {}
})
</script>

<style scoped>
.stat { text-align: center; padding: 6px 0; }
.stat .num { font-size: 30px; font-weight: 700; color: #2e7d32; }
.stat .label { color: #666; margin-top: 4px; }
.chart { height: 320px; }
.mt { margin-top: 16px; }
</style>
