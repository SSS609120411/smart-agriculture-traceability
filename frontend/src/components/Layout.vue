<template>
  <el-container class="layout">
    <el-aside width="220px" class="aside">
      <div class="logo">🌾 智慧农产品溯源</div>
      <el-menu
        :default-active="activeMenu"
        router
        background-color="#001529"
        text-color="#c0c4cc"
        active-text-color="#ffffff"
      >
        <el-menu-item index="/dashboard"><el-icon><DataLine /></el-icon><span>数据看板</span></el-menu-item>
        <el-menu-item v-if="isAdmin" index="/categories"><el-icon><Collection /></el-icon><span>产品分类</span></el-menu-item>
        <el-menu-item index="/products"><el-icon><Apple /></el-icon><span>产品管理</span></el-menu-item>
        <el-menu-item index="/batches"><el-icon><Box /></el-icon><span>批次管理</span></el-menu-item>
        <el-menu-item v-if="isAdmin" index="/users"><el-icon><User /></el-icon><span>用户管理</span></el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="title">{{ $route.meta.title || '' }}</div>
        <div class="right">
          <el-button link type="primary" @click="$router.push('/trace')">溯源查询</el-button>
          <el-tag size="small" type="success">{{ roleText }}</el-tag>
          <span class="uname">{{ auth.user?.name || auth.user?.username }}</span>
          <el-button type="danger" size="small" @click="onLogout">退出</el-button>
        </div>
      </el-header>
      <el-main class="main"><router-view /></el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const isAdmin = computed(() => auth.role === 'admin')
const roleText = computed(() => ({ admin: '管理员', producer: '生产者', consumer: '消费者' }[auth.role] || ''))
const activeMenu = computed(() => (route.path.startsWith('/batches') ? '/batches' : route.path))

function onLogout() {
  ElMessageBox.confirm('确定退出登录吗？', '提示', { type: 'warning' })
    .then(() => {
      auth.logout()
      router.push('/login')
    })
    .catch(() => {})
}
</script>

<style scoped>
.layout { height: 100vh; }
.aside { background: #001529; }
.logo { height: 56px; line-height: 56px; text-align: center; color: #fff; font-size: 17px; font-weight: 600; }
.aside :deep(.el-menu) { border-right: none; }
.header { display: flex; align-items: center; justify-content: space-between; background: #fff; border-bottom: 1px solid #eee; }
.header .title { font-size: 18px; font-weight: 600; }
.header .right { display: flex; align-items: center; gap: 12px; }
.uname { color: #333; }
.main { background: #f5f7fa; }
</style>
