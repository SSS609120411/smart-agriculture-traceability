<template>
  <div class="page">
    <el-card class="card">
      <h2 class="title">🌾 智慧农产品溯源管理系统</h2>
      <el-form :model="form" label-position="top">
        <el-form-item label="用户名">
          <el-input v-model="form.username" size="large" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" show-password size="large" placeholder="请输入密码" @keyup.enter="onLogin" />
        </el-form-item>
        <el-button type="primary" size="large" class="w100" :loading="loading" @click="onLogin">登 录</el-button>
        <div class="links">
          <el-link type="primary" @click="$router.push('/register')">注册账号</el-link>
          <el-link type="info" @click="$router.push('/trace')">游客溯源查询</el-link>
        </div>
        <el-divider />
        <div class="tip">演示账号：admin / admin123（管理员）　producer / producer123（生产者）</div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const form = reactive({ username: '', password: '' })
const loading = ref(false)

async function onLogin() {
  if (!form.username || !form.password) return ElMessage.warning('请输入用户名和密码')
  loading.value = true
  try {
    await auth.login(form.username, form.password)
    ElMessage.success('登录成功')
    router.push('/dashboard')
  } catch (e) {
    // 错误提示已由拦截器处理
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.page { min-height: 100vh; display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, #43a047 0%, #1b5e20 100%); }
.card { width: 400px; padding: 8px 12px; }
.title { text-align: center; margin: 8px 0 20px; color: #2e7d32; }
.w100 { width: 100%; }
.links { display: flex; justify-content: space-between; margin-top: 14px; }
.tip { font-size: 12px; color: #999; text-align: center; }
</style>
